# Dev Assistant CLI Examples

This document provides practical examples of how to use the Dev Assistant CLI in various scenarios.

## Quick Command Examples

### Starting Development Servers

```bash
# Start the Flask development server
dev run

# Run in a specific environment
dev run-prod
```

### Testing

```bash
# Run all tests
dev test

# Run specific test file
dev test app/tests/test_users.py

# Run tests with coverage
dev test-cov
```

### Code Quality

```bash
# Auto-format code with black and isort
dev fix

# Run linters
dev lint

# Clean up project (remove cache, build artifacts)
dev clean
```

## AI Command Examples

### Creating New Components

```bash
# Create a new Flask route
dev create route /api/users get "retrieve all users with pagination and filtering"

# Create a new blueprint
dev create blueprint auth "user authentication and authorization"

# Create a database model
dev create model User "username:string, email:string, created_at:datetime"
```

### Code Analysis

```bash
# Analyze a specific file for improvements
dev analyze app/routes/users.py

# Optimize a database query
dev optimize "SELECT * FROM users JOIN orders ON users.id = orders.user_id"

# Refactor a function to improve readability
dev refactor app/utils/helpers.py get_user_stats
```

### Documentation Generation

```bash
# Generate API documentation
dev docs api /api/users

# Create a README for a module
dev docs readme app/auth

# Generate OpenAPI/Swagger specs
dev docs openapi
```

## Workflow Examples

```bash
# Start a new feature workflow
dev feature_start user-profiles

# Prepare for deployment
dev deploy_prep

# Perform pre-commit checks
dev pre_commit
```

## Custom Commands With Natural Language

```bash
# Ask general questions
dev "what's the best way to implement pagination in Flask-SQLAlchemy?"

# Generate code with specific requirements
dev "create a SQLAlchemy model for a blog post with tags and categories"

# Debug issues
dev "debug why my SQLAlchemy query is returning duplicates"

# Create deployment configurations
dev "create a dockerfile for a Flask application with Gunicorn and Nginx"
```

## Using Custom Vocabulary

Custom vocabulary defined in your YAML file lets you use shorthand:

```bash
# If defined in vocabulary section:
dev "make it faster"  # Expands to optimization request

dev "dockerize it"    # Creates Docker configuration

dev "bulletproof it"  # Adds error handling and validation
```

## Environment Setup Commands

```bash
# Create a new virtual environment for the project
dev setup venv

# Install project dependencies
dev install-deps

# Add a new Python package
dev add flask-login

# Update all dependencies
dev update-deps
```

## Git Workflow Commands

```bash
# Create a new feature branch
dev branch feature user-authentication

# Commit changes with conventional commit message
dev commit "add user login functionality"

# Prepare a PR with template
dev pr-prep
```

## Database Commands

```bash
# Create a new migration
dev db migrate "add user roles table"

# Apply pending migrations
dev db upgrade

# Generate sample data
dev db seed users 50
```

---

Remember to customize these commands in your `.dev-commands.yaml` file to match your specific development workflow and preferences!
