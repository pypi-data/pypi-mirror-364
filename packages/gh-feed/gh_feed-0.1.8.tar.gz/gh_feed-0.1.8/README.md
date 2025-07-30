# gh-feed

![PyPI](https://img.shields.io/pypi/v/gh-feed)
![License](https://img.shields.io/github/license/bhantsi/gh-feed)
![Issues](https://img.shields.io/github/issues/bhantsi/gh-feed)


**gh-feed** is a command-line tool written in Python that fetches and displays a GitHub user's recent public activity directly in the terminal.  
It uses the GitHub API and works with no external libraries.

## 🚀 Features

- **Fetches GitHub activity** - Get the most recent public events for any GitHub user
- **Rich event support** - Supports pushes, issues, pull requests, stars, forks, releases, comments, and more
- **Beautiful output** - Colorized terminal output with relative timestamps (e.g., "2h ago")
- **Smart filtering** - Filter events by type using `--filter <event_type>`
- **Export functionality** - Export results to JSON with `--json` flag
- **Authentication support** - Use GitHub tokens via `--token` or `GITHUB_TOKEN` env variable
- **Interactive mode** - Step-by-step guided usage with `--interactive`
- **Offline caching** - Caches API responses for 5 minutes to reduce API calls
- **Error handling** - Graceful handling of rate limits, network issues, and invalid users
- **Update notifications** - Automatic check for new versions with upgrade instructions
- **Version information** - Check current version with `--version` or `-v`
- **Comprehensive help** - Detailed usage guide with `--help` or `-h`
- **No dependencies** - Pure Python standard library, no external packages required

---

## 📦 Installation

### From PyPI (Recommended)

Install the latest stable version from PyPI:

```bash
pip install gh-feed
```

### From TestPyPI (Development)

For testing pre-release versions, you can install from TestPyPI:

```bash
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gh-feed
```

### Development Installation

For development or contributing:

```bash
git clone https://github.com/bhantsi/gh-feed.git
cd gh-feed
pip install -e .
```

---

## 🛠️ Usage

### Prerequisites
- Python 3 (comes pre-installed on most systems)

### Running the CLI

After installation, you can run the CLI from anywhere:

```bash
gh-feed <github_username>
```

Or, if you want to run the script directly (if you have the source):

```bash
python3 app.py <github_username>
```

### Basic Commands

```bash
# Get user activity
gh-feed octocat

# Show version
gh-feed --version
gh-feed -v

# Show help
gh-feed --help
gh-feed -h

# Interactive mode
gh-feed --interactive
```

### Filtering Events

You can filter by event type (e.g., only show push events):

```bash
gh-feed octocat --filter PushEvent
```

### Exporting to JSON

Export the latest events to a file:

```bash
gh-feed octocat --json
```

You can combine filtering and export:

```bash
gh-feed octocat --filter IssuesEvent --json
```

### Using a GitHub Token

To increase your API rate limit, you can provide a personal access token:

```bash
gh-feed octocat --token <your_github_token>
```

Or set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_github_token
gh-feed octocat
```

### Interactive Mode

Start an interactive session for guided usage:

```bash
gh-feed --interactive
```
You'll be prompted for the username, event filter, token, and export options.

### Caching

API responses are cached for 5 minutes in the `~/.cache/gh-feed/` directory to reduce API calls and speed up repeated queries.

### Update Notifications

The tool automatically checks for new versions when you run commands and notifies you if an update is available:

```
📦 New version available: 0.1.4 (current: 0.1.3)
💡 Run 'pip install --upgrade gh-feed' to update
```

### Example

```bash
gh-feed octocat
```

Sample output:
```
- Pushed 2 commits to octocat/Hello-World (3h ago)
- Opened an issue in octocat/Hello-World (5h ago)
- Starred octocat/Spoon-Knife (1d ago)

Summary:
- push commit: 1
- issue opened: 1
- repo starred: 1
- Activity in 3 repos
```

---

## 🤝 Contributing

### For Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -m "Add feature"`
5. Push to your branch: `git push origin feature-name`
6. Create a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/bhantsi/gh-feed.git
cd gh-feed

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v

# Run the tool locally
python -m gh_feed <username>
```

### Manual Deployment

To deploy a new version to PyPI:

```bash
# Update version in pyproject.toml
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

---

## ⚠️ Important Notes

- **Rate Limits**: GitHub API has rate limits (60 requests/hour for unauthenticated, 5000/hour with token)
- **Public Activity Only**: Only shows public GitHub activity
- **Recent Events**: Limited to the most recent 30 events from GitHub API
- **Cache Duration**: Responses are cached for 5 minutes to reduce API calls

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🐛 Issues & Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/bhantsi/gh-feed/issues) page
2. Create a new issue with detailed information
3. Include your Python version and operating system

---

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/gh-feed/
- **GitHub Repository**: https://github.com/bhantsi/gh-feed
- **Documentation**: See this README

---

## 📝 Attribution

This project was inspired by the [GitHub User Activity CLI](https://roadmap.sh/projects/github-user-activity) project on [roadmap.sh](https://roadmap.sh/).  
Check out their project for more ideas and inspiration!
