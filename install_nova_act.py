#!/usr/bin/env python3
"""
Nova-Act SDK Installation Script for AWS Infrastruct
"""

import subprocess
import sys
import os

def check_nova_act_installed():
    """Check if Nova-Act is already installed"""
    try:
        import nova_act
        print("✅ Nova-Act SDK is already installed")
        print(f"   Version: {getattr(nova_act, '__version__', 'Unknown')}")
        return True
    except ImportError:
        print("❌ Nova-Act SDK is not installed")
        return False

def install_nova_act():
    """Install Nova-Act SDK"""
    print("🚀 Installing Nova-Act SDK...")
    
    try:
        # Try installing nova-act
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "nova-act"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Nova-Act SDK installed successfully!")
        print("📦 Installation output:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install Nova-Act SDK")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        
        # Provide alternative installation methods
        print("\n🔄 Alternative installation methods:")
        print("1. Try installing from source:")
        print("   pip install git+https://github.com/aws/nova-act.git")
        print("\n2. Install with specific Python version:")
        print(f"   {sys.executable} -m pip install nova-act")
        print("\n3. Install in development mode:")
        print("   pip install --user nova-act")
        print("\n4. Check if you need to update pip:")
        print("   python -m pip install --upgrade pip")
        
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_installation():
    """Verify Nova-Act installation and show usage info"""
    try:
        import nova_act
        from nova_act import NovaAct
        
        print("✅ Nova-Act SDK verification successful!")
        print("🎯 Available components:")
        print("   - NovaAct browser automation class")
        print("   - Browser control capabilities")
        print("   - AWS Console automation support")
        
        # Check API key configuration
        print("\n🔑 Checking API key configuration...")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('NOVA_ACT_API_KEY')
            
            if api_key:
                print(f"✅ API key configured: {api_key[:8]}...{api_key[-4:]}")
            else:
                print("⚠️ API key not found in .env file")
                print("💡 Add NOVA_ACT_API_KEY=your-api-key to .env file")
                
        except ImportError:
            print("⚠️ python-dotenv not available, cannot check .env file")
            print("💡 Install with: pip install python-dotenv")
        
        print("\n📚 Usage example:")
        print("""
import os
from nova_act import NovaAct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('NOVA_ACT_API_KEY')

# Use Nova-Act with API key
with NovaAct(starting_page="https://console.aws.amazon.com", api_key=api_key) as browser:
    result = browser.act("Navigate to CloudFormation and create a stack")
    print(result.response)
""")
        
        return True
        
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        print("🔧 The installation may not have completed successfully")
        return False
    
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def show_manual_installation():
    """Show manual installation instructions"""
    print("\n" + "="*60)
    print("📋 MANUAL INSTALLATION INSTRUCTIONS")
    print("="*60)
    print("\nIf the automatic installation fails, try these steps:")
    print("\n1. 🔧 Update pip first:")
    print("   python -m pip install --upgrade pip")
    print("\n2. 🚀 Install Nova-Act SDK:")
    print("   pip install nova-act")
    print("\n3. 🔍 Alternative installation methods:")
    print("   # From GitHub (if PyPI version has issues)")
    print("   pip install git+https://github.com/aws/nova-act.git")
    print("\n   # With user flag (if permissions issues)")
    print("   pip install --user nova-act")
    print("\n   # Force reinstall")
    print("   pip install --force-reinstall nova-act")
    print("\n4. ✅ Verify installation:")
    print("   python -c \"import nova_act; print('Nova-Act installed successfully!')\"")
    print("\n5. 🔑 Configure API key in .env file:")
    print("   Add: NOVA_ACT_API_KEY=your-api-key-here")
    print("   Get your API key from AWS Nova console")
    print("\n6. 🧪 Test complete setup:")
    print("   python test_nova_act.py")
    print("\n7. 🔧 If you encounter build errors:")
    print("   - On Windows: Install Visual Studio Build Tools")
    print("   - On macOS: Install Xcode Command Line Tools")
    print("   - On Linux: Install build-essential package")
    print("\n8. 🌐 For more help, visit:")
    print("   - Nova-Act Documentation: https://docs.aws.amazon.com/nova/")
    print("   - AWS SDK Documentation: https://aws.amazon.com/sdk/")
    print("   - Get API Key: AWS Nova Console → API Keys")

def main():
    """Main installation process"""
    print("🤖 AWS Infrastruct - Nova-Act SDK Installation")
    print("="*50)
    
    # Check current installation
    if check_nova_act_installed():
        print("\n🎉 Nova-Act is ready to use!")
        verify_installation()
        return
    
    # Attempt installation
    print("\n🚀 Starting Nova-Act SDK installation...")
    success = install_nova_act()
    
    if success:
        print("\n🔍 Verifying installation...")
        if verify_installation():
            print("\n🎉 Installation completed successfully!")
            print("✅ Nova-Act SDK is ready for AWS deployment automation")
        else:
            print("\n⚠️ Installation completed but verification failed")
            show_manual_installation()
    else:
        print("\n❌ Automatic installation failed")
        show_manual_installation()
    
    print("\n" + "="*50)
    print("🔄 After installation, restart your application to use Nova-Act")
    print("🚀 Enhanced deployment features will be available in the GUI")

if __name__ == "__main__":
    main()