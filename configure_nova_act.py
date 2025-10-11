#!/usr/bin/env python3
"""
Nova-Act API Key Configuration Script
"""

import os
import re

def read_env_file():
    """Read the current .env file"""
    env_path = '.env'
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars, env_path

def write_env_file(env_vars, env_path):
    """Write the updated .env file"""
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def validate_api_key(api_key):
    """Validate the format of the API key"""
    if not api_key:
        return False, "API key cannot be empty"
    
    if len(api_key) < 10:
        return False, "API key seems too short"
    
    # Basic UUID format check (Nova-Act keys are typically UUIDs)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if re.match(uuid_pattern, api_key, re.IGNORECASE):
        return True, "Valid UUID format"
    
    # Allow other formats but warn
    return True, "API key format accepted (not standard UUID format)"

def configure_api_key():
    """Configure Nova-Act API key"""
    print("🔑 Nova-Act API Key Configuration")
    print("=" * 40)
    
    # Read current .env file
    env_vars, env_path = read_env_file()
    current_key = env_vars.get('NOVA_ACT_API_KEY', '')
    
    if current_key:
        print(f"📋 Current API key: {current_key[:8]}...{current_key[-4:]}")
        print("🔄 Do you want to update it? (y/n): ", end="")
        if input().lower() not in ['y', 'yes']:
            print("✅ Keeping current API key")
            return True
    else:
        print("❌ No Nova-Act API key found in .env file")
    
    print("\n📚 How to get your Nova-Act API key:")
    print("1. Go to AWS Console → Nova service")
    print("2. Navigate to API Keys section")
    print("3. Create a new API key")
    print("4. Copy the generated key")
    print()
    
    # Get new API key from user
    while True:
        print("🔑 Enter your Nova-Act API key: ", end="")
        new_key = input().strip()
        
        if not new_key:
            print("❌ API key cannot be empty. Please try again.")
            continue
        
        # Validate the key
        is_valid, message = validate_api_key(new_key)
        print(f"🔍 Validation: {message}")
        
        if is_valid:
            break
        else:
            print("❌ Invalid API key format. Please try again.")
    
    # Update .env file
    env_vars['NOVA_ACT_API_KEY'] = new_key
    
    try:
        write_env_file(env_vars, env_path)
        print(f"✅ API key saved to {env_path}")
        print(f"🔑 Key: {new_key[:8]}...{new_key[-4:]}")
        
        # Test the configuration
        print("\n🧪 Testing configuration...")
        test_configuration()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save API key: {e}")
        return False

def test_configuration():
    """Test the Nova-Act configuration"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('NOVA_ACT_API_KEY')
        if api_key:
            print(f"✅ API key loaded: {api_key[:8]}...{api_key[-4:]}")
            
            # Test Nova-Act import
            try:
                from nova_act import NovaAct
                print("✅ Nova-Act SDK available")
                print("🎉 Configuration test successful!")
                return True
            except ImportError:
                print("⚠️ Nova-Act SDK not installed")
                print("💡 Install with: pip install nova-act")
                return False
        else:
            print("❌ API key not found after configuration")
            return False
            
    except ImportError:
        print("⚠️ python-dotenv not available")
        print("💡 Install with: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def show_current_config():
    """Show current Nova-Act configuration"""
    print("📊 Current Nova-Act Configuration")
    print("=" * 35)
    
    # Check .env file
    env_vars, env_path = read_env_file()
    api_key = env_vars.get('NOVA_ACT_API_KEY', '')
    
    if api_key:
        print(f"✅ API Key: {api_key[:8]}...{api_key[-4:]}")
        print(f"📁 Location: {env_path}")
    else:
        print("❌ No API key configured")
        print(f"📁 .env file: {env_path}")
    
    # Check Nova-Act installation
    try:
        import nova_act
        print("✅ Nova-Act SDK: Installed")
        version = getattr(nova_act, '__version__', 'Unknown')
        print(f"📦 Version: {version}")
    except ImportError:
        print("❌ Nova-Act SDK: Not installed")
    
    # Check environment loading
    try:
        from dotenv import load_dotenv
        load_dotenv()
        env_key = os.getenv('NOVA_ACT_API_KEY')
        if env_key:
            print("✅ Environment: API key loaded successfully")
        else:
            print("❌ Environment: API key not loaded")
    except ImportError:
        print("⚠️ Environment: python-dotenv not available")

def main():
    """Main configuration function"""
    print("🤖 AWS Infrastruct - Nova-Act Configuration")
    print("=" * 45)
    print()
    
    while True:
        print("Choose an option:")
        print("1. 🔑 Configure API Key")
        print("2. 📊 Show Current Configuration")
        print("3. 🧪 Test Configuration")
        print("4. ❌ Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            print()
            configure_api_key()
        elif choice == "2":
            print()
            show_current_config()
        elif choice == "3":
            print()
            test_configuration()
        elif choice == "4":
            print("\n👋 Configuration complete!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        print("\n" + "-" * 45 + "\n")

if __name__ == "__main__":
    main()