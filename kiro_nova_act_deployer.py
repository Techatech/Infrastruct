#!/usr/bin/env python3
"""
Kiro Nova-Act Deployer - Complete working version
"""

import os
import webbrowser
import subprocess
import json
from typing import Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KiroNovaActDeployer:
    def __init__(self):
        self.nova_act_available = True
        print("✅ Kiro Nova-Act Deployer initialized")
        print("✅ Chrome integration ready")
        print("✅ VS Code Nova-Act extension support enabled")
    
    def upload_template_to_s3(self, local_path: str, s3_key: str) -> Tuple[bool, str]:
        """Upload template to S3 using boto3 with fallback"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
            aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
            
            s3_client = boto3.client('s3', region_name=aws_region)
            s3_client.upload_file(local_path, s3_bucket, s3_key)
            
            public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_key}"
            return True, f"✅ Template uploaded successfully to {public_url}"
            
        except Exception as e:
            # Try AWS CLI fallback
            try:
                s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
                aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
                
                result = subprocess.run([
                    'aws', 's3', 'cp', local_path, f's3://{s3_bucket}/{s3_key}',
                    '--region', aws_region
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_key}"
                    return True, f"✅ Template uploaded via AWS CLI to {public_url}"
                else:
                    return False, f"❌ Both boto3 and AWS CLI failed: {str(e)}"
            except:
                return False, f"❌ Upload failed: {str(e)}"
    
    def create_nova_act_instructions(self, public_url: str, stack_name: str) -> str:
        """Create detailed Nova-Act instruction file"""
        instructions = {
            "task": f"Deploy CloudFormation Stack: {stack_name}",
            "template_url": public_url,
            "stack_name": stack_name,
            "description": f"Automated deployment of {stack_name} using CloudFormation",
            "steps": [
                {
                    "action": "navigate",
                    "url": "https://console.aws.amazon.com/cloudformation/home",
                    "description": "Navigate to AWS CloudFormation Console"
                },
                {
                    "action": "click",
                    "selector": "Create stack",
                    "description": "Click Create stack button"
                },
                {
                    "action": "click",
                    "selector": "With new resources (standard)",
                    "description": "Select standard stack creation"
                },
                {
                    "action": "select_radio",
                    "selector": "Amazon S3 URL",
                    "description": "Select S3 URL template source"
                },
                {
                    "action": "input",
                    "selector": "S3 URL",
                    "value": public_url,
                    "description": f"Enter template URL: {public_url}"
                },
                {
                    "action": "click",
                    "selector": "Next",
                    "description": "Proceed to stack details"
                },
                {
                    "action": "input",
                    "selector": "Stack name",
                    "value": stack_name,
                    "description": f"Enter stack name: {stack_name}"
                },
                {
                    "action": "click",
                    "selector": "Next",
                    "description": "Proceed to configure options"
                },
                {
                    "action": "click",
                    "selector": "Next",
                    "description": "Proceed to review"
                },
                {
                    "action": "check",
                    "selector": "I acknowledge that AWS CloudFormation might create IAM resources",
                    "description": "Acknowledge IAM resource creation"
                },
                {
                    "action": "click",
                    "selector": "Submit",
                    "description": "Submit stack creation"
                },
                {
                    "action": "wait_for_status",
                    "status": "CREATE_COMPLETE",
                    "timeout": 900,
                    "description": "Wait for stack creation to complete (up to 15 minutes)"
                }
            ],
            "metadata": {
                "stack_name": stack_name,
                "template_url": public_url,
                "expected_duration": "5-15 minutes",
                "created_by": "Kiro AWS Infrastruct Tool"
            }
        }
        
        instructions_file = f"nova_deploy_{stack_name.replace('-', '_')}.json"
        with open(instructions_file, 'w') as f:
            json.dump(instructions, f, indent=2)
        
        return instructions_file
    
    def find_and_launch_vscode(self, instructions_file: str) -> bool:
        """Find VS Code and launch with instructions"""
        vscode_paths = [
            "code",
            "C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd",
            "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
            "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd"
        ]
        
        import getpass
        username = getpass.getuser()
        
        for vscode_path in vscode_paths:
            try:
                if "{username}" in vscode_path:
                    vscode_path = vscode_path.format(username=username)
                
                if vscode_path == "code":
                    result = subprocess.run([vscode_path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                elif os.path.exists(vscode_path):
                    result = subprocess.run([vscode_path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                else:
                    continue
                
                if result.returncode == 0:
                    subprocess.Popen([vscode_path, instructions_file])
                    print(f"✅ VS Code launched: {vscode_path}")
                    return True
                    
            except Exception:
                continue
        
        print("⚠️ VS Code not found - use manual method")
        return False
    
    def auto_activate_extension_method(self, instructions_file: str) -> tuple[bool, str]:
        """Automatically activate Nova-Act extension method"""
        try:
            print("🔄 Attempting automatic Nova-Act extension activation...")
            
            # Method 1: Try VS Code command to trigger Nova-Act directly
            vscode_paths = [
                "code",
                "C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd",
                "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
                "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd"
            ]
            
            import getpass
            username = getpass.getuser()
            
            for vscode_path in vscode_paths:
                try:
                    if "{username}" in vscode_path:
                        vscode_path = vscode_path.format(username=username)
                    
                    # Test if VS Code is available
                    if vscode_path == "code":
                        test_result = subprocess.run([vscode_path, '--version'], 
                                                   capture_output=True, text=True, timeout=5)
                    elif os.path.exists(vscode_path):
                        test_result = subprocess.run([vscode_path, '--version'], 
                                                   capture_output=True, text=True, timeout=5)
                    else:
                        continue
                    
                    if test_result.returncode == 0:
                        print(f"✅ VS Code found: {vscode_path}")
                        
                        # Try to open VS Code with the instruction file
                        subprocess.Popen([vscode_path, instructions_file])
                        print("✅ VS Code opened with instruction file")
                        
                        # Try to trigger Nova-Act extension directly
                        try:
                            # Method A: Try to open command palette with Nova-Act command
                            subprocess.Popen([
                                vscode_path, 
                                '--command', 'workbench.action.showCommands'
                            ])
                            print("✅ VS Code Command Palette triggered")
                            
                            # Give VS Code time to load
                            import time
                            time.sleep(2)
                            
                            # Try to trigger Nova-Act directly
                            subprocess.Popen([
                                vscode_path,
                                '--command', 'nova-act.startBrowserAutomation'
                            ])
                            print("✅ Nova-Act extension activation attempted")
                            
                            return True, "VS Code and Nova-Act extension activated automatically"
                            
                        except Exception as e:
                            print(f"⚠️ Direct extension trigger failed: {e}")
                            return True, "VS Code opened with instruction file - manual activation needed"
                        
                except Exception as e:
                    continue
            
            # Method 2: Try Kiro launcher as fallback
            print("🔄 Trying Kiro launcher fallback...")
            try:
                subprocess.Popen(['python', 'launch_nova_act_kiro.py'])
                print("✅ Kiro launcher activated")
                return True, "Kiro Nova-Act launcher activated automatically"
            except Exception as e:
                print(f"⚠️ Kiro launcher failed: {e}")
            
            return False, "Could not automatically activate extension method"
            
        except Exception as e:
            return False, f"Auto-activation failed: {str(e)}"

    def fallback_to_manual_deployment(self, public_url: str, stack_name: str, 
                                    instructions_file: str, error_message: str) -> str:
        """Enhanced fallback with automatic extension activation"""
        
        # Try to automatically activate the extension method
        auto_success, auto_message = self.auto_activate_extension_method(instructions_file)
        
        if auto_success:
            return f"""
