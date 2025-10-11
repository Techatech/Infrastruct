#  AWS Infrastruct

A comprehensive AWS infrastructure management tool with both GUI and CLI interfaces, featuring enhanced diagramming, proper CloudFormation tagging, and persistent chat history.

## 🚀  Features

### 🎨 Visual Architecture Diagrams
- **Real AWS Icons**: Uses the `diagrams` library with actual AWS service icons
- **Automatic Layout**: Intelligent component placement and relationships
- **Export Options**: Save diagrams as PNG files
- **Fallback Support**: Text-based diagrams when visual generation fails

### 🏷️ CloudFormation Tagging
- **Standardized Naming**: `{envid}-ResourceType-InstanceNumber` format
- **Environment Tags**: Consistent environment identification
- **Metadata Tags**: CreatedBy, CreatedDate, ManagedBy
- **Customizable Environment ID**: Set your own environment identifier

### 📚 Persistent Chat History
- **SQLite Database**: All conversations automatically saved
- **Cross-Platform**: Works with both GUI and CLI interfaces
- **Session Management**: Load previous conversations
- **Search Functionality**: Find past sessions by content
- **Session Restoration**: Resume work from where you left off

### 🎯 Multi-Interface Support
- **Enhanced GUI**: Visual interface with chat history panel
- **Enhanced CLI**: Command-line with full feature parity
- **Classic CLI**: Original experience for compatibility

## Features

### 🎯 Multi-Tab Interface (GUI)
- **Chat Assistant**: Interactive conversation with chat history panel
- **Architecture Plan**: View detailed infrastructure plans and cost estimates
- **Architecture Diagram**: Visual representation with actual AWS icons
- **YAML Template**: Enhanced CloudFormation templates with proper tagging
- **Deployment**: Deploy your infrastructure to AWS

### 🚀 Key Capabilities
- Real-time chat with AWS architecture assistant
- Enhanced visual architecture diagram generation
- YAML template editing with standardized tagging
- Cost estimation integration with formatted tables
- One-click deployment to AWS
- Persistent chat history across sessions
- Save/load templates and plans
- Progress tracking for deployments

## Installation

1. Install the enhanced requirements:
```bash
pip install -r requirements_gui.txt
```

2. Install Graphviz (required for diagrams library):
   - **Windows**: Download from https://graphviz.org/download/
   - **macOS**: `brew install graphviz`
   - **Linux**: `sudo apt-get install graphviz` or `sudo yum install graphviz`

3. Make sure your `.env` file is configured with AWS credentials

## Usage

### Option 1: Use the Launcher (Recommended)
```bash
python launcher.py
```
Choose from:
- **Option 1**: Enhanced GUI Interface (recommended)
- **Option 2**: Enhanced CLI Interface (new)
- **Option 3**: Classic CLI Interface (original)

### Option 2: Direct Launch
```bash
# Enhanced GUI
python gui_main.py

# Enhanced CLI
python enhanced_main.py

# Classic CLI
python main.py
```

## Enhanced Tagging Convention

All CloudFormation resources follow this standardized tagging:

### 1. Name Tag
- **Format**: `{envid}-ResourceType-InstanceNumber`
- **Examples**: 
  - `dev-Server01` (first EC2 instance)
  - `prod-Database02` (second RDS instance)

### 2. Environment Tag
- **Format**: `{envid}`
- **Examples**: `dev`, `staging`, `prod`

### 3. Management Tags
- **CreatedBy**: `Infrastruct`
- **CreatedDate**: Current date
- **ManagedBy**: `CloudFormation`

### Setting Environment ID
- **GUI**: Use the Environment ID field in the chat tab
- **Enhanced CLI**: Use command `envid <environment>`
- **Default**: `dev`

## GUI Overview

### Chat Tab 💬
- Main interaction point with the AI assistant
- Quick action buttons for common tasks
- Real-time conversation history
- Support for natural language queries like:
  - "I need a static website for my portfolio"
  - "Create a scalable web application architecture"
  - "I want to build a data processing pipeline"

### Architecture Plan Tab 📋
- Displays detailed infrastructure plans
- Shows cost estimates when available
- Options to generate templates or get estimates
- Save plans to files for later reference

### Architecture Diagram Tab 🏗️
- Visual representation of your infrastructure
- Component relationships and data flow
- Recommendations for diagramming tools
- Export diagram descriptions

### YAML Template Tab 📄
- Full Infrastructure as Code template display
- YAML syntax validation
- Save/load template files
- Template generation from plans

### Deployment Tab 🚀
- Deploy infrastructure to your AWS account
- Real-time deployment progress
- Stack name configuration
- Deployment status and logs

## Quick Start Guide

1. **Start a Conversation**: Go to the Chat tab and describe what you want to build
2. **Review the Plan**: Check the Architecture Plan tab for detailed specifications
3. **View the Diagram**: See the visual representation in the Architecture Diagram tab
4. **Generate Template**: Create the YAML template in the YAML Template tab
5. **Deploy**: Use the Deployment tab to deploy to AWS

## Tips

- Use natural language to describe your infrastructure needs
- The GUI automatically updates related tabs when you complete actions
- Save your plans and templates for future reference
- Validate YAML templates before deployment
- Monitor deployment progress in real-time

## Troubleshooting

### GUI Won't Start
- Ensure all requirements are installed: `pip install -r requirements_gui.txt`
- Check that your Python version supports tkinter (usually built-in)

### Agent Not Responding
- Verify your `.env` file has correct AWS credentials
- Check your internet connection
- Ensure the Bedrock model is accessible in your AWS region

### Template Validation Fails
- Install PyYAML if not already installed: `pip install PyYAML`
- Check YAML syntax for common errors (indentation, colons, etc.)

## Comparison with CLI

| Feature | CLI | GUI |
|---------|-----|-----|
| Interaction | Text-based conversation | Visual tabs + chat |
| Architecture Plans | Text output | Dedicated plan viewer |
| Diagrams | Text description | Visual display area |
| Templates | Text output | Code editor-like view |
| Deployment | Text progress | Visual progress bar |
| File Management | Manual | Built-in save/load |
| Multi-tasking | Sequential | Tab-based workflow |

The GUI provides a more visual and organized experience while maintaining all the powerful features of the CLI version.