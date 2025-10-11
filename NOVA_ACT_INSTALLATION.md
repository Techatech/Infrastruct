# Nova-Act SDK Installation Guide

## 🚀 Quick Installation

### Option 1: Automatic Installation Script
```bash
python install_nova_act.py
```

### Option 2: Windows Batch Script
```cmd
install_nova_act.bat
```

### Option 3: Manual Installation
```bash
pip install nova-act
```

### ⚠️ Important: API Key Configuration
After installation, you must configure your Nova-Act API key in the `.env` file:
```
NOVA_ACT_API_KEY=your-api-key-here
```

## 📋 Detailed Installation Steps

### 1. **Prerequisites**
- Python 3.8 or higher
- pip (Python package installer)
- Internet connection

### 2. **Check Current Installation**
```python
python -c "import nova_act; print('Nova-Act is installed!')"
```

### 3. **Installation Methods**

#### **Method A: Standard Installation**
```bash
# Update pip first
python -m pip install --upgrade pip

# Install Nova-Act
pip install nova-act
```

#### **Method B: User Installation (if permissions issues)**
```bash
pip install --user nova-act
```

#### **Method C: From Source (if PyPI issues)**
```bash
pip install git+https://github.com/aws/nova-act.git
```

#### **Method D: Force Reinstall**
```bash
pip install --force-reinstall nova-act
```

### 4. **API Key Configuration**

#### **Getting Your Nova-Act API Key**
1. **AWS Console**: Go to AWS Nova service console
2. **API Keys**: Navigate to API Keys section
3. **Create Key**: Generate a new API key for your project
4. **Copy Key**: Save the API key securely

#### **Adding API Key to Environment**
Add the following line to your `.env` file:
```env
NOVA_ACT_API_KEY=your-actual-api-key-here
```

#### **Verifying API Key**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('NOVA_ACT_API_KEY')[:8] + '...' if os.getenv('NOVA_ACT_API_KEY') else 'Not found')"
```

#### **Security Best Practices**
- ✅ **Never commit** API keys to version control
- ✅ **Use environment variables** for API key storage
- ✅ **Rotate keys regularly** for security
- ✅ **Limit key permissions** to minimum required
- ❌ **Never hardcode** API keys in source code

### 5. **Platform-Specific Instructions**

#### **Windows**
```cmd
# Run as Administrator if needed
python -m pip install nova-act

# If build errors occur, install Visual Studio Build Tools:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### **macOS**
```bash
# Install Xcode Command Line Tools if needed
xcode-select --install

# Then install Nova-Act
pip install nova-act
```

#### **Linux (Ubuntu/Debian)**
```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Install Nova-Act
pip install nova-act
```

#### **Linux (CentOS/RHEL)**
```bash
# Install build dependencies
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# Install Nova-Act
pip install nova-act
```

## 🔧 Troubleshooting

### **Common Issues & Solutions**

#### **Issue 1: "No module named 'nova_act'"**
```bash
# Solution: Ensure installation completed successfully
pip install nova-act
python -c "import nova_act; print('Success!')"
```

#### **Issue 2: Build/Compilation Errors**
```bash
# Windows: Install Visual Studio Build Tools
# macOS: Install Xcode Command Line Tools
# Linux: Install build-essential or Development Tools

# Then retry installation
pip install nova-act
```

#### **Issue 3: Permission Denied**
```bash
# Use user installation
pip install --user nova-act

# Or run with elevated privileges (Windows)
# Run Command Prompt as Administrator
```

#### **Issue 4: Network/Proxy Issues**
```bash
# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org nova-act

# Or configure proxy
pip install --proxy http://proxy.server:port nova-act
```

#### **Issue 5: Version Conflicts**
```bash
# Create virtual environment
python -m venv nova_env
source nova_env/bin/activate  # Linux/macOS
# or
nova_env\Scripts\activate  # Windows

pip install nova-act
```

### **Verification Steps**

#### **1. Basic Import Test**
```python
try:
    import nova_act
    print("✅ Nova-Act imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
```

#### **2. Version Check**
```python
import nova_act
print(f"Nova-Act version: {getattr(nova_act, '__version__', 'Unknown')}")
```

#### **3. Functionality Test**
```python
from nova_act import NovaAct
print("✅ NovaAct class available")
```

## 🎯 Integration with AWS Infrastruct

### **After Installation**
1. **Restart the application** to detect Nova-Act
2. **Enhanced deployment features** will be automatically enabled
3. **Automated browser deployment** will be available in the GUI
4. **Manual fallback** remains available if needed

### **Usage in AWS Infrastruct**
- **GUI Mode**: Enhanced deployment tab with automation options
- **CLI Mode**: Automated deployment commands
- **Fallback**: Manual deployment instructions if Nova-Act unavailable

### **Features Enabled**
- ✅ **Automated AWS Console navigation**
- ✅ **CloudFormation stack creation**
- ✅ **Template deployment automation**
- ✅ **Status monitoring and reporting**
- ✅ **Error handling and recovery**

## 📚 Additional Resources

### **Documentation**
- [Nova-Act SDK Documentation](https://docs.aws.amazon.com/nova/)
- [AWS SDK Documentation](https://aws.amazon.com/sdk/)
- [CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)

### **Support**
- [AWS Support](https://aws.amazon.com/support/)
- [Nova-Act GitHub Issues](https://github.com/aws/nova-act/issues)
- [AWS Developer Forums](https://forums.aws.amazon.com/)

### **Examples**
```python
# Basic Nova-Act usage
from nova_act import NovaAct

with NovaAct(starting_page="https://console.aws.amazon.com") as browser:
    result = browser.act("Navigate to CloudFormation")
    print(result.response)
```

## ⚠️ Important Notes

1. **AWS Credentials**: Ensure AWS credentials are configured
2. **Browser Requirements**: Nova-Act may require specific browser versions
3. **Network Access**: Requires internet access to AWS Console
4. **Security**: Always sign out of AWS Console after deployment
5. **Monitoring**: Monitor AWS costs and resource usage

## 🔄 Update Instructions

### **Updating Nova-Act**
```bash
# Update to latest version
pip install --upgrade nova-act

# Force reinstall if needed
pip install --force-reinstall nova-act
```

### **Checking for Updates**
```bash
# Check current version
pip show nova-act

# Check available versions
pip index versions nova-act
```