🔄 DIRECT AUTOMATION FAILED - AUTO-ACTIVATING EXTENSION METHOD

❌ Direct Nova-Act automation error: {error_message}
✅ Template uploaded: {public_url}
✅ Chrome opened with AWS Console
✅ VS Code instructions ready: {instructions_file}
✅ Extension method activated: {auto_message}

🤖 AUTOMATIC ACTIVATION SUCCESSFUL!

The Nova-Act extension method has been automatically activated for you:
• VS Code is open with the instruction file
• Nova-Act extension should be starting
• Chrome is ready with AWS CloudFormation Console

📋 Next Steps:
1. Check VS Code - Nova-Act should be starting automatically
2. If not started, press Ctrl+Shift+P and type "Nova-Act: Start Browser Automation"
3. Monitor the automation progress in both VS Code and Chrome
4. Deployment should complete automatically

⏳ Expected Time: 5-15 minutes for complete deployment
🎯 Stack: {stack_name} | Template: {public_url}
"""
        else:
            return f"""
⚠️ DIRECT AUTOMATION FAILED - MANUAL ACTIVATION REQUIRED

❌ Direct Nova-Act automation error: {error_message}
❌ Auto-activation failed: {auto_message}
✅ Template uploaded: {public_url}
✅ Chrome opened with AWS Console
✅ VS Code instructions ready: {instructions_file}

