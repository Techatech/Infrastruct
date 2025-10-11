# Nova-Act VS Code Extension Guide

## 🎉 Extension Successfully Installed!

The Nova-Act VS Code extension has been installed and is ready to automate your AWS deployments.

## 🚀 How to Use Nova-Act Extension

### Method 1: Automated via AWS Infrastruct Tool

1. **Run the AWS Infrastruct Tool** (GUI or CLI)
2. **Generate your infrastructure** (templates, diagrams, etc.)
3. **Click "Deploy"** - the tool will automatically:
   - Create Nova-Act instruction files
   - Provide VS Code commands to run
   - Guide you through the automation process

### Method 2: Manual Nova-Act Commands

1. **Open Command Palette**: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)

2. **Available Nova-Act Commands**:
   - `Nova-Act: Start Browser Automation` - Begin automated deployment
   - `Nova-Act: Stop Browser Automation` - Stop current automation
   - `Nova-Act: Show Output` - View automation logs
   - `Nova-Act: Configure Settings` - Adjust extension settings

3. **Follow the guided process** in VS Code's Nova-Act panel

## 📋 What Nova-Act Does

- **Opens AWS Console** automatically in your browser
- **Navigates to CloudFormation** service
- **Creates stacks** with your templates
- **Fills forms** and clicks buttons automatically
- **Monitors deployment** progress
- **Reports results** back to VS Code

## 🔧 Configuration

### Browser Setup (Recommended)
Nova-Act works best with Google Chrome. If you don't have Chrome installed:

1. **Download Chrome**: https://www.google.com/chrome/
2. **Install Chrome** and set it as your default browser
3. **Alternative**: Nova-Act can work with Edge or other Chromium browsers

### AWS Credentials
- Ensure you're logged into AWS Console in your browser
- Nova-Act will use your existing browser session
- No additional AWS credentials needed in VS Code

### Extension Settings
- Access via: `File > Preferences > Settings > Extensions > Nova-Act`
- Configure automation speed, timeouts, and behavior
- Set preferred browser if you have multiple installed

## 📊 Deployment Process

When you use the AWS Infrastruct tool's "Deploy" feature:

1. **Instruction File Created**: `nova_deploy_[stack-name].json`
2. **VS Code Command**: Run `Nova-Act: Start Browser Automation`
3. **Browser Opens**: AWS Console loads automatically
4. **Automation Runs**: Forms filled, buttons clicked
5. **Monitoring**: Real-time progress in VS Code
6. **Completion**: Success/failure reported

## 🆘 Troubleshooting

### Extension Not Working?
- Check VS Code Extensions panel
- Ensure Nova-Act extension is enabled
- Restart VS Code if needed

### Browser Issues?
- Ensure you're logged into AWS Console
- Check popup blockers aren't interfering
- Try different browser if needed

### Automation Stuck?
- Check VS Code Output panel → Nova-Act
- Stop automation and retry
- Fall back to manual deployment if needed

## 🔗 Next Steps

1. **Test the setup**: Try deploying a simple stack
2. **Monitor resources**: Check AWS Console after deployment
3. **Clean up**: Remember to delete test stacks to avoid charges
4. **Explore features**: Try different infrastructure templates

## 💡 Tips

- **Keep VS Code open** during deployments
- **Monitor the Output panel** for real-time updates
- **Use descriptive stack names** for easier management
- **Review generated templates** before deploying
- **Start with simple stacks** to test the automation

---

🎯 **Ready to deploy?** Run the AWS Infrastruct tool and click "Deploy" to see Nova-Act in action!