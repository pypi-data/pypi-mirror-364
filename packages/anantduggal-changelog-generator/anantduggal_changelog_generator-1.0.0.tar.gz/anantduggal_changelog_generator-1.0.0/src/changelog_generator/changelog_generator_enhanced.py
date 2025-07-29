#!/usr/bin/env python3
"""
Enhanced Git Changelog Generator CLI

A high-performance command-line tool that generates AI-powered changelogs from git commit history
using the Claude API. Combines full CLI functionality with memory optimizations and async processing.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import gc
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from urllib.parse import urlparse
from contextlib import asynccontextmanager

import aiohttp
import aiofiles
import redis.asyncio as redis
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

# API Configuration
DEFAULT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFkdWdnYWxAdXdhdGVybG9vLmNhIiwiYXNzZXNzbWVudCI6ImFpIiwiY3JlYXRlZF9hdCI6IjIwMjUtMDctMjNUMDU6MDU6MjkuNTEzMDg0MDYyWiIsImlhdCI6MTc1MzI0NzEyOX0.pu-ZZcLNOUWbsSBtusmV8qDwQ3oelMqBG9sAtTsfwEs"
DEFAULT_BASE_URL = "https://mintlify-take-home.com"
DEFAULT_API_ENDPOINT = "/api/message"

# GitHub API Configuration
GITHUB_API_BASE = "https://api.github.com"

# Memory optimization settings
MICRO_CHUNK_SIZE = 10  # Process commits in small chunks
GC_FREQUENCY = 10      # Force garbage collection frequency
MAX_CACHED_COMMITS_PER_REPO = 1000  # Limit cache size per repo

# GitHub API rate limits
GITHUB_AUTHENTICATED_RATE_LIMIT = 5000  # 5000 requests per hour with token
GITHUB_UNAUTHENTICATED_RATE_LIMIT = 60  # 60 requests per hour without token

# Initialize rich console for beautiful output
console = Console()

# Global session for HTTP connections
http_session: Optional[aiohttp.ClientSession] = None


class EnhancedConfig:
    """Enhanced configuration management combining original and ultra-optimized features."""
    
    def __init__(self):
        self.config_file = Path.home() / ".changelog_generator.yaml"
        self.config = self._load_config()
        self._github_token = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
        
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value and save to file."""
        self.config[key] = value
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not save config: {e}[/yellow]")

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration with defaults."""
        return self.config.get('cache', {
            'enabled': True,
            'max_cached_repos': 50,
            'repo_metadata_ttl': 86400,  # 24 hours
            'commit_data_ttl': 3600,     # 1 hour
            'smart_caching': {
                'enabled': True,
                'sha_check_frequency': 300,  # 5 minutes
                'max_commit_cache_per_repo': 1000,
                'background_updates': True
            }
        })

    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration with defaults."""
        return self.config.get('redis', {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5
        })

    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from config or environment."""
        if self._github_token is not None:
            return self._github_token
        
        # Try config file first
        self._github_token = self.get('github.token')
        
        # Try environment variables
        if not self._github_token:
            self._github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        
        return self._github_token
    
    def has_github_token(self) -> bool:
        """Check if GitHub token is available."""
        return self.get_github_token() is not None

    def is_smart_caching_enabled(self) -> bool:
        """Check if smart caching is enabled."""
        return self.get_cache_config().get('smart_caching', {}).get('enabled', True)


class MemoryOptimizedRateLimiter:
    """Memory-optimized rate limiter with GitHub-specific logic."""
    
    _token_message_printed = False  # Class-level flag to print message only once
    
    def __init__(self, config: EnhancedConfig):
        self.config = config
        self.has_token = config.has_github_token()
        self.requests_per_hour = GITHUB_AUTHENTICATED_RATE_LIMIT if self.has_token else GITHUB_UNAUTHENTICATED_RATE_LIMIT
        self.requests_made = 0
        self.reset_time = datetime.now()
        self._lock = asyncio.Lock()
        
        # Be more conservative with rate limiting
        self.safety_margin = 0.8  # Use 80% of the rate limit
        self.effective_limit = int(self.requests_per_hour * self.safety_margin)
        
        # Only print the GitHub token message once
        if not MemoryOptimizedRateLimiter._token_message_printed:
            if self.has_token:
                console.print(f"[green]GitHub token found - using authenticated rate limit: {self.effective_limit} requests/hour[/green]")
            else:
                console.print(f"[yellow]No GitHub token - using unauthenticated rate limit: {self.effective_limit} requests/hour[/yellow]")
                console.print("[yellow]Set GITHUB_TOKEN environment variable for higher limits[/yellow]")
            MemoryOptimizedRateLimiter._token_message_printed = True
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        async with self._lock:
            now = datetime.now()
            
            if now - self.reset_time > timedelta(hours=1):
                self.requests_made = 0
                self.reset_time = now
            
            if self.requests_made >= self.effective_limit:
                wait_time = 3600 - (now - self.reset_time).total_seconds()
                if wait_time > 0:
                    console.print(f"[yellow]Rate limit reached. Waiting {wait_time:.0f} seconds...[/yellow]")
                    await asyncio.sleep(wait_time)
                    self.requests_made = 0
                    self.reset_time = datetime.now()
            
            self.requests_made += 1
    
    async def handle_rate_limit_response(self, response: aiohttp.ClientResponse) -> bool:
        """Handle rate limit response headers and wait if needed. Returns True if should retry."""
        if response.status == 403:
            # Check if it's a rate limit error
            error_data = None
            try:
                error_data = await response.json()
            except:
                pass
            
            if error_data and 'rate limit' in error_data.get('message', '').lower():
                console.print("[yellow]GitHub rate limit exceeded![/yellow]")
                
                # Check for reset time in headers
                reset_header = response.headers.get('X-RateLimit-Reset')
                if reset_header:
                    reset_time = datetime.fromtimestamp(int(reset_header))
                    wait_time = (reset_time - datetime.now()).total_seconds()
                    if wait_time > 0:
                        console.print(f"[yellow]Waiting {wait_time:.0f} seconds for rate limit reset...[/yellow]")
                        await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
                        return True
                else:
                    # Default wait time
                    console.print("[yellow]Waiting 60 seconds before retry...[/yellow]")
                    await asyncio.sleep(60)
                    return True
        
        return False


class EnhancedCacheManager:
    """Enhanced cache manager combining original functionality with ultra-optimized features."""

    def __init__(self, config: EnhancedConfig):
        self.config = config
        self.cache_config = config.get_cache_config()
        self.redis_config = config.get_redis_config()
        self._redis_pool = None
        self._connection_pool_size = 10

    async def get_redis_pool(self) -> Optional[redis.ConnectionPool]:
        """Get Redis connection pool with lazy initialization."""
        if not self.cache_config.get('enabled', True):
            return None

        if self._redis_pool is None:
            try:
                self._redis_pool = redis.ConnectionPool(
                    **self.redis_config,
                    max_connections=self._connection_pool_size,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                async with redis.Redis(connection_pool=self._redis_pool) as redis_client:
                    await redis_client.ping()
            except Exception as e:
                console.print(f"[yellow]Warning: Could not connect to Redis: {e}[/yellow]")
                console.print("[yellow]Cache functionality will be disabled[/yellow]")
                return None

        return self._redis_pool

    async def is_cache_enabled(self) -> bool:
        """Check if cache is enabled and available."""
        return await self.get_redis_pool() is not None

    async def get_cached_repos(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Get list of cached repositories for a user."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return []

        try:
            key = f"repos:{user_id}:list"
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                repo_data = await redis_client.lrange(key, 0, -1)
                repos = []

                for repo_json in repo_data:
                    try:
                        repo_info = json.loads(repo_json)
                        # Always include the repo, metadata is optional enhancement
                        metadata = await self.get_repo_metadata(repo_info['owner'], repo_info['repo'])
                        if metadata:
                            repo_info.update(metadata)
                        repos.append(repo_info)
                    except (json.JSONDecodeError, KeyError):
                        continue

                return repos
        except Exception as e:
            console.print(f"[yellow]Warning: Error retrieving cached repos: {e}[/yellow]")
            return []

    async def add_repo_to_cache(self, owner: str, repo: str, user_id: str = "default") -> bool:
        """Add a repository to the user's cache."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return False

        try:
            repo_info = {
                'owner': owner,
                'repo': repo,
                'last_accessed': datetime.now().isoformat(),
                'full_name': f"{owner}/{repo}"
            }

            # Add to user's repo list (keep only recent ones)
            key = f"repos:{user_id}:list"
            repo_json = json.dumps(repo_info)

            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                # Remove if already exists
                await redis_client.lrem(key, 0, repo_json)
                # Add to front
                await redis_client.lpush(key, repo_json)
                # Keep only max_cached_repos
                max_repos = self.cache_config.get('max_cached_repos', 50)
                await redis_client.ltrim(key, 0, max_repos - 1)

            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error adding repo to cache: {e}[/yellow]")
            return False

    async def get_repo_metadata(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get cached repository metadata."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return None

        try:
            key = f"repo:{owner}:{repo}:metadata"
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                metadata_json = await redis_client.get(key)

                if metadata_json:
                    metadata = json.loads(metadata_json)
                    # Check if still valid
                    cached_time = datetime.fromisoformat(metadata['cached_at'])
                    ttl = self.cache_config.get('repo_metadata_ttl', 86400)

                    if datetime.now() - cached_time < timedelta(seconds=ttl):
                        return metadata
                    else:
                        # Expired, remove it
                        await redis_client.delete(key)

                return None
        except Exception as e:
            console.print(f"[yellow]Warning: Error retrieving repo metadata: {e}[/yellow]")
            return None

    async def cache_repo_metadata(self, owner: str, repo: str, metadata: Dict[str, Any]) -> bool:
        """Cache repository metadata."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return False

        try:
            key = f"repo:{owner}:{repo}:metadata"
            metadata['cached_at'] = datetime.now().isoformat()

            ttl = self.cache_config.get('repo_metadata_ttl', 86400)
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                await redis_client.setex(key, ttl, json.dumps(metadata))

            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error caching repo metadata: {e}[/yellow]")
            return False

    async def get_cached_commits(self, owner: str, repo: str, num_commits: int) -> Optional[List[Dict[str, str]]]:
        """Get cached commits for a repository."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return None

        try:
            key = f"repo:{owner}:{repo}:commits"
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                commit_data = await redis_client.get(key)

                if commit_data:
                    cached_info = json.loads(commit_data)
                    cached_time = datetime.fromisoformat(cached_info['cached_at'])
                    ttl = self.cache_config.get('commit_data_ttl', 3600)

                    if datetime.now() - cached_time < timedelta(seconds=ttl):
                        commits = cached_info['commits']
                        # Return requested number of commits
                        return commits[:num_commits] if len(commits) >= num_commits else commits
                    else:
                        # Expired, remove it
                        await redis_client.delete(key)

                return None
        except Exception as e:
            console.print(f"[yellow]Warning: Error retrieving cached commits: {e}[/yellow]")
            return None

    async def cache_commits(self, owner: str, repo: str, commits: List[Dict[str, str]]) -> bool:
        """Cache commits for a repository."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return False

        try:
            key = f"repo:{owner}:{repo}:commits"
            commit_data = {
                'commits': commits,
                'cached_at': datetime.now().isoformat(),
                'total_commits': len(commits)
            }

            ttl = self.cache_config.get('commit_data_ttl', 3600)
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                await redis_client.setex(key, ttl, json.dumps(commit_data))

            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error caching commits: {e}[/yellow]")
            return False

    async def clear_cache(self, pattern: str = "*") -> bool:
        """Clear cache entries matching pattern."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return False

        try:
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
                    console.print(f"[green]Cleared {len(keys)} cache entries[/green]")
                else:
                    console.print("[yellow]No cache entries found to clear[/yellow]")
            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error clearing cache: {e}[/yellow]")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return {'enabled': False}

        try:
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                info = await redis_client.info()
                keys = await redis_client.keys("*")

                stats = {
                    'enabled': True,
                    'total_keys': len(keys),
                    'memory_used': info.get('used_memory_human', 'Unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'redis_version': info.get('redis_version', 'Unknown')
                }

                # Count different types of keys
                repo_keys = len([k for k in keys if k.decode().startswith('repo:')])
                user_keys = len([k for k in keys if k.decode().startswith('repos:')])

                stats.update({
                    'repo_cache_entries': repo_keys,
                    'user_cache_entries': user_keys
                })

                return stats
        except Exception as e:
            console.print(f"[yellow]Warning: Error getting cache stats: {e}[/yellow]")
            return {'enabled': False, 'error': str(e)}


class SmartCacheManager(EnhancedCacheManager):
    """Smart cache manager with SHA-based caching and enhanced repository management."""

    def __init__(self, config: EnhancedConfig, rate_limiter: Optional[MemoryOptimizedRateLimiter] = None):
        super().__init__(config)
        self.smart_config = config.get_cache_config().get('smart_caching', {})
        self.rate_limiter = rate_limiter or MemoryOptimizedRateLimiter(config)

    async def get_latest_commit_sha(self, owner: str, repo: str, branch: str = 'main') -> Optional[str]:
        """Get the latest commit SHA from GitHub API (lightweight call)."""
        if not await self.is_cache_enabled():
            return None

        try:
            session = await get_enhanced_http_session(self.config)
            
            await self.rate_limiter.wait_if_needed()
            
            api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
            params = {'per_page': 1, 'sha': branch}
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    commit_data = await response.json()
                    if commit_data:
                        return commit_data[0]['sha']
                return None
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch latest SHA for {owner}/{repo}: {e}[/yellow]")
            return None

    async def get_cached_latest_sha(self, owner: str, repo: str) -> Optional[str]:
        """Get the cached latest commit SHA."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return None

        try:
            key = f"repo:{owner}:{repo}:latest_sha"
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                return await redis_client.get(key)
        except Exception as e:
            console.print(f"[yellow]Warning: Error retrieving cached SHA: {e}[/yellow]")
            return None

    async def cache_latest_sha(self, owner: str, repo: str, sha: str, branch: str = 'main') -> bool:
        """Cache the latest commit SHA."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return False

        try:
            key = f"repo:{owner}:{repo}:latest_sha"
            sha_data = {
                'sha': sha,
                'branch': branch,
                'cached_at': datetime.now().isoformat()
            }
            
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                await redis_client.setex(key, 86400, json.dumps(sha_data))  # 24 hour TTL
            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error caching SHA: {e}[/yellow]")
            return False

    async def detect_new_commits(self, owner: str, repo: str, branch: str = 'main') -> Tuple[bool, int]:
        """
        Detect if new commits are available using Git-style ahead/behind logic.
        
        Returns:
            Tuple of (has_new_commits, estimated_new_count)
        """
        if not self.smart_config.get('enabled', True):
            return False, 0

        try:
            # Get current latest SHA from GitHub
            current_sha = await self.get_latest_commit_sha(owner, repo, branch)
            if not current_sha:
                return False, 0

            # Get cached latest SHA
            cached_sha_data = await self.get_cached_latest_sha(owner, repo)
            
            if not cached_sha_data:
                # No cached SHA, cache current SHA and consider it current (not new)
                await self.cache_latest_sha(owner, repo, current_sha, branch)
                return False, 0  # First time caching, consider it current
            
            try:
                # Handle both string and JSON formats for cached SHA
                if isinstance(cached_sha_data, str):
                    try:
                        cached_data = json.loads(cached_sha_data)
                        cached_sha_value = cached_data.get('sha')
                    except json.JSONDecodeError:
                        # If it's just a plain string SHA
                        cached_sha_value = cached_sha_data
                elif isinstance(cached_sha_data, bytes):
                    # Handle bytes format (Redis sometimes returns bytes)
                    try:
                        # Try to decode as JSON first
                        decoded = cached_sha_data.decode('utf-8')
                        try:
                            cached_data = json.loads(decoded)
                            cached_sha_value = cached_data.get('sha')
                        except json.JSONDecodeError:
                            # If not JSON, treat as plain string
                            cached_sha_value = decoded
                    except UnicodeDecodeError:
                        # If can't decode, treat as plain string
                        cached_sha_value = str(cached_sha_data)
                else:
                    cached_sha_value = str(cached_sha_data)
                
                # Ensure we have a valid cached SHA
                if not cached_sha_value:
                    await self.cache_latest_sha(owner, repo, current_sha, branch)
                    return False, 0
                    
            except Exception as e:
                # If any parsing error, cache current SHA and treat as current
                await self.cache_latest_sha(owner, repo, current_sha, branch)
                return False, 0

            # Compare SHAs (make sure both are strings)
            current_sha_str = str(current_sha)
            cached_sha_str = str(cached_sha_value)
            
            if current_sha_str != cached_sha_str:
                # SHAs are different, check if current is ahead of cached
                if len(cached_sha_str) >= 7 and len(current_sha_str) >= 7:  # Valid SHA length check
                    estimated_count = await self._estimate_new_commit_count(owner, repo, cached_sha_str, current_sha_str)
                    
                    if estimated_count > 0:
                        # Current SHA is ahead of cached SHA - we have new commits
                        await self.cache_latest_sha(owner, repo, current_sha, branch)
                        return True, estimated_count
                    else:
                        # Current SHA is behind or same as cached SHA - no new commits
                        # Update cached SHA to current for future reference
                        await self.cache_latest_sha(owner, repo, current_sha, branch)
                        return False, 0
                else:
                    # Invalid SHA format, update cache and treat as current
                    await self.cache_latest_sha(owner, repo, current_sha, branch)
                    return False, 0
            
            # SHAs match - no new commits
            return False, 0

        except Exception as e:
            console.print(f"[dim]Error detecting new commits for {owner}/{repo}: {e}[/dim]")
            # On error, cache current state and report no changes to avoid spam
            try:
                current_sha = await self.get_latest_commit_sha(owner, repo, branch)
                if current_sha:
                    await self.cache_latest_sha(owner, repo, current_sha, branch)
            except:
                pass
            return False, 0

    async def _estimate_new_commit_count(self, owner: str, repo: str, old_sha: str, new_sha: str) -> int:
        """
        Estimate number of new commits using Git-style ahead/behind logic.
        Only considers commits as 'new' if the current SHA is ahead of the cached SHA.
        """
        try:
            # Validate SHAs
            if not old_sha or not new_sha or old_sha == new_sha:
                return 0
            
            # Ensure SHAs are at least 7 characters (typical short SHA length)
            if len(old_sha) < 7 or len(new_sha) < 7:
                return 0
            
            session = await get_enhanced_http_session(self.config)
            
            await self.rate_limiter.wait_if_needed()
            
            # Use GitHub's compare API to get ahead/behind information
            api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/compare/{old_sha}...{new_sha}"
            
            async with session.get(api_url) as response:
                if response.status == 200:
                    compare_data = await response.json()
                    
                    # Check if current SHA is ahead of cached SHA
                    ahead_by = compare_data.get('ahead_by', 0)
                    behind_by = compare_data.get('behind_by', 0)
                    
                    # Only consider it as having new commits if we're ahead
                    if ahead_by > 0:
                        return ahead_by
                    elif behind_by > 0:
                        # We're behind - this could happen if there was a force push or branch change
                        return 0
                    else:
                        # Same commit or no difference
                        return 0
                        
                elif response.status == 404:
                    # One of the SHAs doesn't exist anymore (force push, etc.)
                    return 0
                else:
                    return 0
        except Exception:
            # Silently fail to avoid spam - this is just for estimation
            return 0

    async def get_enhanced_repo_metadata(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get enhanced repository metadata with usage statistics and update status."""
        basic_metadata = await self.get_repo_metadata(owner, repo)
        if not basic_metadata:
            basic_metadata = {}

        # Check for updates
        has_new_commits, new_count = await self.detect_new_commits(owner, repo)
        
        # Get usage statistics
        usage_stats = await self.get_repo_usage_stats(owner, repo)
        
        enhanced_metadata = {
            **basic_metadata,
            'has_new_commits': has_new_commits,
            'estimated_new_count': new_count,
            'usage_count': usage_stats.get('usage_count', 0),
            'last_accessed': usage_stats.get('last_accessed'),
            'access_frequency': usage_stats.get('access_frequency', 0.0)
        }
        
        return enhanced_metadata

    async def get_repo_usage_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository usage statistics."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return {}

        try:
            key = f"repo:{owner}:{repo}:usage_stats"
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                stats_data = await redis_client.get(key)
                if stats_data:
                    return json.loads(stats_data)
                return {}
        except Exception as e:
            console.print(f"[yellow]Warning: Error retrieving usage stats: {e}[/yellow]")
            return {}

    async def update_repo_usage_stats(self, owner: str, repo: str) -> bool:
        """Update repository usage statistics."""
        redis_pool = await self.get_redis_pool()
        if not redis_pool:
            return False

        try:
            key = f"repo:{owner}:{repo}:usage_stats"
            async with redis.Redis(connection_pool=redis_pool) as redis_client:
                # Get current stats
                current_stats = await self.get_repo_usage_stats(owner, repo)
                
                # Calculate new stats
                now = datetime.now()
                usage_count = current_stats.get('usage_count', 0) + 1
                last_accessed = now.isoformat()
                
                # Calculate access frequency (accesses per day)
                first_access = current_stats.get('first_accessed')
                if not first_access:
                    first_access = last_accessed
                    access_frequency = 1.0
                else:
                    try:
                        first_dt = datetime.fromisoformat(first_access.replace('Z', '+00:00'))
                        days_since_first = max(1, (now - first_dt).days)
                        access_frequency = usage_count / days_since_first
                    except:
                        access_frequency = 1.0

                new_stats = {
                    'usage_count': usage_count,
                    'last_accessed': last_accessed,
                    'first_accessed': first_access,
                    'access_frequency': access_frequency,
                    'updated_at': last_accessed
                }
                
                await redis_client.setex(key, 86400 * 30, json.dumps(new_stats))  # 30 day TTL
                return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error updating usage stats: {e}[/yellow]")
            return False

    async def get_smart_cached_repos(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Get enhanced list of cached repositories with smart metadata."""
        basic_repos = await self.get_cached_repos(user_id)
        enhanced_repos = []

        for repo in basic_repos:
            try:
                enhanced_metadata = await self.get_enhanced_repo_metadata(repo['owner'], repo['repo'])
                if enhanced_metadata:
                    repo_data = {
                        **repo,
                        **enhanced_metadata
                    }
                    enhanced_repos.append(repo_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Error enhancing repo {repo.get('full_name', 'unknown')}: {e}[/yellow]")
                enhanced_repos.append(repo)  # Fallback to basic data

        # Sort by smart priority (frequency * recency with updates boost)
        def calculate_priority(repo_data):
            base_score = repo_data.get('access_frequency', 0.1)
            
            # Boost for recent access
            last_accessed = repo_data.get('last_accessed')
            if last_accessed:
                try:
                    last_dt = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                    hours_ago = (datetime.now() - last_dt).total_seconds() / 3600
                    recency_boost = max(0.1, 1.0 / (1 + hours_ago / 24))  # Decay over days
                    base_score *= recency_boost
                except:
                    pass
            
            # Major boost for repositories with new commits
            if repo_data.get('has_new_commits'):
                base_score *= 2.0
            
            return base_score

        enhanced_repos.sort(key=calculate_priority, reverse=True)
        return enhanced_repos

    async def suggest_cache_refresh(self, owner: str, repo: str, num_commits: int) -> Tuple[Optional[List[Dict[str, str]]], bool]:
        """
        Smart cache refresh suggestion based on Git-style ahead/behind detection.
        
        Returns:
            Tuple of (cached_commits, should_refresh)
        """
        # First check if we have cached commits
        cached_commits = await self.get_cached_commits(owner, repo, num_commits)
        
        # Check for new commits using Git-style ahead/behind detection
        has_new_commits, new_count = await self.detect_new_commits(owner, repo)
        
        if not cached_commits:
            console.print(f"\n[yellow]No cached commits found for {owner}/{repo}[/yellow]")
            return None, True
        
        if has_new_commits and new_count > 0:
            console.print(f"\n[bold yellow]📬 {new_count} new commits detected for {owner}/{repo}[/bold yellow]")
            console.print(f"[dim]Repository is {new_count} commits ahead of cached state[/dim]")
            if Confirm.ask("Fetch the latest commits?", default=True):
                return cached_commits, True
            else:
                console.print("[dim]Using cached commits (may be outdated)[/dim]")
                return cached_commits, False
        elif has_new_commits and new_count == 0:
            # This shouldn't happen with proper ahead/behind logic, but handle gracefully
            console.print(f"\n[yellow]⚡ Repository state changed for {owner}/{repo}[/yellow]")
            console.print("[dim]This could indicate branch changes or force pushes[/dim]")
            if Confirm.ask("Fetch fresh data to be safe?", default=False):
                return cached_commits, True
            else:
                return cached_commits, False
        else:
            console.print(f"\n[green]✓ {owner}/{repo} is up to date (cached commits available)[/green]")
            console.print(f"[dim]Repository head matches cached state[/dim]")
            # For current repos, we can offer the option but default to using cache
            if len(cached_commits) < num_commits:
                console.print(f"[dim]Note: You requested {num_commits} commits but only have {len(cached_commits)} cached[/dim]")
                if Confirm.ask("Fetch more commits?", default=True):
                    return cached_commits, True
            
            if Confirm.ask("Use cached commits?", default=True):
                return cached_commits, False
            else:
                return cached_commits, True


async def get_enhanced_http_session(config: EnhancedConfig) -> aiohttp.ClientSession:
    """Get or create global HTTP session optimized for memory efficiency with GitHub auth."""
    global http_session
    if http_session is None or http_session.closed:
        headers = {'User-Agent': 'ChangelogGenerator/Enhanced'}
        
        # Add GitHub authentication if token is available
        github_token = config.get_github_token()
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            headers['Accept'] = 'application/vnd.github.v3+json'
        
        connector = aiohttp.TCPConnector(
            limit=20,  # Connection pool size
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
    return http_session


async def cleanup_global_session():
    """Cleanup global HTTP session."""
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()


async def display_cached_repos_async(cache_manager: EnhancedCacheManager, user_id: str = "default") -> Optional[str]:
    """Display cached repositories and allow user to select one (async version)."""
    # Use SmartCacheManager if available and enabled
    if isinstance(cache_manager, SmartCacheManager):
        cached_repos = await cache_manager.get_smart_cached_repos(user_id)
    elif cache_manager.config.is_smart_caching_enabled():
        # Create a minimal rate limiter for this operation (won't print duplicate messages)
        temp_rate_limiter = MemoryOptimizedRateLimiter(cache_manager.config)
        smart_cache = SmartCacheManager(cache_manager.config, temp_rate_limiter)
        cached_repos = await smart_cache.get_smart_cached_repos(user_id)
    else:
        cached_repos = await cache_manager.get_cached_repos(user_id)

    if not cached_repos:
        console.print("[yellow]No cached repositories found.[/yellow]")
        return None

    console.print("\n[bold blue]Recently used repositories:[/bold blue]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Repository", style="green", width=30)
    table.add_column("Status", style="white", width=20)
    table.add_column("Last Accessed", style="yellow", width=20)
    table.add_column("Usage", style="blue", width=10)

    for i, repo in enumerate(cached_repos, 1):
        last_accessed = repo.get('last_accessed', 'Unknown')
        if last_accessed != 'Unknown':
            try:
                dt = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                last_accessed = dt.strftime('%m-%d %H:%M')
            except:
                pass

        # Determine status with smart indicators
        status_parts = []
        
        # Check if we have cached commits
        cached_commits = await cache_manager.get_cached_commits(repo['owner'], repo['repo'], 1)
        has_cache = cached_commits is not None
        
        # Check for updates (smart caching)
        has_new_commits = repo.get('has_new_commits', False)
        estimated_new_count = repo.get('estimated_new_count', 0)
        
        if has_new_commits and estimated_new_count > 0:
            status_parts.append(f"[bold yellow]📬 {estimated_new_count} new[/bold yellow]")
        elif has_new_commits:
            status_parts.append("[yellow]⚡ Updates[/yellow]")
        elif has_cache:
            status_parts.append("[green]✓ Current[/green]")
        else:
            status_parts.append("[dim]No cache[/dim]")
        
        if has_cache:
            status_parts.append("[dim]Cached[/dim]")
        
        status = " • ".join(status_parts)
        
        # Usage information
        usage_count = repo.get('usage_count', 0)
        access_frequency = repo.get('access_frequency', 0.0)
        if usage_count > 0:
            usage_info = f"{usage_count}x"
            if access_frequency > 1:
                usage_info += f" ({access_frequency:.1f}/d)"
        else:
            usage_info = "New"

        table.add_row(
            str(i),
            repo['full_name'],
            status,
            last_accessed,
            usage_info
        )

    console.print(table)
    
    # Show legend for status indicators
    console.print("\n[dim]Status: ✓ Current • ⚡ Updates available • 📬 New commits detected • Cached = Has local cache[/dim]")
    console.print()

    # Get user selection
    while True:
        choice = Prompt.ask(
            "Select a repository by number, enter 'new' for a new repo, or 'skip' to continue",
            default="skip"
        )

        if choice.lower() == 'skip':
            return None
        elif choice.lower() == 'new':
            return 'new'
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(cached_repos):
                    selected_repo = cached_repos[index]
                    
                    # Update usage stats when repo is selected
                    if isinstance(cache_manager, SmartCacheManager):
                        await cache_manager.update_repo_usage_stats(selected_repo['owner'], selected_repo['repo'])
                    elif cache_manager.config.is_smart_caching_enabled():
                        # Reuse the temp_rate_limiter we created earlier
                        await smart_cache.update_repo_usage_stats(selected_repo['owner'], selected_repo['repo'])
                    
                    return f"{selected_repo['owner']}/{selected_repo['repo']}"
                else:
                    console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number, 'new', or 'skip'.[/red]")


async def check_cached_commits_freshness(cache_manager: EnhancedCacheManager, owner: str, repo: str, num_commits: int) -> Tuple[Optional[List[Dict[str, str]]], bool]:
    """
    Check if cached commits exist and if they should be refreshed.

    Returns:
        Tuple of (cached_commits, should_refresh)
    """
    # Use smart caching if available and enabled
    if isinstance(cache_manager, SmartCacheManager):
        return await cache_manager.suggest_cache_refresh(owner, repo, num_commits)
    elif cache_manager.config.is_smart_caching_enabled():
        # Create a minimal rate limiter for this operation
        temp_rate_limiter = MemoryOptimizedRateLimiter(cache_manager.config)
        smart_cache = SmartCacheManager(cache_manager.config, temp_rate_limiter)
        return await smart_cache.suggest_cache_refresh(owner, repo, num_commits)
    
    # Fallback to legacy time-based caching
    cached_commits = await cache_manager.get_cached_commits(owner, repo, num_commits)

    if not cached_commits:
        return None, True

    # Check cache age - get metadata to determine age
    metadata = await cache_manager.get_repo_metadata(owner, repo)
    if metadata and 'cached_at' in metadata:
        try:
            cached_time = datetime.fromisoformat(metadata['cached_at'])
            age_minutes = (datetime.now() - cached_time).total_seconds() / 60

            console.print(f"\n[yellow]Found cached commits from {age_minutes:.1f} minutes ago[/yellow]")

            if age_minutes > 30:  # Suggest refresh if older than 30 minutes
                if Confirm.ask("Commits are a bit old. Fetch fresh data?", default=True):
                    return cached_commits, True
            else:
                if Confirm.ask("Use cached commits?", default=True):
                    return cached_commits, False
                else:
                    return cached_commits, True
        except Exception:
            pass

    return cached_commits, False


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AI-powered changelogs from git commit history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python changelog_generator_enhanced.py 10                    # Generate changelog for last 10 commits
  python changelog_generator_enhanced.py 5 --interactive       # Interactive mode with preview
  python changelog_generator_enhanced.py 20 --output file.md   # Save to file
  python changelog_generator_enhanced.py 15 --format json      # Output as JSON
  python changelog_generator_enhanced.py 10 --config           # Show current configuration
  python changelog_generator_enhanced.py 10 --cache-stats      # Show cache statistics
  python changelog_generator_enhanced.py 10 --list-repos       # List cached repositories
  python changelog_generator_enhanced.py 10 --smart-cache      # Force smart SHA-based caching

Smart Caching Features:
  • SHA-based update detection - Precise detection of new commits
  • Repository usage tracking - Smart prioritization of frequently used repos
  • Enhanced repository backlog - Shows update status and usage statistics
  • Intelligent cache refresh - Only fetches new commits when needed

Environment Variables:
  GITHUB_TOKEN     GitHub personal access token for authenticated requests
  GH_TOKEN         Alternative name for GitHub token
        """
    )
    
    parser.add_argument(
        "num_commits",
        type=int,
        help="Number of recent commits to include in the changelog"
    )
    
    parser.add_argument(
        "--repo", "-r",
        type=str,
        help="GitHub repository URL or owner/repo (e.g., 'owner/repo' or 'https://github.com/owner/repo')"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode: preview commits before processing"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (supports .md, .txt, .json)"
    )
    
    parser.add_argument(
        "--format",
        choices=["markdown", "text", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="Override API key"
    )
    
    parser.add_argument(
        "--api-url",
        type=str,
        help="Override API base URL"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching of results"
    )

    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics"
    )

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached data"
    )

    parser.add_argument(
        "--list-repos",
        action="store_true",
        help="List cached repositories"
    )

    parser.add_argument(
        "--smart-cache",
        action="store_true",
        help="Enable smart SHA-based caching (default if available)"
    )

    parser.add_argument(
        "--legacy-cache",
        action="store_true",
        help="Force use of legacy time-based caching"
    )

    return parser.parse_args()


def get_git_commits(num_commits: int) -> List[Dict[str, str]]:
    """
    Fetch the last n commits from the git repository.
    
    Args:
        num_commits: Number of commits to fetch
        
    Returns:
        List of commit dictionaries with hash, message, author, and date
        
    Raises:
        subprocess.CalledProcessError: If git command fails
        FileNotFoundError: If git is not installed
    """
    try:
        # Get commit information in a structured format
        git_command = [
            "git", "log", 
            f"-{num_commits}",
            "--pretty=format:%H|%s|%an|%ad",
            "--date=short"
        ]
        
        result = subprocess.run(
            git_command,
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0][:8],  # Short hash
                        'message': parts[1],
                        'author': parts[2],
                        'date': parts[3]
                    })
        
        return commits
        
    except FileNotFoundError:
        console.print("[red]Error: Git is not installed or not in PATH[/red]")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        if "not a git repository" in e.stderr.lower():
            console.print("[red]Error: Current directory is not a git repository[/red]")
        else:
            console.print(f"[red]Error running git command: {e.stderr}[/red]")
        sys.exit(1)


def parse_github_repo(repo_input: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL or owner/repo format.
    
    Args:
        repo_input: Repository URL or owner/repo string
        
    Returns:
        Tuple of (owner, repo)
        
    Raises:
        ValueError: If repo format is invalid
    """
    # Handle different formats
    if repo_input.startswith(('http://', 'https://')):
        # Parse URL
        parsed = urlparse(repo_input)
        if 'github.com' not in parsed.netloc:
            raise ValueError("URL must be a GitHub repository URL")
        
        # Extract owner/repo from path
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL format")
        
        owner, repo = path_parts[0], path_parts[1]
        
    elif '/' in repo_input:
        # Handle owner/repo format
        parts = repo_input.split('/', 1)
        if len(parts) != 2:
            raise ValueError("Invalid repository format. Use 'owner/repo' or GitHub URL")
        owner, repo = parts
        
    else:
        raise ValueError("Invalid repository format. Use 'owner/repo' or GitHub URL")
    
    # Remove .git suffix if present
    if repo.endswith('.git'):
        repo = repo[:-4]
    
    return owner, repo


async def get_github_commits_enhanced(
    repo_url: str, 
    num_commits: int, 
    cache_manager: EnhancedCacheManager,
    rate_limiter: MemoryOptimizedRateLimiter
) -> List[Dict[str, str]]:
    """
    Enhanced GitHub commits fetcher with async processing, caching, and rate limiting.

    Args:
        repo_url: GitHub repository URL or owner/repo format
        num_commits: Number of commits to fetch
        cache_manager: Cache manager for caching results
        rate_limiter: Rate limiter for API requests

    Returns:
        List of commit dictionaries with hash, message, author, and date

    Raises:
        ValueError: If repo URL is invalid
        aiohttp.ClientError: If API request fails
    """
    try:
        owner, repo = parse_github_repo(repo_url)

        # Check cache first if available
        if await cache_manager.is_cache_enabled():
            cached_commits, should_refresh = await check_cached_commits_freshness(
                cache_manager, owner, repo, num_commits
            )

            if cached_commits and not should_refresh:
                console.print(f"[green]Using cached commits for {owner}/{repo}[/green]")
                await cache_manager.add_repo_to_cache(owner, repo)  # Update access time
                return cached_commits
        
        session = await get_enhanced_http_session(rate_limiter.config)
        api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
        
        commits = []
        total_fetched = 0
        page = 1
        
        console.print(f"[yellow]Fetching {num_commits} commits from GitHub...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching commits...", total=None)
            
            while total_fetched < num_commits:
                await rate_limiter.wait_if_needed()
                
                # Parameters for pagination and limiting results
                params = {
                    'per_page': min(100, num_commits - total_fetched),  # GitHub API max per page
                    'page': page
                }
                
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        async with session.get(api_url, params=params) as response:
                            # Handle rate limiting
                            if await rate_limiter.handle_rate_limit_response(response):
                                retry_count += 1
                                continue
                            
                            if response.status == 401 or response.status == 403:
                                error_data = None
                                try:
                                    error_data = await response.json()
                                except:
                                    pass
                                
                                if error_data and 'private' in error_data.get('message', '').lower():
                                    raise aiohttp.ClientError(
                                        f"Repository '{owner}/{repo}' is private. "
                                        "Please provide authentication or use a public repository."
                                    )
                                else:
                                    raise aiohttp.ClientError(
                                        f"Access denied to '{owner}/{repo}'. Check permissions or repository visibility."
                                    )
                            elif response.status == 404:
                                raise aiohttp.ClientError(
                                    f"Repository '{owner}/{repo}' not found. "
                                    "Please check the repository name and ensure it exists."
                                )
                            elif response.status != 200:
                                error_text = await response.text()
                                raise aiohttp.ClientError(f"GitHub API error {response.status}: {error_text}")
                            
                            # Parse response
                            commit_data = await response.json()
                            
                            if not commit_data:
                                console.print("[yellow]No more commits available[/yellow]")
                                break
                            
                            for commit in commit_data:
                                if total_fetched >= num_commits:
                                    break
                                
                                try:
                                    # Extract commit information
                                    commit_info = commit['commit']
                                    author_info = commit_info['author']
                                    
                                    commit_dict = {
                                        'hash': commit['sha'][:8],  # Short hash
                                        'full_sha': commit['sha'],   # Store full SHA for smart caching
                                        'message': commit_info['message'],
                                        'author': author_info['name'],
                                        'date': author_info['date'][:10]  # YYYY-MM-DD format
                                    }
                                    
                                    commits.append(commit_dict)
                                    total_fetched += 1
                                    
                                    # Memory management - force GC periodically
                                    if total_fetched % GC_FREQUENCY == 0:
                                        gc.collect()
                                
                                except KeyError as e:
                                    console.print(f"[yellow]Warning: Skipping malformed commit data: {e}[/yellow]")
                                    continue
                            
                            # Check if we need to fetch more pages
                            if len(commit_data) < params['per_page']:
                                break
                            
                            page += 1
                            break  # Success, exit retry loop
                            
                    except aiohttp.ClientTimeout:
                        if retry_count < max_retries - 1:
                            retry_count += 1
                            wait_time = 2 ** retry_count
                            console.print(f"[yellow]Request timeout, retrying in {wait_time} seconds... ({retry_count}/{max_retries})[/yellow]")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise aiohttp.ClientError("Request to GitHub API timed out after multiple attempts. Please try again.")
                    
                    except aiohttp.ClientError as e:
                        if retry_count < max_retries - 1:
                            retry_count += 1
                            wait_time = 2 ** retry_count
                            console.print(f"[yellow]Connection error, retrying in {wait_time} seconds... ({retry_count}/{max_retries})[/yellow]")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise e

        # Cache the results if cache manager is available
        if await cache_manager.is_cache_enabled() and commits:
            await cache_manager.cache_commits(owner, repo, commits)
            await cache_manager.add_repo_to_cache(owner, repo)
            
            # Cache basic repository metadata to ensure it shows up in lists
            basic_metadata = {
                'owner': owner,
                'repo': repo,
                'last_updated': datetime.now().isoformat(),
                'commit_count': len(commits)
            }
            await cache_manager.cache_repo_metadata(owner, repo, basic_metadata)
            
            # Update latest SHA if using smart caching
            if isinstance(cache_manager, SmartCacheManager) and commits:
                latest_sha = commits[0]['full_sha'] # Use full_sha from the fetched commit
                await cache_manager.cache_latest_sha(owner, repo, latest_sha)
            elif hasattr(cache_manager, 'config') and cache_manager.config.is_smart_caching_enabled():
                if commits:
                    # Create a minimal rate limiter for SHA caching
                    temp_rate_limiter = MemoryOptimizedRateLimiter(cache_manager.config)
                    smart_cache = SmartCacheManager(cache_manager.config, temp_rate_limiter)
                    latest_sha = commits[0]['full_sha']
                    await smart_cache.cache_latest_sha(owner, repo, latest_sha)
            
            console.print(f"[green]Cached {len(commits)} commits for future use[/green]")

        return commits
        
    except ValueError as e:
        raise ValueError(f"Invalid repository format: {str(e)}")


def display_commits_preview(commits: List[Dict[str, str]], num_commits: int):
    """Display a preview of commits in an interactive table."""
    console.print(f"\n[bold blue]Preview of last {num_commits} commits:[/bold blue]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Hash", style="cyan", width=8)
    table.add_column("Date", style="green", width=10)
    table.add_column("Author", style="yellow", width=20)
    table.add_column("Message", style="white")
    
    for commit in commits:
        table.add_row(
            commit['hash'],
            commit['date'],
            commit['author'][:18] + "..." if len(commit['author']) > 18 else commit['author'],
            commit['message'][:60] + "..." if len(commit['message']) > 60 else commit['message']
        )
    
    console.print(table)
    console.print()


def categorize_commits(commits: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Categorize commits by type for better prompt engineering."""
    categories = {
        'features': [],
        'fixes': [],
        'improvements': [],
        'docs': [],
        'refactor': [],
        'other': []
    }
    
    for commit in commits:
        message = commit['message'].lower()
        
        if any(word in message for word in ['feat', 'feature', 'add', 'new']):
            categories['features'].append(commit)
        elif any(word in message for word in ['fix', 'bug', 'issue', 'problem']):
            categories['fixes'].append(commit)
        elif any(word in message for word in ['improve', 'enhance', 'optimize', 'better']):
            categories['improvements'].append(commit)
        elif any(word in message for word in ['doc', 'readme', 'comment']):
            categories['docs'].append(commit)
        elif any(word in message for word in ['refactor', 'clean', 'restructure']):
            categories['refactor'].append(commit)
        else:
            categories['other'].append(commit)
    
    return categories


def format_commits_for_api(commits: List[Dict[str, str]], repo_url: str = None) -> str:
    """
    Format commit data for the Claude API request with enhanced prompt engineering.
    
    Args:
        commits: List of commit dictionaries
        repo_url: Repository URL for context
        
    Returns:
        Formatted string containing commit information for the API
    """
    if not commits:
        return "No commits found."
    
    # Categorize commits for better organization
    categories = categorize_commits(commits)
    
    # Build structured commit information
    commit_sections = []
    
    for category, category_commits in categories.items():
        if category_commits:
            commit_sections.append(f"\n## {category.title()}")
            for commit in category_commits:
                commit_sections.append(
                    f"• {commit['hash']} - {commit['message']} "
                    f"(by {commit['author']} on {commit['date']})"
                )
    
    commit_text = "\n".join(commit_sections)
    
    # Enhanced prompt for Vercel-style changelogs
    repo_info = f"\nRepository: {repo_url}" if repo_url else ""
    
    prompt = f"""You are an expert at creating professional, beautifully formatted changelogs from git commit history. 
Your task is to analyze the following commits and generate a changelog that matches the style of Vercel's changelog - 
beautiful, professional, and user-focused.

IMPORTANT GUIDELINES:
1. Format like Vercel's changelog with clear dates, author names, and professional descriptions
2. Focus on user-facing changes and benefits
3. Use clear, professional language that explains what users can do with new features
4. Include code examples when relevant (like Vercel does)
5. Group related changes into logical sections
6. Use emojis sparingly but effectively (🚀 for features, 🔧 for improvements, 🐛 for fixes)
7. Use ONLY the actual author names from the commit data - DO NOT make up GitHub usernames
8. Explain the benefits and use cases clearly
9. Use a professional, positive tone throughout
10. Format with proper markdown structure
11. DO NOT include fake GitHub links or usernames
12. End with a proper reference to the actual repository

COMMIT HISTORY:
{commit_text}{repo_info}

Please generate a changelog that:
- Matches Vercel's professional style and formatting
- Includes clear dates and versioning
- Explains features with benefits and use cases
- Uses professional language throughout
- Groups changes logically
- Includes code examples when relevant
- Maintains beautiful, readable formatting
- Focuses on user-facing improvements
- Uses ONLY real author names from the commit data
- Ends with proper repository reference using the actual repository URL

Format the output as a professional changelog suitable for a company website like Vercel or Mintlify."""

    return prompt


async def call_claude_api_enhanced(prompt: str, config: EnhancedConfig, args: argparse.Namespace) -> str:
    """
    Enhanced async Claude API caller with improved error handling and retries.
    
    Args:
        prompt: The formatted prompt containing commit information
        config: Configuration object
        args: Command line arguments
        
    Returns:
        Generated changelog text
        
    Raises:
        aiohttp.ClientError: If API request fails
    """
    # Get API configuration with fallbacks
    api_key = args.api_key or config.get('api_key', DEFAULT_API_KEY)
    base_url = args.api_url or config.get('api_url', DEFAULT_BASE_URL)
    api_endpoint = config.get('api_endpoint', DEFAULT_API_ENDPOINT)
    
    url = f"{base_url}{api_endpoint}"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.5
    }
    
    # Create a separate session for Claude API (not using the GitHub session)
    connector = aiohttp.TCPConnector(
        limit=5,
        limit_per_host=5,
        ttl_dns_cache=300,
        use_dns_cache=True
    )
    timeout = aiohttp.ClientTimeout(total=90, connect=10)  # Longer timeout for AI processing
    
    # Retry logic for better reliability
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Generating changelog with AI...", total=None)
                    
                    async with session.post(url, json=payload) as response:
                        if response.status == 401:
                            raise aiohttp.ClientError("API authentication failed. Check your API key.")
                        elif response.status == 429:
                            console.print(f"[yellow]Rate limited, retrying in 30 seconds... (attempt {attempt + 1}/{max_retries})[/yellow]")
                            await asyncio.sleep(30)
                            continue
                        elif response.status != 200:
                            error_text = await response.text()
                            raise aiohttp.ClientError(f"API request failed with status {response.status}: {error_text}")
                        
                        response_data = await response.json()
                        
                        # Extract the content from Claude's response
                        if "content" in response_data and response_data["content"]:
                            return response_data["content"][0]["text"]
                        else:
                            return "No changelog generated."
                            
        except aiohttp.ClientTimeout:
            if attempt < max_retries - 1:
                console.print(f"[yellow]Request timed out, retrying... (attempt {attempt + 1}/{max_retries})[/yellow]")
                await asyncio.sleep(5)
                continue
            else:
                raise aiohttp.ClientError("Request timed out after multiple attempts. Please try again.")
        except aiohttp.ClientError as e:
            if attempt < max_retries - 1:
                console.print(f"[yellow]Connection error, retrying... (attempt {attempt + 1}/{max_retries})[/yellow]")
                await asyncio.sleep(5)
                continue
            else:
                raise e
        except Exception as e:
            raise aiohttp.ClientError(f"Unexpected error: {str(e)}")


def save_changelog(changelog: str, output_path: str, format_type: str):
    """Save changelog to file in the specified format."""
    try:
        if format_type == "json":
            # Convert markdown to structured JSON
            import re
            sections = re.split(r'^##\s+', changelog, flags=re.MULTILINE)
            structured_data = {
                "generated_at": datetime.now().isoformat(),
                "sections": []
            }
            
            for section in sections[1:]:  # Skip first empty section
                lines = section.strip().split('\n')
                if lines:
                    section_title = lines[0].strip()
                    items = []
                    for line in lines[1:]:
                        if line.strip().startswith('- ') or line.strip().startswith('• '):
                            items.append(line.strip()[2:])
                    
                    structured_data["sections"].append({
                        "title": section_title,
                        "items": items
                    })
            
            with open(output_path, 'w') as f:
                json.dump(structured_data, f, indent=2)
        else:
            # Save as markdown or text
            with open(output_path, 'w') as f:
                f.write(changelog)
        
        console.print(f"[green]Changelog saved to: {output_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error saving changelog: {str(e)}[/red]")
        sys.exit(1)


def display_changelog(changelog: str, num_commits: int, format_type: str = "markdown"):
    """
    Display the generated changelog in a beautiful format.
    
    Args:
        changelog: The generated changelog text
        num_commits: Number of commits processed
        format_type: Output format type
    """
    console.print()
    console.print(Panel.fit(
        f"[bold blue]Changelog Generated[/bold blue]\n"
        f"[dim]Based on the last {num_commits} commits[/dim]",
        border_style="blue"
    ))
    console.print()
    
    if format_type == "json":
        # Display JSON structure in a readable format
        try:
            data = json.loads(changelog)
            console.print(json.dumps(data, indent=2))
        except:
            console.print(changelog)
    else:
        # Display the changelog as markdown for better formatting
        try:
            markdown = Markdown(changelog)
            console.print(markdown)
        except Exception:
            # Fallback to plain text if markdown parsing fails
            console.print(changelog)
    
    console.print()


def show_configuration(config: EnhancedConfig):
    """Display current configuration."""
    console.print("\n[bold blue]Current Configuration:[/bold blue]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    api_key = config.get('api_key', DEFAULT_API_KEY)
    masked_key = api_key[:10] + "..." if len(api_key) > 10 else api_key
    table.add_row("API Key", masked_key)
    table.add_row("API URL", config.get('api_url', DEFAULT_BASE_URL))
    table.add_row("API Endpoint", config.get('api_endpoint', DEFAULT_API_ENDPOINT))
    table.add_row("Config File", str(config.config_file))
    
    # GitHub token info
    github_token = config.get_github_token()
    if github_token:
        masked_github = github_token[:8] + "..." if len(github_token) > 8 else github_token
        table.add_row("GitHub Token", masked_github)
    else:
        table.add_row("GitHub Token", "[red]Not configured[/red]")
    
    console.print(table)
    console.print()


async def async_main(args: argparse.Namespace):
    """
    Async main function that handles the core processing.
    """
    # Initialize configuration and components
    config = EnhancedConfig()
    
    # Use SmartCacheManager if smart caching is enabled
    use_smart_cache = config.is_smart_caching_enabled()
    
    # Override with command line arguments
    if args.smart_cache:
        use_smart_cache = True
    elif args.legacy_cache:
        use_smart_cache = False
    
    # Initialize rate limiter first
    rate_limiter = MemoryOptimizedRateLimiter(config)
    
    if use_smart_cache:
        cache_manager = SmartCacheManager(config, rate_limiter)
        console.print("[dim]🧠 Smart caching enabled with SHA-based update detection[/dim]")
    else:
        cache_manager = EnhancedCacheManager(config)
        console.print("[dim]📅 Using standard time-based caching[/dim]")
    
    # Handle cache management commands
    if args.cache_stats:
        stats = await cache_manager.get_cache_stats()
        console.print("\n[bold blue]Cache Statistics:[/bold blue]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), str(value))

        console.print(table)
        
        # Show smart caching specific stats if available
        if isinstance(cache_manager, SmartCacheManager):
            console.print("\n[bold blue]Smart Caching Features:[/bold blue]")
            console.print("• ✅ SHA-based update detection")
            console.print("• ✅ Repository usage tracking") 
            console.print("• ✅ Enhanced repository backlog")
            console.print("• ✅ Intelligent cache refresh")
        else:
            console.print("\n[dim]💡 Use --smart-cache to enable smart caching features[/dim]")
        
        return

    if args.clear_cache:
        if Confirm.ask("Are you sure you want to clear all cached data?"):
            await cache_manager.clear_cache()
        return

    if args.list_repos:
        # Use smart repository list if available
        if isinstance(cache_manager, SmartCacheManager):
            cached_repos = await cache_manager.get_smart_cached_repos()
        else:
            cached_repos = await cache_manager.get_cached_repos()
            
        if cached_repos:
            console.print("\n[bold blue]Cached Repositories:[/bold blue]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Repository", style="green")
            table.add_column("Last Accessed", style="yellow")
            
            # Add smart caching columns if available
            if isinstance(cache_manager, SmartCacheManager):
                table.add_column("Status", style="white")
                table.add_column("Usage", style="blue")

            for repo in cached_repos:
                last_accessed = repo.get('last_accessed', 'Unknown')
                if last_accessed != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                        last_accessed = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                if isinstance(cache_manager, SmartCacheManager):
                    # Enhanced display with smart caching info
                    has_new_commits = repo.get('has_new_commits', False)
                    estimated_new_count = repo.get('estimated_new_count', 0)
                    usage_count = repo.get('usage_count', 0)
                    
                    if has_new_commits and estimated_new_count > 0:
                        status = f"📬 {estimated_new_count} new"
                    elif has_new_commits:
                        status = "⚡ Updates"
                    else:
                        status = "✓ Current"
                    
                    usage_info = f"{usage_count}x" if usage_count > 0 else "New"
                    table.add_row(repo['full_name'], last_accessed, status, usage_info)
                else:
                    # Basic display
                    table.add_row(repo['full_name'], last_accessed)

            console.print(table)
            
            if isinstance(cache_manager, SmartCacheManager):
                console.print("\n[dim]Status: ✓ Current • ⚡ Updates available • 📬 New commits detected[/dim]")
        else:
            console.print("[yellow]No cached repositories found.[/yellow]")
        return

    # Disable cache if requested
    if args.no_cache:
        config.set('cache.enabled', False)
        cache_manager = EnhancedCacheManager(config)  # Reinitialize with disabled cache
    
    # Repository selection logic
    selected_repo = args.repo

    # If no repo specified and cache is enabled, show cached repos
    if not selected_repo and await cache_manager.is_cache_enabled():
        selected_repo = await display_cached_repos_async(cache_manager)

        if selected_repo == 'new':
            selected_repo = Prompt.ask("Enter GitHub repository (owner/repo or URL)")
        elif selected_repo is None:
            # User chose to skip, check if we're in a git repo
            try:
                get_git_commits(1)  # Test if we're in a git repo
                selected_repo = None  # Use local repo
            except:
                console.print("[red]No repository selected and not in a git repository.[/red]")
                console.print("[yellow]Please specify a GitHub repository with --repo or run from a git repository.[/yellow]")
                return

    # Determine whether to use GitHub API or local git
    if selected_repo:
        console.print(f"[bold green]Fetching last {args.num_commits} commits from GitHub repository: {selected_repo}[/bold green]")

        try:
            # Get commits from GitHub with enhanced async processing
            commits = await get_github_commits_enhanced(selected_repo, args.num_commits, cache_manager, rate_limiter)
            
            if not commits:
                console.print("[yellow]No commits found in the repository.[/yellow]")
                return
            
            console.print(f"[green]Found {len(commits)} commits from GitHub[/green]")
            
        except ValueError as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return
        except aiohttp.ClientError as e:
            if "private" in str(e).lower() or "authentication" in str(e).lower():
                console.print(f"[red]Error: {str(e)}[/red]")
                console.print("[yellow]Tip: Set GITHUB_TOKEN environment variable for private repositories.[/yellow]")
            else:
                console.print(f"[red]Error: {str(e)}[/red]")
            return
        except Exception as e:
            console.print(f"[red]Error connecting to GitHub: {str(e)}[/red]")
            return
    else:
        console.print(f"[bold green]Fetching last {args.num_commits} commits from local repository...[/bold green]")
        
        # Get git commits from local repository
        commits = get_git_commits(args.num_commits)
        
        if not commits:
            console.print("[yellow]No commits found in the repository.[/yellow]")
            return
        
        console.print(f"[green]Found {len(commits)} commits[/green]")
    
    # Interactive mode: show preview and get confirmation
    if args.interactive:
        display_commits_preview(commits, args.num_commits)
        
        if not Confirm.ask("Proceed with generating changelog?"):
            console.print("[yellow]Operation cancelled by user[/yellow]")
            return
    
    # Format commits for API
    repo_url = selected_repo if selected_repo else None
    prompt = format_commits_for_api(commits, repo_url)
    
    # Generate changelog using Claude API
    try:
        changelog = await call_claude_api_enhanced(prompt, config, args)
    except aiohttp.ClientError as e:
        console.print(f"[red]Error generating changelog: {str(e)}[/red]")
        return
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        return
    
    # Handle output
    if args.output:
        save_changelog(changelog, args.output, args.format)
    else:
        # Display the result
        display_changelog(changelog, len(commits), args.format)


def main():
    """Main function that orchestrates the changelog generation process."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Initialize configuration for sync operations
        config = EnhancedConfig()

        # Handle configuration display (sync operation)
        if args.config:
            show_configuration(config)
            return

        # Validate arguments
        if args.num_commits <= 0:
            console.print("[red]Error: Number of commits must be positive[/red]")
            sys.exit(1)

        # Run async main function
        asyncio.run(async_main(args))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        asyncio.run(cleanup_global_session())
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        asyncio.run(cleanup_global_session())
        sys.exit(1)
    finally:
        # Ensure cleanup
        try:
            asyncio.run(cleanup_global_session())
        except:
            pass


if __name__ == "__main__":
    main() 