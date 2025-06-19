#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const yaml = require('js-yaml');

class DevAssistant {
  constructor() {
    this.configPath = this.findConfigFile();
    this.config = this.loadConfig();
    this.anthropicApiKey = process.env.ANTHROPIC_API_KEY;
  }

  findConfigFile() {
    const possiblePaths = [
      '.dev-cheat.yaml',
      '.dev-cheat.yml',
      'dev-commands.yaml',
      'dev-commands.yml'
    ];
    
    for (const filePath of possiblePaths) {
      if (fs.existsSync(filePath)) {
        return filePath;
      }
    }
    
    throw new Error('No dev-commands.yaml file found in current directory');
  }

  loadConfig() {
    try {
      const fileContents = fs.readFileSync(this.configPath, 'utf8');
      return yaml.load(fileContents);
    } catch (error) {
      throw new Error(`Error loading config file: ${error.message}`);
    }
  }

  async executeCommand(command, args = []) {
    const fullCommand = [command, ...args].join(' ');
    
    // Check if it's a quick command first
    if (this.config.quick_commands && this.config.quick_commands[command]) {
      return this.executeQuickCommand(command);
    }
    
    // Check if it's an AI command
    if (this.config.ai_commands && this.config.ai_commands[command]) {
      return this.executeAICommand(command, args);
    }
    
    // Check if it's a workflow
    if (this.config.workflows && this.config.workflows[command]) {
      return this.executeWorkflow(command, args);
    }
    
    // Check custom vocabulary
    if (this.config.vocabulary && this.config.vocabulary[fullCommand]) {
      return this.executeAICommand('custom', [this.config.vocabulary[fullCommand]]);
    }

    // Default: send to AI for interpretation
    return this.executeAICommand('interpret', [fullCommand]);
  }

  executeQuickCommand(command) {
    const cmd = this.config.quick_commands[command];
    console.log(`🚀 Executing: ${cmd.description}`);
    
    try {
      cmd.actions.forEach(action => {
        console.log(`  → ${action}`);
        if (!action.startsWith('echo ')) {
          execSync(action, { stdio: 'inherit' });
        } else {
          console.log(action.replace('echo ', ''));
        }
      });
      console.log('✅ Command completed successfully!');
    } catch (error) {
      console.error('❌ Command failed:', error.message);
      process.exit(1);
    }
  }

  async executeAICommand(command, args) {
    if (!this.anthropicApiKey) {
      console.error('❌ ANTHROPIC_API_KEY environment variable not set');
      console.log('Please set your Claude API key: export ANTHROPIC_API_KEY=your_key_here');
      process.exit(1);
    }

    console.log('🤖 Processing with Claude AI...');
    
    const prompt = this.buildAIPrompt(command, args);
    
    try {
      const response = await this.callClaudeAPI(prompt);
      return this.executeAIResponse(response);
    } catch (error) {
      console.error('❌ AI command failed:', error.message);
      process.exit(1);
    }
  }

  buildAIPrompt(command, args) {
    const context = this.getProjectContext();
    const commandContext = this.getCommandContext(command, args);
    
    return `You are a development assistant for this project. Here's the context:

PROJECT CONTEXT:
${JSON.stringify(context, null, 2)}

COMMAND: ${command}
ARGS: ${args.join(' ')}

COMMAND CONTEXT:
${commandContext}

Based on the project context and command, provide executable actions. If you're generating code, make it production-ready and follow the specified standards.

Respond in this format:
ACTIONS:
- [list of shell commands to execute]

CODE:
[any code files to create/modify]

EXPLANATION:
[brief explanation of what you're doing]`;
  }

  getProjectContext() {
    return {
      project: this.config.project,
      standards: this.config.project?.standards,
      tools: this.config.project?.tools,
      currentDirectory: process.cwd(),
      files: this.getRelevantFiles()
    };
  }

  getRelevantFiles() {
    try {
      // Get basic project structure
      const files = execSync('find . -type f -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | head -20', 
        { encoding: 'utf8' }).trim().split('\n');
      return files.filter(f => f && !f.includes('node_modules'));
    } catch {
      return [];
    }
  }

  getCommandContext(command, args) {
    if (this.config.ai_commands && this.config.ai_commands[command]) {
      const cmdConfig = this.config.ai_commands[command];
      return `Template: ${cmdConfig.template}\nContext needed: ${cmdConfig.context_needed?.join(', ') || 'none'}`;
    }
    return `General command interpretation needed for: ${command} ${args.join(' ')}`;
  }

  async callClaudeAPI(prompt) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.anthropicApiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2000,
        messages: [{
          role: 'user',
          content: prompt
        }]
      })
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.content[0].text;
  }

  executeAIResponse(response) {
    console.log('📝 Claude Response:');
    console.log(response);
    
    // Parse actions from response
    const actionMatch = response.match(/ACTIONS:\s*([\s\S]*?)(?=CODE:|EXPLANATION:|$)/);
    if (actionMatch) {
      const actions = actionMatch[1].trim().split('\n')
        .filter(line => line.trim().startsWith('-'))
        .map(line => line.replace(/^-\s*/, '').trim());
      
      if (actions.length > 0) {
        console.log('\n🔧 Executing actions:');
        actions.forEach(action => {
          console.log(`  → ${action}`);
          try {
            execSync(action, { stdio: 'inherit' });
          } catch (error) {
            console.error(`    ❌ Failed: ${error.message}`);
          }
        });
      }
    }

    // Handle code generation
    const codeMatch = response.match(/CODE:\s*([\s\S]*?)(?=EXPLANATION:|$)/);
    if (codeMatch) {
      console.log('\n📄 Generated code:');
      console.log(codeMatch[1].trim());
    }
  }

  executeWorkflow(workflow, args) {
    const wf = this.config.workflows[workflow];
    console.log(`🔄 Starting workflow: ${wf.description}`);
    
    // For now, treat workflow steps as AI commands
    // In a full implementation, you'd handle each step type differently
    const stepsPrompt = `Execute this workflow: ${wf.steps.join(', ')}`;
    return this.executeAICommand('workflow', [stepsPrompt, ...args]);
  }

  showHelp() {
    console.log(`
🚀 Dev Assistant CLI

USAGE:
  dev <command> [args...]

QUICK COMMANDS:
${Object.entries(this.config.quick_commands || {})
  .map(([cmd, config]) => `  ${cmd.padEnd(15)} - ${config.description}`)
  .join('\n')}

AI COMMANDS:
${Object.entries(this.config.ai_commands || {})
  .map(([cmd, config]) => `  ${cmd.padEnd(15)} - ${config.description}`)
  .join('\n')}

WORKFLOWS:
${Object.entries(this.config.workflows || {})
  .map(([cmd, config]) => `  ${cmd.padEnd(15)} - ${config.description}`)
  .join('\n')}

EXAMPLES:
  dev build                    # Run production build
  dev create component Button  # Generate new component
  dev fix                      # Auto-fix linting issues
  dev analyze src/App.tsx      # Analyze specific file

Set ANTHROPIC_API_KEY environment variable for AI commands.
    `);
  }
}

// CLI Entry Point
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    try {
      const assistant = new DevAssistant();
      assistant.showHelp();
    } catch (error) {
      console.error('❌ Error:', error.message);
      console.log('\nCreate a .dev-commands.yaml file to get started!');
    }
    return;
  }

  try {
    const assistant = new DevAssistant();
    const [command, ...commandArgs] = args;
    await assistant.executeCommand(command, commandArgs);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = DevAssistant;
