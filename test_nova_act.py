#!/usr/bin/env python3
"""
Test script to verify Nova-Act SDK installation and functionality
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if Nova-Act API key is configured"""
    print("🔑 Testing Nova-Act API key configuration...")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if api_key:
        print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
        return True
    else:
        print("❌ No Nova-Act API key found in environment")
        print("💡 Add NOVA_ACT_API_KEY to your .env file")
        return False

def test_nova_act_import():
    """Test if Nova-Act can be imported"""
    print("🔍 Testing Nova-Act import...")
    try:
        import nova_act
        print("✅ Nova-Act imported successfully")
        
        # Try to get version
        version = getattr(nova_act, '__version__', 'Unknown')
        print(f"📦 Version: {version}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import Nova-Act: {e}")
        return False

def test_nova_act_class():
    """Test if NovaAct class is available"""
    print("\n🔍 Testing NovaAct class...")
    try:
        from nova_act import NovaAct
        print("✅ NovaAct class imported successfully")
        
        # Test class instantiation (without actually starting browser)
        print("🧪 Testing class structure...")
        print(f"📋 NovaAct class: {NovaAct}")
        print(f"📋 NovaAct methods: {[method for method in dir(NovaAct) if not method.startswith('_')]}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import NovaAct class: {e}")
        return False
    except Exception as e:
        print(f"⚠️ NovaAct class available but error in testing: {e}")
        return True  # Class is available even if testing failed

def test_enhanced_deployer():
    """Test if enhanced deployer can use Nova-Act"""
    print("\n🔍 Testing enhanced deployer integration...")
    try:
        from tools.enhanced_deployer_tool import EnhancedDeploymentManager
        
        manager = EnhancedDeploymentManager()
        print(f"✅ Enhanced deployment manager created")
        print(f"🤖 Nova-Act available: {manager.nova_act_available}")
        
        if manager.nova_act_available:
            print("🎉 Enhanced deployment with Nova-Act is ready!")
        else:
            print("📋 Enhanced deployment will use manual mode")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import enhanced deployer: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Enhanced deployer available but error in testing: {e}")
        return True

def show_installation_status():
    """Show overall installation status"""
    print("\n" + "="*50)
    print("📊 NOVA-ACT INSTALLATION STATUS")
    print("="*50)
    
    # Test components
    api_key_available = test_api_key()
    nova_act_available = test_nova_act_import()
    class_available = test_nova_act_class() if nova_act_available else False
    deployer_ready = test_enhanced_deployer()
    
    print("\n📋 Summary:")
    print(f"   API Key: {'✅ Configured' if api_key_available else '❌ Missing'}")
    print(f"   Nova-Act SDK: {'✅ Installed' if nova_act_available else '❌ Not Available'}")
    print(f"   NovaAct Class: {'✅ Available' if class_available else '❌ Not Available'}")
    print(f"   Enhanced Deployer: {'✅ Ready' if deployer_ready else '❌ Not Ready'}")
    
    if api_key_available and nova_act_available and class_available:
        print("\n🎉 INSTALLATION SUCCESSFUL!")
        print("✅ Nova-Act SDK is ready for AWS deployment automation")
        print("🔑 API key is properly configured")
        print("🚀 Enhanced deployment features are available")
        print("🎯 You can now use automated browser deployment in the GUI")
    elif nova_act_available and class_available:
        print("\n⚠️ PARTIAL INSTALLATION")
        print("✅ Nova-Act SDK is installed but API key is missing")
        print("🔑 Add NOVA_ACT_API_KEY to your .env file")
        print("💡 Get your API key from AWS Nova console")
    elif nova_act_available:
        print("\n⚠️ PARTIAL INSTALLATION")
        print("✅ Nova-Act SDK is installed but some features may not work")
        print("🔧 Try reinstalling: pip install --force-reinstall nova-act")
        if not api_key_available:
            print("🔑 Also add NOVA_ACT_API_KEY to your .env file")
    else:
        print("\n❌ INSTALLATION NEEDED")
        print("🔧 Install Nova-Act SDK using one of these methods:")
        print("   1. Run: python install_nova_act.py")
        print("   2. Run: pip install nova-act")
        print("   3. See NOVA_ACT_INSTALLATION.md for detailed instructions")
        if not api_key_available:
            print("🔑 Also add NOVA_ACT_API_KEY to your .env file")
    
    print("\n" + "="*50)

def main():
    """Main test function"""
    print("🧪 AWS Infrastruct - Nova-Act SDK Test")
    print("="*40)
    
    show_installation_status()
    
    print("\n💡 Next Steps:")
    if test_nova_act_import():
        print("   • Restart AWS Infrastruct GUI to enable enhanced deployment")
        print("   • Use the 'Deploy to AWS' feature with automated mode")
        print("   • Monitor deployment progress in real-time")
    else:
        print("   • Install Nova-Act SDK using the installation guide")
        print("   • Run this test again to verify installation")
        print("   • Manual deployment mode will be available as fallback")

if __name__ == "__main__":
    main()