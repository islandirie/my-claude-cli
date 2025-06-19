#!/bin/bash

echo "🚀 Setting up Dev Assistant CLI..."

# Default to Python implementation
echo "🐍 Setting up Python implementation (recommended)"
IMPLEMENTATION="python"

# Ask about virtual environment
read -p "Use a virtual environment for installation? [Y/n] (recommended): " USE_VENV
USE_VENV=${USE_VENV:-Y}

# Optional: Uncomment the following lines to enable selection of implementation
# read -p "Which implementation do you want to install? [python/js/both] (default: python): " IMPLEMENTATION_CHOICE
# if [[ "$IMPLEMENTATION_CHOICE" == "js" || "$IMPLEMENTATION_CHOICE" == "both" ]]; then
#   IMPLEMENTATION=$IMPLEMENTATION_CHOICE
# fi

if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
    echo "🐍 Setting up Python implementation..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi

    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 is not installed. Please install pip3 first."
        exit 1
    fi
fi

if [[ "$IMPLEMENTATION" == "js" || "$IMPLEMENTATION" == "both" ]]; then
    echo "🟨 Setting up JavaScript implementation..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js first."
        exit 1
    fi

    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed. Please install npm first."
        exit 1
    fi
fi

# Create CLI directory
CLI_DIR="$HOME/dev-assistant-cli"
echo "📁 Creating CLI directory at $CLI_DIR"
mkdir -p "$CLI_DIR"

if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
    # Copy Python files
    echo "📄 Copying Python CLI files..."
    cp dev_cli.py "$CLI_DIR/"
    cp requirements.txt "$CLI_DIR/"

    # Make CLI executable
    chmod +x "$CLI_DIR/dev_cli.py"

    # Setup virtual environment if requested
    cd "$CLI_DIR"
    if [[ "$USE_VENV" =~ ^[Yy]$ ]]; then
        echo "🧪 Setting up virtual environment..."
        
        # Check if venv module is available
        if ! python3 -c "import venv" &> /dev/null; then
            echo "❌ Python venv module not found. Please install it first."
            echo "   On Ubuntu/Debian: sudo apt-get install python3-venv"
            echo "   On macOS: It should be included with Python 3"
            exit 1
        fi
        
        # Create virtual environment
        python3 -m venv venv
        
        # Activate virtual environment
        source venv/bin/activate
        
        echo "✅ Virtual environment created and activated"
        
        # Create activation script
        cat > activate_dev_cli.sh << 'ACTIVATE_EOF'
#!/bin/bash
# Helper script to activate the virtual environment
source "$(dirname "$0")/venv/bin/activate"
echo "✅ Dev CLI virtual environment activated"
echo "Run 'dev --help' to see available commands"
ACTIVATE_EOF
        chmod +x activate_dev_cli.sh
    fi

    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Specifically check for Anthropic installation
    if ! python3 -c "import anthropic" &> /dev/null; then
        echo "📦 Installing Anthropic SDK..."
        pip3 install anthropic>=0.20.0
    else
        echo "✅ Anthropic SDK already installed."
    fi

    # Create wrapper script for global access
    echo "🌍 Creating global access to Python CLI..."
    
    if [[ "$USE_VENV" =~ ^[Yy]$ ]]; then
        # Create a wrapper script that activates the venv
        cat > "/tmp/dev_wrapper.sh" << EOF
#!/bin/bash
# Wrapper script for dev-cli that activates virtual environment
CLI_DIR="$CLI_DIR"
source "\$CLI_DIR/venv/bin/activate"
"\$CLI_DIR/dev_cli.py" "\$@"
EOF
        chmod +x "/tmp/dev_wrapper.sh"
        sudo mv "/tmp/dev_wrapper.sh" "/usr/local/bin/dev"
    else
        # Direct symlink if not using venv
        sudo ln -sf "$CLI_DIR/dev_cli.py" "/usr/local/bin/dev"
    fi
    
    echo "✅ Python implementation installed!"
    cd - > /dev/null