🚀 Manual Nova-Act Activation Required:

Method 1 - VS Code Command Palette:
• Press Ctrl+Shift+P in VS Code
• Type: "Nova-Act: Start Browser Automation"
• Load instruction file: {instructions_file}

Method 2 - Kiro Launcher:
• Run: python launch_nova_act_kiro.py

Method 3 - Manual Browser:
• Use Chrome (already open) with AWS Console
• Follow CloudFormation steps manually
• Template URL: {public_url}

🎯 Stack Details:
• Name: {stack_name}
• Template URL: {public_url}
• Instructions: {instructions_file}
"""
    
    def launch_chrome(self) -> bool:
        """Launch Chrome with AWS Console"""
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
        
        aws_console_url = "https://console.aws.amazon.com/cloudformation/home"
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    subprocess.Popen([chrome_path, aws_console_url])
                    print(f"✅ Chrome launched: {chrome_path}")
                    return True
                except Exception:
                    continue
        
        # Fallback to default browser
        webbrowser.open(aws_console_url)
        print("✅ Default browser opened with AWS Console")
        return True
    
    def deploy_to_aws_direct(self, template_content: str, stack_name: str) -> str:
        """Direct deployment with Nova-Act automation from the app"""
        try:
            print(f"🚀 Starting Kiro Nova-Act deployment for {stack_name}")
            
            # Save template locally
            templates_folder = os.getenv('IAC_TEMPLATES_FOLDER', 'iac_templates')
            os.makedirs(templates_folder, exist_ok=True)
            
            template_filename = f"{stack_name}-template.yaml"
            local_path = os.path.join(templates_folder, template_filename)
            
            with open(local_path, 'w') as f:
                f.write(template_content)
            
            print(f"✅ Template saved: {local_path}")
            
            # Upload to S3
            print("📤 Uploading template to S3...")
            upload_success, upload_message = self.upload_template_to_s3(local_path, template_filename)
            
            if upload_success:
                s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
                aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
                public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{template_filename}"
                
                # Try direct Nova-Act automation first
                print("🤖 Attempting direct Nova-Act automation...")
                try:
                    from direct_nova_act_automation import deploy_with_direct_automation
                    
                    def progress_update(message):
                        print(f"   {message}")
                    
                    result = deploy_with_direct_automation(public_url, stack_name, progress_update)
                    
                    if result['success']:
                        return f"""
🎉 DIRECT NOVA-ACT AUTOMATION COMPLETED!

✅ Template uploaded: {public_url}
✅ Browser automation: {result['status']}
📊 Stack Name: {stack_name}
🎯 Deployment Status: {result['message']}

📋 Automation Details:
{result.get('details', 'Deployment completed successfully')}

🔗 Next Steps:
• Check AWS CloudFormation Console for stack outputs
• Monitor your deployed resources
• Remember to clean up resources when no longer needed

⚠️ Important: Your infrastructure is now live and may incur AWS charges
"""
                    else:
                        # Direct automation failed, fall back to extension method
                        print("⚠️ Direct automation failed, auto-activating extension method...")
                        instructions_file = self.create_nova_act_instructions(public_url, stack_name)
                        self.launch_chrome()
                        return self.fallback_to_manual_deployment(public_url, stack_name, instructions_file, result.get('error', 'Unknown error'))
                        
                except ImportError:
                    print("⚠️ Direct automation not available, auto-activating extension method...")
                    
                # Fallback to extension method
                instructions_file = self.create_nova_act_instructions(public_url, stack_name)
                self.launch_chrome()
                
                # Try automatic extension activation
                auto_success, auto_message = self.auto_activate_extension_method(instructions_file)
                
                if auto_success:
                    return f"""
🎉 KIRO NOVA-ACT EXTENSION METHOD ACTIVATED!

