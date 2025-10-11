#!/usr/bin/env python3
"""
Test Direct Nova-Act Automation
Demonstrates browser automation directly from Python app
"""

from direct_nova_act_automation import deploy_with_direct_automation, check_deployment_status_direct
import time

def test_direct_automation():
    """Test direct Nova-Act automation"""
    print("🧪 Testing Direct Nova-Act Browser Automation")
    print("=" * 60)
    
    # Test deployment
    template_url = "https://infrastruct.s3.us-east-1.amazonaws.com/test-template.yaml"
    stack_name = "direct-automation-test"
    
    print(f"📋 Stack Name: {stack_name}")
    print(f"🌐 Template URL: {template_url}")
    print(f"🤖 Starting direct browser automation...")
    print()
    
    def progress_callback(message):
        print(f"   {message}")
    
    try:
        # Run direct automation
        result = deploy_with_direct_automation(template_url, stack_name, progress_callback)
        
        print("\n" + "=" * 60)
        print("📊 AUTOMATION RESULT:")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            print(f"Details: {result.get('details', 'N/A')}")
            
            # Test status checking
            print("\n🔍 Testing status check...")
            status_result = check_deployment_status_direct(stack_name)
            print(f"Status Check Success: {status_result['success']}")
            if status_result['success']:
                print(f"Status Info: {status_result['status_info']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Fallback: {result.get('fallback', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🎯 DIRECT AUTOMATION BENEFITS:")
        print("✅ No manual VS Code steps required")
        print("✅ Real-time progress updates in your app")
        print("✅ Programmatic control over deployment")
        print("✅ Error handling and status monitoring")
        print("✅ Seamless integration with your GUI")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def demo_gui_integration():
    """Demonstrate GUI integration"""
    print("\n🖥️ GUI Integration Demo")
    print("=" * 30)
    
    try:
        from gui_direct_automation import create_direct_automation_window
        
        print("✅ Direct automation GUI available")
        print("🚀 To test GUI integration:")
        print("   python gui_direct_automation.py")
        
        # Optionally launch the GUI
        import sys
        if "--gui" in sys.argv:
            print("🖥️ Launching direct automation GUI...")
            root, gui = create_direct_automation_window()
            root.mainloop()
            
    except ImportError as e:
        print(f"⚠️ GUI integration not available: {e}")

if __name__ == "__main__":
    test_direct_automation()
    demo_gui_integration()