fi

if [[ "$IMPLEMENTATION" == "js" || "$IMPLEMENTATION" == "both" ]]; then
    # Copy JavaScript files
    echo "📄 Copying JavaScript CLI files..."
    mkdir -p "$CLI_DIR/js"
    cp js/dev-cli.js "$CLI_DIR/js/"
    cp package.json "$CLI_DIR/"

    # Make CLI executable
    chmod +x "$CLI_DIR/js/dev-cli.js"

    # Install dependencies
    echo "📦 Installing JavaScript dependencies..."
    cd "$CLI_DIR"
    npm install

    # Install globally
    echo "🌍 Installing JavaScript CLI globally..."
    npm install -g .
    
    echo "✅ JavaScript implementation installed!"
    cd - > /dev/null
fi

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not found in environment variables"
    echo "🔑 To use AI commands, set your Claude API key:"
    echo "    export ANTHROPIC_API_KEY=your_key_here"
    echo "    # Add to your ~/.bashrc or ~/.zshrc for persistence"
fi

# Create sample config if it doesn't exist
if [ ! -f ".dev-commands.yaml" ]; then
    echo "📝 Creating sample .dev-commands.yaml in current directory..."
    
    if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
        cat > .dev-commands.yaml << 'EOF'
# Sample .dev-commands.yaml - Customize for your project
project:
  name: "my-python-project"
  stack: ["Python", "Flask", "SQLAlchemy", "HTML/CSS/JS"]
  standards:
    commit_style: "conventional commits"

quick_commands:
  run:
    description: "Run the development server"
    actions:
      - "flask run --debug"
  
  test:
    description: "Run tests"
    actions:
      - "python -m pytest"

ai_commands:
  create:
    route:
      description: "Create a new Flask route"
      context_needed: ["route path", "functionality"]
      template: "Create a Flask route with proper error handling"
EOF
    elif [[ "$IMPLEMENTATION" == "js" ]]; then
        cat > .dev-commands.yaml << 'EOF'
# Sample .dev-commands.yaml - Customize for your project
project:
  name: "my-js-project"
  stack: ["React", "TypeScript", "Node.js"]
  standards:
    commit_style: "conventional commits"

quick_commands:
  build:
    description: "Build the project"
    actions:
      - "npm run build"
  
  test:
    description: "Run tests"
    actions:
      - "npm test"

ai_commands:
  create:
    component:
      description: "Create a new component"
      context_needed: ["component name"]
      template: "Create a React component with TypeScript"
EOF
    fi
fi

echo ""
echo "✅ Dev Assistant CLI installed successfully!"
echo ""

if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
    echo "📚 Python Quick start:"
    echo "   dev --help          # Show available commands"
    echo "   dev run             # Run development server"
    echo "   dev create route /users  # AI-powered route generation"
    echo ""
    
    if [[ "$USE_VENV" =~ ^[Yy]$ ]]; then
        echo "🧪 Virtual Environment:"
        echo "   Virtual environment is set up at $CLI_DIR/venv"
        echo "   To activate manually: source $CLI_DIR/venv/bin/activate"
        echo "   Or use the helper script: $CLI_DIR/activate_dev_cli.sh"
        echo "   The 'dev' command automatically uses the virtual environment"
        echo ""
    fi
fi

if [[ "$IMPLEMENTATION" == "js" || "$IMPLEMENTATION" == "both" ]]; then
    echo "� JavaScript Quick start:"
    echo "   devjs --help         # Show available commands"
    echo "   devjs build          # Run build command"
    echo "   devjs create component Button  # AI-powered component generation"
    echo ""
fi

echo "�🔧 Next steps:"
echo "   1. Customize your .dev-commands.yaml file"
echo "   2. Set ANTHROPIC_API_KEY for AI features"
echo "   3. Run 'dev --help' or 'devjs --help' to see your custom commands"
echo ""