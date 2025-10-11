#!/usr/bin/env python3
"""
VS Code Nova-Act Launcher Script
Helps launch Nova-Act automation when automatic triggering fails
"""

import os
import subprocess
import sys
import glob
from pathlib import Path

def find_vscode():
    """Find VS Code installation"""
    vscode_paths = [
        "code",  # If in PATH
        "C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd",
        "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd", 
        "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd",
        "C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "C:\\Program Files\\Microsoft VS Code\\Code.exe",
        "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe"
    ]
    
    import getpass
    username = getpass.getuser()
    
    for path in vscode_paths:
        try:
            # Expand username placeholder
            if "{username}" in path:
                path = path.format(username=username)
            
            # Test if it's the 'code' command in PATH
            if path == "code":
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            # Test if it's a file path
            elif os.path.exists(path):
                return path
                
        except Exception:
            continue
    
    return None

def find_nova_act_instructions():
    """Find Nova-Act instruction files"""
    pattern = "nova_deploy_*.json"
    files = glob.glob(pattern)
    
    if not files:
        print("❌ No Nova-Act instruction files found")
        print(f"💡 Looking for files matching: {pattern}")
        return None
    
    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    return files

def launch_vscode_with_nova_act():
    """Launch VS Code with Nova-Act instructions"""
    print("🚀 VS Code Nova-Act Launcher")
    print("=" * 40)
    
    # Find VS Code
    print("🔍 Looking for VS Code installation...")
    vscode_path = find_vscode()
    
    if not vscode_path:
        print("❌ VS Code not found!")
        print("\n💡 Manual Steps:")
        print("1. Install VS Code from: https://code.visualstudio.com/")
        print("2. Add VS Code to your system PATH")
        print("3. Install Nova-Act extension in VS Code")
        print("4. Run this script again")
        return False
    
    print(f"✅ VS Code found: {vscode_path}")
    
    # Find instruction files
    print("\n🔍 Looking for Nova-Act instruction files...")
    instruction_files = find_nova_act_instructions()
    
    if not instruction_files:
        print("\n💡 To create instruction files:")
        print("1. Run the AWS Infrastruct GUI: python gui_main.py")
        print("2. Create infrastructure and click 'Deploy to AWS'")
        print("3. Instruction files will be generated automatically")
        return False
    
    print(f"✅ Found {len(instruction_files)} instruction file(s):")
    for i, file in enumerate(instruction_files, 1):
        mod_time = os.path.getmtime(file)
        print(f"   {i}. {file} (modified: {os.path.getctime(file)})")
    
    # Use the most recent file
    latest_file = instruction_files[0]
    print(f"\n🎯 Using latest file: {latest_file}")
    
    # Launch VS Code
    print(f"\n🚀 Launching VS Code with Nova-Act instructions...")
    try:
        if vscode_path == "code":
            subprocess.Popen([vscode_path, latest_file])
        else:
            subprocess.Popen([vscode_path, latest_file])
        
        print("✅ VS Code launched successfully!")
        print("\n📋 Next Steps in VS Code:")
        print("1. Press Ctrl+Shift+P to open Command Palette")
        print("2. Type: 'Nova-Act: Start Browser Automation'")
        print("3. Select the command and follow the prompts")
        print("4. Nova-Act will read the instruction file and automate deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch VS Code: {e}")
        print(f"\n🔧 Manual Launch:")
        print(f"1. Open VS Code manually")
        print(f"2. Open file: {latest_file}")
        print(f"3. Use Nova-Act extension to run the instructions")
        
        return False

def show_instruction_file_content():
    """Show the content of the latest instruction file"""
    instruction_files = find_nova_act_instructions()
    
    if not instruction_files:
        return
    
    latest_file = instruction_files[0]
    
    print(f"\n📄 Content of {latest_file}:")
    print("=" * 50)
    
    try:
        with open(latest_file, 'r') as f:
            import json
            data = json.load(f)
            
            print(f"Task: {data.get('task', 'N/A')}")
            print(f"Stack Name: {data.get('stack_name', 'N/A')}")
            print(f"Template URL: {data.get('template_url', 'N/A')}")
            
            if 'timeout_settings' in data:
                settings = data['timeout_settings']
                print(f"Login Timeout: {settings.get('login_timeout_minutes', 0)} minutes")
                print(f"Deployment Timeout: {settings.get('deployment_timeout_minutes', 15)} minutes")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main launcher function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--show-content":
        show_instruction_file_content()
        return
    
    success = launch_vscode_with_nova_act()
    
    if success:
        print("\n🎉 VS Code Nova-Act launcher completed successfully!")
    else:
        print("\n⚠️ Launcher encountered issues - see manual steps above")
        
        # Show instruction file content for manual use
        print("\n" + "=" * 50)
        show_instruction_file_content()

if __name__ == "__main__":
    main()