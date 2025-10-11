#!/usr/bin/env python3
"""
AWS Infrastruct Launcher
Choose between CLI and GUI interfaces
"""

import sys
import os

def show_menu():
    print("=" * 75)
    print("🤖  AWS INFRASTRUCT LAUNCHER  🤖")
    print("=" * 75)
    print("Choose your interface:")
    print()
    print("1. 💬 Enhanced GUI Interface (Full Features)")
    print("   - Visual interface with tabs")
    print("   - Enhanced architecture diagrams with AWS icons")
    print("   - YAML template editor with proper tagging")
    print("   - Chat history with left panel")
    print("   - Nova-Act automated deployment")
    print("   - Requires: diagrams, PIL, sqlite3, nova-act")
    print()
    print("2. 🎯 Simple GUI Interface (No Dependencies)")
    print("   - Clean visual interface with tabs")
    print("   - Text-based architecture diagrams")
    print("   - YAML template editor")
    print("   - Manual deployment mode")
    print("   - Works with basic Python installation")
    print()
    print("3. 🚀 Enhanced CLI Interface")
    print("   - Enhanced command-line with visual diagrams")
    print("   - Proper CloudFormation tagging")
    print("   - Chat history and session management")
    print("   - Requires: diagrams, sqlite3")
    print()
    print("4. 🖥️  Classic CLI Interface")
    print("   - Original command-line conversation")
    print("   - Text-based interaction")
    print("   - No additional dependencies")
    print()
    print("5. 🔧 Install Nova-Act SDK")
    print("   - Install browser automation for deployment")
    print("   - Enables automated AWS Console deployment")
    print("   - Required for enhanced deployment features")
    print()
    print("6. 🧪 Test Nova-Act Installation")
    print("   - Verify Nova-Act SDK installation")
    print("   - Check deployment automation readiness")
    print()
    print("7. 🔑 Configure Nova-Act API Key")
    print("   - Set up API key for browser automation")
    print("   - Manage Nova-Act configuration")
    print()
    print("8. ❌ Exit")
    print("=" * 75)

def main():
    while True:
        show_menu()
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting Enhanced GUI Interface...")
                try:
                    import gui_main
                    gui_main.main()
                    break
                except ImportError as e:
                    print(f"❌ Error: Could not import Enhanced GUI module: {e}")
                    print("💡 Missing dependencies. Try option 2 (Simple GUI) or install requirements:")
                    print("   pip install diagrams PyYAML Pillow")
                    print("   Also install Graphviz: https://graphviz.org/download/")
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Error starting Enhanced GUI: {e}")
                    input("\nPress Enter to continue...")
            
            elif choice == "2":
                print("\n🚀 Starting Simple GUI Interface...")
                try:
                    import simple_gui
                    simple_gui.main()
                    break
                except Exception as e:
                    print(f"❌ Error starting Simple GUI: {e}")
                    input("\nPress Enter to continue...")
            
            elif choice == "3":
                print("\n🚀 Starting Enhanced CLI Interface...")
                try:
                    import enhanced_main
                    enhanced_main.main()
                    break
                except ImportError as e:
                    print(f"❌ Error: Could not import Enhanced CLI module: {e}")
                    print("💡 Missing dependencies. Try option 4 (Classic CLI) or install requirements:")
                    print("   pip install diagrams PyYAML")
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Error starting Enhanced CLI: {e}")
                    input("\nPress Enter to continue...")
            
            elif choice == "4":
                print("\n🚀 Starting Classic CLI Interface...")
                try:
                    import main
                    # The main.py file will handle its own execution
                    os.system(f"{sys.executable} main.py")
                    break
                except Exception as e:
                    print(f"❌ Error starting Classic CLI: {e}")
                    input("\nPress Enter to continue...")
            
            elif choice == "5":
                print("\n🔧 Installing Nova-Act SDK...")
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, "install_nova_act.py"], 
                                          capture_output=False, text=True)
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Error running installation script: {e}")
                    print("💡 Try running manually: python install_nova_act.py")
                    input("\nPress Enter to continue...")
            
            elif choice == "6":
                print("\n🧪 Testing Nova-Act Installation...")
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, "test_nova_act.py"], 
                                          capture_output=False, text=True)
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Error running test script: {e}")
                    print("💡 Try running manually: python test_nova_act.py")
                    input("\nPress Enter to continue...")
            
            elif choice == "7":
                print("\n🔑 Configuring Nova-Act API Key...")
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, "configure_nova_act.py"], 
                                          capture_output=False, text=True)
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Error running configuration script: {e}")
                    print("💡 Try running manually: python configure_nova_act.py")
                    input("\nPress Enter to continue...")
            
            elif choice == "8":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("\n❌ Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, or 8.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()