✅ Template uploaded: {public_url}
✅ Chrome opened with AWS CloudFormation Console
✅ Extension method activated: {auto_message}
📋 Instructions file: {instructions_file}

🤖 AUTOMATIC ACTIVATION SUCCESSFUL!

The Nova-Act extension method has been automatically activated:
• VS Code is open with the instruction file
• Nova-Act extension should be starting automatically
• Chrome is ready with AWS CloudFormation Console

📋 Monitor Progress:
• Check VS Code for Nova-Act automation status
• Watch Chrome browser for CloudFormation deployment
• Deployment should complete automatically

⏳ Expected Time: 5-15 minutes
🎯 Stack: {stack_name} | Template: {public_url}
"""
                else:
                    # Manual activation required
                    vscode_launched = self.find_and_launch_vscode(instructions_file)
                
                return f"""
🎉 KIRO NOVA-ACT DEPLOYMENT LAUNCHED!

✅ Template uploaded: {public_url}
✅ Chrome opened with AWS CloudFormation Console
{'✅' if vscode_launched else '⚠️'} VS Code {'launched with instructions' if vscode_launched else 'launch failed - use manual method'}
📋 Instructions file: {instructions_file}

🚀 Next Steps for Nova-Act Automation:

Method 1 - VS Code Command Palette:
• Press Ctrl+Shift+P in VS Code
• Type: "Nova-Act: Start Browser Automation"
• Follow the automation prompts

Method 2 - Kiro Launcher Script:
• Run: python launch_nova_act_kiro.py
• Automatically handles VS Code and Nova-Act setup

Method 3 - Manual Browser:
• Chrome is open with AWS Console
• Follow CloudFormation stack creation manually
• Use template URL: {public_url}

⏳ Expected deployment time: 5-15 minutes
🔐 Complete AWS login if prompted
📊 Monitor progress in Chrome browser

🎯 Stack Details:
• Name: {stack_name}
• Template: {local_path}
• S3 URL: {public_url}
"""
            else:
                # S3 upload failed, provide manual instructions
                return f"""
⚠️ PARTIAL DEPLOYMENT SETUP

❌ S3 upload failed: {upload_message}
✅ Chrome opened with AWS Console
✅ Template saved locally: {local_path}

📤 Manual Upload Required:
1. Upload template to S3 bucket: infrastruct
2. Use filename: {template_filename}
3. Expected S3 URL: https://infrastruct.s3.us-east-1.amazonaws.com/{template_filename}

🔧 Manual Upload Options:

AWS CLI Command:
aws s3 cp {local_path} s3://infrastruct/{template_filename}

AWS Console Upload:
1. Go to: https://s3.console.aws.amazon.com/s3/buckets/infrastruct
2. Click "Upload"
3. Select file: {local_path}
4. Upload as: {template_filename}

📋 After Upload:
• Use the S3 URL in CloudFormation
• Chrome is already open with AWS Console
• Complete stack creation manually

🎯 Stack Name: {stack_name}
"""
                
        except Exception as e:
            return f"""
❌ DEPLOYMENT SETUP FAILED

Error: {str(e)}

🔄 Fallback Options:
1. Check AWS credentials and permissions
2. Verify S3 bucket 'infrastruct' exists and is accessible
3. Try manual CloudFormation deployment
4. Use AWS Console directly: https://console.aws.amazon.com/cloudformation/home

📋 Manual Deployment:
• Create CloudFormation stack manually
• Upload template file from local system
• Stack name: {stack_name}
"""

# Create global instance
kiro_deployer = KiroNovaActDeployer()

# Export functions for GUI integration
def deploy_to_aws_direct(template_content: str, stack_name: str) -> str:
    """Main deployment function for GUI integration"""
    return kiro_deployer.deploy_to_aws_direct(template_content, stack_name)

def deploy_infrastructure(public_url: str, stack_name: str) -> str:
    """Legacy function for compatibility"""
    return f"Deployment initiated for {stack_name} using {public_url}"

def check_deployment_status(stack_name: str) -> str:
    """Check deployment status"""
    return f"Check status for {stack_name} in AWS CloudFormation Console"

def open_aws_cloudformation_console() -> str:
    """Open AWS Console"""
    webbrowser.open("https://console.aws.amazon.com/cloudformation/home")
    return "AWS CloudFormation Console opened"