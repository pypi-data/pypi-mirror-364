# Changelog Generator 🚀

[![PyPI version](https://badge.fury.io/py/changelog-generator.svg)](https://badge.fury.io/py/changelog-generator)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, AI-powered command-line tool that generates beautiful changelogs from git commit history using Claude API. Features smart caching, async processing, and seamless GitHub integration.

## ✨ Features

### 🎯 Core Functionality
- **AI-Powered**: Generate professional changelogs using Claude 3.5 Sonnet
- **Multi-Source**: Works with local git repositories and GitHub repositories
- **Beautiful Output**: Rich terminal interface with progress bars and formatted tables
- **Multiple Formats**: Output in Markdown, JSON, or plain text
- **Interactive Mode**: Preview commits before generating changelog

### ⚡ Performance Enhancements
- **Async Processing**: Non-blocking operations for better performance
- **Memory Optimization**: Micro-chunking and garbage collection for large repositories
- **Smart Caching**: Redis-based caching with intelligent freshness detection
- **Rate Limiting**: Intelligent GitHub API rate limiting with token support
- **Connection Pooling**: Efficient HTTP connection management

### 🔗 GitHub Integration
- **Token Authentication**: Automatic GitHub token detection from environment or config
- **Private Repositories**: Support for private repos with proper authentication
- **Rate Limit Handling**: Automatic rate limit detection and backoff
- **Error Recovery**: Robust error handling with automatic retries

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install changelog-generator

# Or install with development dependencies
pip install changelog-generator[dev]
```

### Basic Usage

```bash
# Generate changelog for last 10 commits (local repository)
changelog-generator 10

# Generate changelog for GitHub repository
changelog-generator 10 --repo owner/repo

# Interactive mode with preview
changelog-generator 10 --interactive

# Save to file
changelog-generator 20 --output changelog.md

# Output as JSON
changelog-generator 15 --format json
```

## 📋 Command Line Options

### Required Arguments
- `num_commits`: Number of recent commits to include in the changelog

### Optional Arguments
- `--repo, -r`: GitHub repository (owner/repo or full URL)
- `--interactive, -i`: Interactive mode with commit preview
- `--output, -o`: Output file path (.md, .txt, .json)
- `--format`: Output format (markdown, text, json)
- `--config`: Show current configuration
- `--api-key`: Override API key
- `--api-url`: Override API base URL
- `--no-cache`: Disable caching
- `--cache-stats`: Show cache statistics
- `--clear-cache`: Clear all cached data
- `--list-repos`: List cached repositories
- `--smart-cache`: Enable smart SHA-based caching (default)
- `--legacy-cache`: Force use of legacy time-based caching

## ⚙️ Configuration

### Environment Variables
```bash
# GitHub token for authenticated requests (recommended)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export GH_TOKEN=ghp_xxxxxxxxxxxx  # Alternative

# Optional: Redis configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### Configuration File
Create `~/.changelog_generator.yaml`:

```yaml
# API Configuration
api_key: "your-api-key-here"
api_url: "https://your-api-endpoint.com"
api_endpoint: "/api/message"

# GitHub Configuration
github:
  token: "your-github-token-here"

# Cache Configuration
cache:
  enabled: true
  max_cached_repos: 50
  repo_metadata_ttl: 86400  # 24 hours
  commit_data_ttl: 3600     # 1 hour
  smart_caching:
    enabled: true
    sha_check_frequency: 300  # 5 minutes
    max_commit_cache_per_repo: 1000
    background_updates: true

# Redis Configuration
redis:
  host: localhost
  port: 6379
  db: 0
  decode_responses: true
  socket_timeout: 5
  socket_connect_timeout: 5
```

## 🧠 Smart Caching Features

### SHA-Based Update Detection
- **Precise Detection**: Uses Git-style ahead/behind logic to detect new commits
- **Efficient Updates**: Only fetches new commits when repository has changed
- **Background Monitoring**: Monitors repository state without unnecessary API calls

### Repository Usage Tracking
- **Smart Prioritization**: Frequently used repositories appear first in lists
- **Access Frequency**: Tracks how often repositories are accessed
- **Usage Statistics**: Provides insights into repository usage patterns

### Enhanced Repository Backlog
- **Update Status**: Shows which repositories have new commits
- **Usage Statistics**: Displays access frequency and last accessed time
- **Smart Indicators**: Visual indicators for repository status

## 📊 Examples

### Local Repository
```bash
# Generate changelog for last 15 commits in current directory
changelog-generator 15
```

### GitHub Repository
```bash
# Generate changelog for a public repository
changelog-generator 20 --repo facebook/react

# Generate changelog for a private repository (requires GITHUB_TOKEN)
changelog-generator 10 --repo myorg/private-repo
```

### Interactive Mode
```bash
# Preview commits before generating changelog
changelog-generator 10 --interactive
```

### Save to File
```bash
# Save as Markdown
changelog-generator 25 --output CHANGELOG.md

# Save as JSON
changelog-generator 15 --format json --output changelog.json
```

### Cache Management
```bash
# View cache statistics
changelog-generator 10 --cache-stats

# List cached repositories
changelog-generator 10 --list-repos

# Clear all cached data
changelog-generator 10 --clear-cache
```

## 🔧 Development

### Installation for Development
```bash
# Clone the repository
git clone https://github.com/anantduggal/changelog-generator.git
cd changelog-generator

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=changelog_generator

# Run specific test file
pytest tests/test_core.py
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## 📦 Package Structure

```
changelog-generator/
├── src/
│   └── changelog_generator/
│       ├── __init__.py
│       └── changelog_generator_enhanced.py
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Claude API](https://claude.ai/) for AI-powered changelog generation
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [aiohttp](https://github.com/aio-libs/aiohttp) for async HTTP operations
- [Redis](https://redis.io/) for smart caching functionality

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/anantduggal/changelog-generator/issues)
- **Documentation**: [GitHub Wiki](https://github.com/anantduggal/changelog-generator/wiki)
- **Email**: aduggal@uwaterloo.ca

---

Made with ❤️ by [Anant Duggal](https://github.com/anantduggal) 