# Dev Assistant CLI

A powerful AI-powered CLI tool that uses Claude AI to assist in development tasks through custom commands defined in YAML configuration files.

## Overview

Dev Assistant CLI helps you streamline development workflows by:

- Executing predefined quick commands (shortcuts for frequent tasks)
- Processing AI-powered commands through Claude AI
- Automating multi-step development workflows
- Providing contextual assistance based on project configuration

The tool uses a YAML configuration file to define commands and project context, making it highly customizable for different development environments and languages.

## Key Features

- **Quick Commands**: Simple shortcuts for common tasks
- **AI-Powered Commands**: Complex commands that use Claude AI to generate code, analyze issues, etc.
- **Workflow Automation**: Chain together multiple steps
- **Project Context Awareness**: Provides Claude AI with relevant project information
- **Custom Vocabulary**: Define your own shorthand terms
- **Virtual Environment Support**: Clean dependency isolation

## Prerequisites

- Python 3.7+ (recommended: Python 3.9+)
- pip package manager
- Anthropic API key for Claude AI (sign up at [anthropic.com](https://www.anthropic.com))

## Installation

### Automatic Installation

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Ask if you want to use a virtual environment (recommended)
2. Install required dependencies
3. Create a global `dev` command
4. Generate a sample configuration file

### Manual Installation

1. Ensure Python 3.7+ is installed
2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make the script executable:
   ```bash
   chmod +x dev_cli.py
   ```
5. Set up your API key:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
6. Create a `.dev-commands.yaml` configuration file in your project directory

## Configuration

The CLI uses a YAML configuration file to define commands and project context. Look for a file named:
- `.dev-cheat.yaml`
- `.dev-cheat.yml`
- `dev-commands.yaml`
- `dev-commands.yml`

### Example Configuration

```yaml
# Project Context - Helps Claude understand your environment
project:
  name: "my-python-project"
  type: "web-application"
  stack: 
    - "Flask"
    - "Python"
    - "SQLAlchemy"
    - "HTML/CSS/JS"
  
  # Your coding standards and preferences
  standards:
    commit_style: "conventional commits"
    file_structure: "module-based packages with __init__.py exports"
    testing: "pytest with fixtures and mocking"
  
  # Your preferred tools and commands
  tools:
    package_manager: "pip"
    linter: "flake8 + black"
    database: "PostgreSQL with SQLAlchemy"

# Quick Commands - Simple word → action mappings
quick_commands:
  run:
    description: "Run the development server"
    actions:
      - "flask run --debug"
      - "echo 'Development server running on http://localhost:5000'"
  
  test:
    description: "Run tests with coverage"
    actions:
      - "python -m pytest --cov=app"

# AI-Powered Commands - These require Claude to generate actions
ai_commands:
  create:
    route:
      description: "Generate Flask route with proper error handling"
      context_needed: ["route path", "HTTP method", "functionality"]
      template: |
        Create a Flask route following my standards:
        - Blueprint structure
        - Input validation
        - Proper error handling
        - SQLAlchemy queries
        - Documentation
```

## Usage

### Basic Commands

```bash
# Show available commands
dev --help

# Run a quick command
dev run

# Run an AI-powered command
dev create route /users

# Run a custom request
dev "create a flask route for user authentication"
```

### Command Types

1. **Quick Commands**: Predefined shell commands that run directly
   ```bash
   dev test
   ```

2. **AI Commands**: Commands that use Claude AI to generate actions or code
   ```bash
   dev create route /users get "retrieve all users with pagination"
   ```

3. **Workflows**: A series of steps executed in sequence
   ```bash
   dev feature_start user-authentication
   ```

### Using with Virtual Environment

If you installed with a virtual environment:

1. The `dev` command automatically activates the virtual environment
2. To manually activate: `source ~/dev-assistant-cli/activate_dev_cli.sh`

### Environment Variables

- `ANTHROPIC_API_KEY`: Required for AI commands
  ```bash
  export ANTHROPIC_API_KEY=your_key_here
  # Add to ~/.bashrc or ~/.zshrc for persistence
  ```

## Customization

### Adding Quick Commands

Edit your `.dev-commands.yaml` file:

```yaml
quick_commands:
  migrate:
    description: "Run database migrations"
    actions:
      - "flask db upgrade"
      - "echo 'Migrations completed successfully'"
```

### Adding AI Commands

Create templates for specific AI tasks:

```yaml
ai_commands:
  optimize:
    description: "Optimize code for performance"
    context_needed: ["file path", "performance goals"]
    template: |
      Optimize this code for better performance:
      - Reduce time complexity
      - Minimize database queries
      - Improve algorithm efficiency
```

### Custom Vocabulary

Define shorthand terms for common operations:

```yaml
vocabulary:
  "make it faster": "optimize the code for better performance and response time"
  "dockerize it": "create a Dockerfile and docker-compose.yml for this project"
```

## Troubleshooting

### API Key Issues

```
❌ ANTHROPIC_API_KEY environment variable not set
```

Solution: Set your API key with:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Command Not Found

```
command not found: dev
```

Solution: Either:
1. Run the setup script again
2. Add `/usr/local/bin` to your PATH
3. Use the full path to the script: `~/dev-assistant-cli/dev_cli.py`

### Python Import Errors

```
ImportError: No module named 'anthropic'
```

Solution:
```bash
pip install anthropic
```

### Permission Denied

```
permission denied: ./dev_cli.py
```

Solution:
```bash
chmod +x dev_cli.py
```

## License

MIT License

## Acknowledgements

- Powered by [Claude AI](https://www.anthropic.com/claude) from Anthropic
- Inspired by AI-powered development workflows and custom command languages
