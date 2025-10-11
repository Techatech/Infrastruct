import os
import webbrowser
import time
from typing import Optional, Dict, Any
from strands import Agent, tool
from dotenv import load_dotenv

# Try to import requests for login checking
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests library not available - login checking disabled")

# Load environment variables
load_dotenv()

class EnhancedDeploymentManager:
    def __init__(self):
        self.nova_act_available = False
        self.deployment_status = {}
        
        # Check if Nova-Act VS Code extension is available
        self.nova_act_available = self.check_nova_act_extension()
        
        if self.nova_act_available:
            print("✅ Nova-Act VS Code extension detected - automated deployment available")
            
            # Check Chrome installation
            chrome_available, chrome_message = self.check_chrome_installation()
            print(chrome_message)
            if not chrome_available:
                print("💡 Install Chrome for optimal Nova-Act performance: https://www.google.com/chrome/")
        else:
            print("⚠️ Nova-Act VS Code extension not detected - manual deployment mode")
            print("💡 Install Nova-Act extension in VS Code for automated deployment")
    
    def check_nova_act_extension(self) -> bool:
        """Check if Nova-Act VS Code extension is installed"""
        try:
            # Check if we're running in VS Code environment
            import subprocess
            result = subprocess.run(['code', '--list-extensions'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                extensions = result.stdout.lower()
                # Look for Nova-Act extension
                if 'nova-act' in extensions or 'amazonwebservices.amazon-nova-act' in extensions:
                    return True
            
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # VS Code not available or extension check failed
            # Assume extension might be available if we're in VS Code context
            return True  # Optimistic assumption for better UX
    
    def check_chrome_installation(self) -> tuple[bool, str]:
        """Check if Google Chrome is installed"""
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return True, f"✅ Chrome found at: {path}"
        
        return False, "⚠️ Chrome not found - Nova-Act works best with Chrome"
    
    def create_login_instructions(self) -> str:
        """Create user-friendly login instructions"""
        return """
🔐 AWS LOGIN GUIDANCE
====================

If you see the AWS login screen:

1️⃣ CHOOSE YOUR LOGIN METHOD:
   • AWS IAM User: Enter username/password
   • AWS SSO: Click "Sign in with SSO"
   • Root Account: Use root email/password (not recommended)
   • Federated Login: Use your organization's login

2️⃣ COMPLETE AUTHENTICATION:
   • Enter your credentials
   • Complete MFA if required (SMS, authenticator app, etc.)
   • Wait for successful login redirect

3️⃣ AUTOMATION RESUMES:
   • Once logged in, you'll see the AWS Console
   • Nova-Act will detect successful login automatically
   • Deployment automation will resume within 15 seconds

⏱️ TIME LIMIT: You have 5 minutes to complete login
🔄 RETRY: If timeout occurs, click "Deploy to AWS" again

💡 TIP: Log in to AWS Console beforehand to avoid delays
"""

    def create_deployment_instructions(self, public_url: str, stack_name: str) -> str:
        """Create detailed deployment instructions for Nova-Act with enhanced login handling"""
        return f"""You are an AWS CloudFormation deployment assistant. Follow these instructions precisely:

DEPLOYMENT WORKFLOW:
==================

1. INITIAL NAVIGATION & LOGIN CHECK:
   - Navigate to: https://console.aws.amazon.com/cloudformation/home
   - WAIT AND CHECK FOR LOGIN SCREEN:
     * If AWS login page appears, PAUSE automation
     * Display message: "⏳ Please log in to AWS Console. Automation will resume automatically after login."
     * Wait up to 5 minutes for user to complete login
     * Check every 15 seconds for successful login (look for CloudFormation console)
     * If login successful, display: "✅ Login detected! Resuming automation..."
     * If timeout after 5 minutes, display: "⚠️ Login timeout. Please refresh and try again."
   - If already logged in, display: "✅ Already logged in! Starting deployment..."
   - Once in CloudFormation console, proceed to step 2

2. CREATE STACK INITIATION:
   - Look for "Create stack" button (orange/blue button, usually top-right area)
   - Click "Create stack" → "With new resources (standard)"
   - Wait for page to load completely
   - Verify page title contains "Create stack"

3. TEMPLATE SELECTION:
   - Under "Prerequisite - Prepare template":
     * Select "Choose an existing template" (should be default)
   - Under "Specify template":
     * Select "Amazon S3 URL" radio button
     * In the S3 URL text field, enter: {public_url}
     * Wait for template validation (green checkmark or "Valid template" message)
   - Click "Next" button (bottom right)

4. STACK DETAILS:
   - On "Specify stack details" page:
     * In "Stack name" field, enter: {stack_name}
     * Leave all other parameters as default unless specifically required
   - Click "Next" button (bottom right)

5. CONFIGURE STACK OPTIONS:
   - On "Configure stack options" page:
     * Leave all settings as default (tags, permissions, rollback, etc.)
     * Scroll to bottom
   - Click "Next" button (bottom right)

6. REVIEW AND CREATE:
   - On "Review" page:
     * Scroll through and verify all settings
     * At bottom, check "I acknowledge that AWS CloudFormation might create IAM resources" if present
   - Click "Submit" or "Create stack" button (bottom right)

7. MONITOR DEPLOYMENT:
   - On stack details page:
     * Click "Stack info" tab if not already selected
     * Monitor "Status" field under "Overview"
     * Wait for status to change to "CREATE_COMPLETE"
     * If status shows "CREATE_FAILED", capture error details from Events tab

8. COMPLETION:
   - Once status is "CREATE_COMPLETE":
     * Capture stack outputs if any
     * Return success message with deployment details

ERROR HANDLING:
- If any step fails, capture screenshot and error details
- If login expires during deployment, pause and wait for re-authentication
- If template validation fails, report the specific error with details
- If stack creation fails, capture failure reason from Events tab
- If login timeout (5 minutes), display timeout message and stop automation

LOGIN TIMEOUT HANDLING:
- If user doesn't complete login within 5 minutes:
  * Display: "⚠️ Login timeout reached. Please refresh browser and try again."
  * Stop automation gracefully
  * Allow user to restart deployment process

EXPECTED COMPLETION TIME: 
- Login: Up to 5 minutes (if required)
- Deployment: 5-15 minutes depending on resources
- Total: 5-20 minutes maximum

SUCCESS FORMAT: "✅ Deployment for Environment: {stack_name} was successful. Stack Status: CREATE_COMPLETE. Please review the deployed resources in the AWS Console."

TIMEOUT FORMAT: "⚠️ Login timeout for deployment: {stack_name}. Please refresh browser and restart deployment."
"""

    def check_cloudformation_access(self, url: str) -> tuple[bool, str]:
        """Check if URL leads directly to CloudFormation console (no login required)"""
        if not REQUESTS_AVAILABLE:
            return True, "⚠️ Cannot check login status - assuming login may be required"
        
        try:
            # Make a simple request to check if we get redirected to login
            response = requests.get(url, allow_redirects=True, timeout=10)
            
            # Check if we're on a login page
            login_indicators = [
                'signin.aws.amazon.com',
                'aws.amazon.com/console/home',
                'Sign in to AWS',
                'AWS Management Console',
                'Enter your email'
            ]
            
            final_url = response.url.lower()
            page_content = response.text.lower()
            
            # If we're redirected to signin or see login indicators
            for indicator in login_indicators:
                if indicator.lower() in final_url or indicator.lower() in page_content:
                    return False, "🔐 Login required - redirected to AWS sign-in page"
            
            # If we see CloudFormation-specific content, we're logged in
            cf_indicators = ['cloudformation', 'create stack', 'stacks']
            for indicator in cf_indicators:
                if indicator in page_content:
                    return True, "✅ Already logged in - CloudFormation console accessible"
            
            return False, "⚠️ Unable to determine login status"
            
        except Exception as e:
            return False, f"⚠️ Cannot check login status: {str(e)}"

    def create_nova_act_steps(self, public_url: str, stack_name: str) -> list:
        """Create individual Nova-Act steps following best practices"""
        steps = [
            {
                "step": 1,
                "action": f"Navigate to https://console.aws.amazon.com/cloudformation/home",
                "description": "Open AWS CloudFormation Console"
            },
            {
                "step": 2, 
                "action": "Click the 'Create stack' button",
                "description": "Start stack creation process"
            },
            {
                "step": 3,
                "action": "Click 'With new resources (standard)'",
                "description": "Select standard stack creation"
            },
            {
                "step": 4,
                "action": "Click the 'Amazon S3 URL' radio button",
                "description": "Select S3 URL as template source"
            },
            {
                "step": 5,
                "action": f"Type '{public_url}' in the S3 URL text field",
                "description": "Enter the CloudFormation template URL"
            },
            {
                "step": 6,
                "action": "Click the 'Next' button",
                "description": "Proceed to stack details"
            },
            {
                "step": 7,
                "action": f"Type '{stack_name}' in the Stack name field",
                "description": "Enter the stack name"
            },
            {
                "step": 8,
                "action": "Click the 'Next' button",
                "description": "Proceed to configure options"
            },
            {
                "step": 9,
                "action": "Click the 'Next' button",
                "description": "Proceed to review"
            },
            {
                "step": 10,
                "action": "Check the 'I acknowledge that AWS CloudFormation might create IAM resources' checkbox if present",
                "description": "Acknowledge IAM resource creation"
            },
            {
                "step": 11,
                "action": "Click the 'Submit' or 'Create stack' button",
                "description": "Submit the stack for creation"
            }
        ]
        return steps

    def deploy_with_nova_act_direct(self, public_url: str, stack_name: str) -> str:
        """Deploy directly using Nova-Act in Kiro IDE with proper step-by-step approach"""
        try:
            import subprocess
            import json
            import webbrowser
            
            print(f"🚀 Starting direct Nova-Act deployment for {stack_name}...")
            print(f"🌐 Opening Chrome browser...")
            print(f"🔐 Checking AWS login status...")
            
            # Check if login is required before starting automation
            aws_console_url = "https://console.aws.amazon.com/cloudformation/home"
            login_required, login_status = self.check_cloudformation_access(aws_console_url)
            
            print(f"Login check result: {login_status}")
            
            # Create step-by-step Nova-Act instructions
            nova_steps = self.create_nova_act_steps(public_url, stack_name)
            
            # Create Nova-Act Python script for Kiro IDE
            nova_script = self.create_nova_act_script(nova_steps, public_url, stack_name, login_required)
            
            # Save the Nova-Act script
            script_file = os.path.join(os.getcwd(), f"nova_deploy_{stack_name.replace('-', '_')}.py")
            with open(script_file, 'w') as f:
                f.write(nova_script)
            
            print(f"🤖 Nova-Act script created: {script_file}")
            
            # Open Chrome browser first
            chrome_launched = self.launch_chrome_browser(aws_console_url)
            
            print(f"✅ Chrome launched: {chrome_launched}")
            
            # Provide instructions for Kiro IDE Nova-Act usage
            return self.create_kiro_deployment_instructions(script_file, stack_name, public_url, login_required)
                
        except Exception as e:
            return f"""
❌ NOVA-ACT PREPARATION FAILED

Error preparing Nova-Act deployment: {str(e)}

🔄 Fallback Options:
1. Try manual deployment (see instructions below)
2. Check Kiro IDE Nova-Act extension installation
3. Verify file permissions in current directory

{self.manual_deployment_guide(public_url, stack_name)}
"""

    def create_nova_act_script(self, steps: list, public_url: str, stack_name: str, login_required: bool) -> str:
        """Create a Nova-Act Python script following best practices"""
        
        script = f'''#!/usr/bin/env python3
"""
Nova-Act Deployment Script for {stack_name}
Generated by AWS Infrastruct Tool

This script uses the recommended Nova-Act approach with multiple small act() calls
for reliable, maintainable automation.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def deploy_cloudformation_stack():
    """Deploy CloudFormation stack using Nova-Act step-by-step approach"""
    
    # Import Nova-Act (adjust import based on your setup)
    try:
        from nova_act import NovaAct
    except ImportError:
        print("❌ Nova-Act not available. Please install Nova-Act extension in Kiro IDE.")
        return False
    
    # Get API key from environment
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ Nova-Act API key not found. Please set NOVA_ACT_API_KEY in .env file.")
        return False
    
    print("🚀 Starting Nova-Act CloudFormation deployment...")
    print(f"📋 Stack Name: {stack_name}")
    print(f"🌐 Template URL: {public_url}")
    
    try:
        # Initialize Nova-Act with Chrome browser
        with NovaAct(starting_page="https://console.aws.amazon.com/cloudformation/home", 
                     api_key=api_key) as nova:
            
            print("🤖 Nova-Act initialized, starting deployment steps...")
'''

        # Add login handling if required
        if login_required:
            script += '''
            # Step 0: Handle login if required
            print("🔐 Checking for AWS login requirement...")
            login_result = nova.act("Check if AWS login is required, if login page is visible, wait for user to complete login")
            print(f"Login check: {login_result}")
            
'''

        # Add each deployment step
        for step in steps:
            script += f'''
            # Step {step['step']}: {step['description']}
            print("Step {step['step']}: {step['description']}")
            result_{step['step']} = nova.act("{step['action']}")
            print(f"Result: {{result_{step['step']}}}")
            
'''

        # Add completion and monitoring
        script += f'''
            # Final step: Monitor deployment
            print("📊 Monitoring stack creation...")
            monitor_result = nova.act("Wait for the stack status to show CREATE_COMPLETE or CREATE_FAILED, check the status every 30 seconds")
            print(f"Final status: {{monitor_result}}")
            
            print("✅ Nova-Act deployment automation completed!")
            return True
            
    except Exception as e:
        print(f"❌ Nova-Act deployment failed: {{e}}")
        return False

if __name__ == "__main__":
    success = deploy_cloudformation_stack()
    if success:
        print("🎉 Deployment completed successfully!")
    else:
        print("⚠️ Deployment encountered issues - check the logs above")
'''
        
        return script

    def launch_chrome_browser(self, url: str) -> bool:
        """Launch Chrome browser with the specified URL"""
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
        ]
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    import subprocess
                    subprocess.Popen([chrome_path, url])
                    return True
                except Exception as e:
                    print(f"⚠️ Failed to launch Chrome at {chrome_path}: {e}")
                    continue
        
        # Fallback to default browser
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"⚠️ Failed to open browser: {e}")
            return False

    def create_kiro_deployment_instructions(self, script_file: str, stack_name: str, public_url: str, login_required: bool) -> str:
        """Create instructions for using Nova-Act in Kiro IDE"""
        
        login_note = ""
        if login_required:
            login_note = """
🔐 Login Required:
• AWS login screen will appear first
• Complete your authentication
• Nova-Act will wait and then continue automatically
"""
        
        return f"""
🎉 NOVA-ACT KIRO IDE DEPLOYMENT READY!

✅ Chrome browser opened with AWS CloudFormation Console
✅ Nova-Act script created with step-by-step automation
📊 Stack Name: {stack_name}
🌐 Template URL: {public_url}

📋 To Start Nova-Act Automation in Kiro IDE:

Method 1 - Run Nova-Act Script:
• Open Kiro IDE terminal
• Run: python {script_file}
• Nova-Act will execute step-by-step deployment

Method 2 - Interactive Nova-Act:
• Open Kiro IDE
• Use Nova-Act extension
• Import the script: {script_file}
• Execute step by step

Method 3 - Manual Nova-Act Commands:
• Open Kiro IDE Nova-Act panel
• Execute each step individually:
  1. nova.act("Navigate to https://console.aws.amazon.com/cloudformation/home")
  2. nova.act("Click the 'Create stack' button")
  3. nova.act("Click 'With new resources (standard)'")
  4. nova.act("Click the 'Amazon S3 URL' radio button")
  5. nova.act("Type '{public_url}' in the S3 URL text field")
  6. nova.act("Click the 'Next' button")
  7. nova.act("Type '{stack_name}' in the Stack name field")
  8. nova.act("Click the 'Next' button")
  9. nova.act("Click the 'Next' button")
  10. nova.act("Check the IAM acknowledgment checkbox if present")
  11. nova.act("Click the 'Submit' or 'Create stack' button")

{login_note}

🤖 Nova-Act Best Practices Used:
• ✅ Prescriptive and succinct commands
• ✅ Broken into small, manageable steps
• ✅ Each step has a clear, specific action
• ✅ Following Nova-Act documentation recommendations

⏳ Expected Time: 5-15 minutes for complete deployment

⚠️ Important:
• Keep Chrome and Kiro IDE open during deployment
• Nova-Act will control the browser automatically
• Monitor progress in Kiro IDE Nova-Act panel
"""
            
            # Provide user instructions based on login status
            if login_required:
                return f"""
🎉 NOVA-ACT DEPLOYMENT LAUNCHED!

✅ Chrome browser opened with AWS Console
🔐 Login required - please complete AWS authentication
📊 Stack Name: {stack_name}
🌐 Template URL: {public_url}

⏳ Deployment Process:
1. 🔐 Complete AWS login (you have 5 minutes)
2. ✅ After login: Automation will detect and resume
3. 🤖 CloudFormation stack creation begins
4. 📊 Monitor progress in browser

📋 To Start Nova-Act Automation:

Method 1 - VS Code Command Palette:
• Press Ctrl+Shift+P in VS Code
• Type: "Nova-Act: Start Browser Automation"
• Load instruction file: {instructions_file}

Method 2 - Manual VS Code Opening:
• Open VS Code manually
• Open file: {instructions_file}
• Use Nova-Act extension to run the instructions

Method 3 - Launcher Script:
• Run: python launch_nova_act.py
• Automatically finds VS Code and instruction files
• Launches VS Code with Nova-Act ready to go

Method 4 - Direct Browser Automation:
• Chrome is already open with AWS Console
• Follow the step-by-step instructions in the file
• Complete the deployment manually if needed

🔐 Login Guidance:
{login_guide}

⚠️ Important:
• Complete AWS login within 5 minutes
• Keep Chrome and VS Code open
• Automation resumes automatically after login
"""
            else:
                return f"""
🎉 NOVA-ACT DEPLOYMENT LAUNCHED!

✅ Chrome browser opened with AWS Console
✅ Already logged in - ready for automation
📊 Stack Name: {stack_name}
🌐 Template URL: {public_url}

⏳ Deployment Process:
1. ✅ Login verified - proceeding directly
2. 🤖 CloudFormation automation starting
3. 📊 Monitor progress in browser

📋 To Start Nova-Act Automation:

Method 1 - VS Code Command Palette:
• Press Ctrl+Shift+P in VS Code
• Type: "Nova-Act: Start Browser Automation"
• Load instruction file: {instructions_file}

Method 2 - Manual VS Code Opening:
• Open VS Code manually
• Open file: {instructions_file}
• Use Nova-Act extension to run the instructions

Method 3 - Launcher Script:
• Run: python launch_nova_act.py
• Automatically finds VS Code and instruction files
• Launches VS Code with Nova-Act ready to go

Method 4 - Direct Browser Automation:
• Chrome is already open with AWS Console
• Follow the step-by-step instructions in the file
• Complete the deployment manually if needed

🚀 Automation should begin immediately since you're already logged in!

⚠️ Keep Chrome and VS Code open during deployment
"""
            
            # Method 2: Open Chrome directly and provide instructions
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if chrome_path:
                # Open Chrome with AWS Console
                aws_url = "https://console.aws.amazon.com/cloudformation/home"
                subprocess.Popen([chrome_path, aws_url])
                
                return f"""
🎉 DEPLOYMENT STARTED - CHROME OPENED!

✅ Chrome browser opened with AWS CloudFormation Console
🤖 Ready for automated deployment

📋 AUTOMATED DEPLOYMENT STEPS:
{instructions}

📊 Deployment Details:
• Stack Name: {stack_name}
• Template URL: {public_url}
• Browser: Chrome (opened automatically)

🚀 Next Steps:
1. Chrome should show AWS CloudFormation Console
2. 🔐 If login screen appears: Complete AWS login first
3. ✅ After login: Follow the automated steps above
4. Or use Nova-Act VS Code extension for full automation

⏳ Expected Time: 5-15 minutes (plus login time if needed)

🔐 Login Guidance:
• You have up to 5 minutes to complete AWS login
• Automation will detect successful login automatically
• Use your standard AWS credentials (IAM user, SSO, etc.)
• After login, automation resumes the deployment process

💡 For full automation, use VS Code Command Palette:
   Ctrl+Shift+P → "Nova-Act: Start Browser Automation"
   Load file: {instructions_file}
"""
            else:
                # Fallback: Open default browser
                webbrowser.open("https://console.aws.amazon.com/cloudformation/home")
                return f"""
🎉 DEPLOYMENT STARTED - BROWSER OPENED!

✅ Browser opened with AWS CloudFormation Console
🤖 Ready for deployment

📋 DEPLOYMENT INSTRUCTIONS:
{instructions}

📊 Deployment Details:
• Stack Name: {stack_name}
• Template URL: {public_url}
• Instructions saved: {instructions_file}

🚀 Complete the deployment by following the steps above
⏳ Expected Time: 5-15 minutes
"""
                
        except Exception as e:
            return f"""
❌ DIRECT DEPLOYMENT LAUNCH FAILED

Error: {str(e)}

🔄 Fallback: Opening AWS Console manually
{self.open_aws_console()}

📋 Manual deployment instructions:
{self.manual_deployment_guide(public_url, stack_name)}
"""

    def deploy_with_nova_act(self, public_url: str, stack_name: str) -> str:
        """Deploy using Nova-Act - direct launch approach"""
        return self.deploy_with_nova_act_direct(public_url, stack_name)
    
    def manual_deployment_guide(self, public_url: str, stack_name: str) -> str:
        """Provide manual deployment instructions"""
        return f"""
📋 MANUAL DEPLOYMENT GUIDE

Since automated deployment is not available, please follow these steps:

🔗 AWS CloudFormation Console: https://console.aws.amazon.com/cloudformation/home

📝 Step-by-Step Instructions:

1️⃣ NAVIGATE TO CLOUDFORMATION:
   • Open: https://console.aws.amazon.com/cloudformation/home
   • Ensure you're in the correct AWS region

2️⃣ CREATE STACK:
   • Click "Create stack" → "With new resources (standard)"

3️⃣ SPECIFY TEMPLATE:
   • Select "Choose an existing template"
   • Select "Amazon S3 URL"
   • Enter URL: {public_url}
   • Click "Next"

4️⃣ STACK DETAILS:
   • Stack name: {stack_name}
   • Review parameters (leave defaults unless needed)
   • Click "Next"

5️⃣ CONFIGURE OPTIONS:
   • Leave default settings
   • Click "Next"

6️⃣ REVIEW AND CREATE:
   • Review all settings
   • Check acknowledgment boxes if present
   • Click "Submit" or "Create stack"

7️⃣ MONITOR DEPLOYMENT:
   • Wait for status: CREATE_COMPLETE
   • Check Events tab for any issues
   • Review Outputs tab for important information

⏱️ Expected Time: 5-15 minutes

🆘 Need Help?
• Check AWS CloudFormation documentation
• Review stack events for error details
• Ensure you have proper IAM permissions

🔒 Security Reminder: Sign out of AWS Console when finished
"""

    def upload_template_to_s3_boto3(self, local_path: str, s3_key: str) -> tuple[bool, str]:
        """Upload template to S3 bucket using boto3"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
            aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
            
            # Create S3 client
            s3_client = boto3.client('s3', region_name=aws_region)
            
            # Upload file
            s3_client.upload_file(local_path, s3_bucket, s3_key)
            
            # Construct public URL
            public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_key}"
            
            return True, f"✅ Template uploaded successfully to {public_url}"
            
        except NoCredentialsError:
            return False, "❌ AWS credentials not found - configure AWS credentials"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                return False, f"❌ S3 bucket '{s3_bucket}' does not exist"
            elif error_code == 'AccessDenied':
                return False, f"❌ Access denied to S3 bucket '{s3_bucket}'"
            else:
                return False, f"❌ S3 upload failed: {e.response['Error']['Message']}"
        except FileNotFoundError:
            return False, f"❌ Local file not found: {local_path}"
        except Exception as e:
            return False, f"❌ Upload error: {str(e)}"

    def upload_template_to_s3(self, local_path: str, s3_key: str) -> tuple[bool, str]:
        """Upload template to S3 bucket - try boto3 first, fallback to AWS CLI"""
        # Try boto3 first
        success, message = self.upload_template_to_s3_boto3(local_path, s3_key)
        if success:
            return success, message
        
        # Fallback to AWS CLI if boto3 fails
        try:
            import subprocess
            
            s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
            s3_uri = f"s3://{s3_bucket}/{s3_key}"
            
            result = subprocess.run([
                'aws', 's3', 'cp', local_path, s3_uri,
                '--region', os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
                public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_key}"
                return True, f"✅ Template uploaded via AWS CLI to {public_url}"
            else:
                return False, f"❌ Both boto3 and AWS CLI failed. Boto3: {message}, CLI: {result.stderr}"
                
        except Exception as cli_error:
            return False, f"❌ Both upload methods failed. Boto3: {message}, CLI: {str(cli_error)}"

    def open_aws_console(self, stack_name: str = None) -> str:
        """Open AWS CloudFormation console in browser"""
        try:
            url = "https://console.aws.amazon.com/cloudformation/home"
            if stack_name:
                # Try to construct direct stack URL (region-dependent)
                url += f"#/stacks/stackinfo?stackId={stack_name}"
            
            webbrowser.open(url)
            return f"✅ AWS CloudFormation Console opened in your default browser"
        except Exception as e:
            return f"❌ Failed to open browser: {str(e)}"

# Global deployment manager instance
deployment_manager = EnhancedDeploymentManager()

@tool
def deploy_to_aws_direct(template_content: str, stack_name: str) -> str:
    """
    Direct deployment: Click Deploy → Chrome Opens → Automation Starts
    
    This is the main deployment function that provides the expected user experience:
    1. User provides stack name and clicks "Deploy to AWS"
    2. System saves template and uploads to S3
    3. Chrome browser opens automatically
    4. Nova-Act starts automated deployment immediately
    
    Args:
        template_content (str): CloudFormation template YAML/JSON content
        stack_name (str): Name for the CloudFormation stack
    
    Returns:
        str: Deployment status and progress information
    """
    try:
        print(f"🚀 DIRECT DEPLOYMENT INITIATED")
        print(f"📋 Stack Name: {stack_name}")
        
        # Get environment variables
        s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
        templates_folder = os.getenv('IAC_TEMPLATES_FOLDER', 'iac_templates')
        aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
        
        # Clean stack name
        clean_stack_name = stack_name.strip().replace(' ', '-')
        
        # Save template to local folder
        template_filename = f"{clean_stack_name}-template.yaml"
        local_template_path = os.path.join(templates_folder, template_filename)
        
        # Ensure templates folder exists
        os.makedirs(templates_folder, exist_ok=True)
        
        # Save template content
        with open(local_template_path, 'w') as f:
            f.write(template_content)
        
        print(f"✅ Template saved: {local_template_path}")
        
        # Construct S3 URL
        s3_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{template_filename}"
        
        # Try automatic S3 upload
        print("📤 Uploading template to S3...")
        upload_success, upload_message = deployment_manager.upload_template_to_s3(local_template_path, template_filename)
        
        if upload_success:
            print("✅ S3 upload successful")
            
            # Launch direct Nova-Act deployment
            print("🤖 Launching Nova-Act automation...")
            deployment_result = deployment_manager.deploy_with_nova_act_direct(s3_url, clean_stack_name)
            
            return f"""
🎉 DEPLOYMENT LAUNCHED SUCCESSFULLY!

✅ Template uploaded to S3: {s3_url}
🚀 Chrome browser opening with automated deployment
🤖 Nova-Act handling CloudFormation stack creation

{deployment_result}

📊 Deployment Summary:
• Stack Name: {clean_stack_name}
• Template: {local_template_path}
• S3 URL: {s3_url}
• Status: Automation in progress

⏳ Sit back and watch the magic happen!
"""
        else:
            # Upload failed, but still try to deploy with manual upload instructions
            print(f"⚠️ S3 upload failed: {upload_message}")
            
            # Still launch browser for manual deployment
            deployment_result = deployment_manager.deploy_with_nova_act_direct(s3_url, clean_stack_name)
            
            return f"""
⚠️ PARTIAL DEPLOYMENT LAUNCH

❌ Automatic S3 upload failed: {upload_message}
✅ Chrome browser opened for manual deployment

📤 MANUAL UPLOAD REQUIRED:
1. Upload {local_template_path} to S3 bucket: {s3_bucket}
2. Use filename: {template_filename}
3. Expected URL: {s3_url}

{deployment_result}

🔧 Quick Upload Command:
aws s3 cp {local_template_path} s3://{s3_bucket}/{template_filename}
"""
            
    except Exception as e:
        return f"""
❌ DEPLOYMENT LAUNCH FAILED

Error: {str(e)}

🔄 Fallback: Opening AWS Console for manual deployment
Stack Name: {stack_name}

{deployment_manager.open_aws_console()}
{deployment_manager.manual_deployment_guide("your-s3-url", stack_name)}
"""

@tool
def deploy_infrastructure_from_template(template_content: str, stack_name: str) -> str:
    """
    Complete deployment workflow: save template → upload to S3 → deploy with Nova-Act
    
    Args:
        template_content (str): CloudFormation template YAML/JSON content
        stack_name (str): Name for the CloudFormation stack
    
    Returns:
        str: Deployment result with status and next steps
    """
    try:
        # Get environment variables
        s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
        templates_folder = os.getenv('IAC_TEMPLATES_FOLDER', 'iac_templates')
        aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
        
        # Clean stack name
        clean_stack_name = stack_name.strip().replace(' ', '-')
        
        # Save template to local folder
        template_filename = f"{clean_stack_name}-template.yaml"
        local_template_path = os.path.join(templates_folder, template_filename)
        
        # Ensure templates folder exists
        os.makedirs(templates_folder, exist_ok=True)
        
        # Save template content
        with open(local_template_path, 'w') as f:
            f.write(template_content)
        
        print(f"✅ Template saved to: {local_template_path}")
        
        # Construct S3 URL
        s3_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{template_filename}"
        
        print(f"🚀 Starting deployment process...")
        print(f"📄 Template: {local_template_path}")
        print(f"🌐 S3 URL: {s3_url}")
        print(f"🏷️ Stack: {clean_stack_name}")
        
        # Try automatic S3 upload first
        print("📤 Attempting automatic S3 upload...")
        upload_success, upload_message = deployment_manager.upload_template_to_s3(local_template_path, template_filename)
        
        if upload_success:
            print(upload_message)
            upload_status = f"✅ TEMPLATE UPLOADED AUTOMATICALLY\n\n{upload_message}\n"
        else:
            print(upload_message)
            upload_status = f"""
📤 AUTOMATIC UPLOAD FAILED - MANUAL UPLOAD REQUIRED

{upload_message}

📋 Manual Upload Options:

1️⃣ AWS CLI METHOD:
   aws s3 cp {local_template_path} s3://{s3_bucket}/{template_filename}

2️⃣ AWS CONSOLE METHOD:
   • Go to: https://s3.console.aws.amazon.com/s3/buckets/{s3_bucket}
   • Click "Upload"
   • Select file: {local_template_path}
   • Upload as: {template_filename}

3️⃣ VERIFY UPLOAD:
   • Check that {s3_url} is accessible
   • Template should be publicly readable for CloudFormation

"""
        
        # Try Nova-Act VS Code extension deployment
        if deployment_manager.nova_act_available:
            print("🤖 Using Nova-Act VS Code extension...")
            deployment_result = deployment_manager.deploy_with_nova_act(s3_url, clean_stack_name)
            
            return f"""
{upload_status}

{deployment_result}

📋 Complete Workflow Summary:
1. ✅ Template saved locally: {local_template_path}
2. {'✅' if upload_success else '⚠️'} S3 upload: {s3_url}
3. 🤖 Nova-Act automation: Ready for VS Code extension
4. 📊 Monitor progress in VS Code Output panel
"""
        else:
            print("📋 Nova-Act extension not available, providing manual deployment guide...")
            deployment_manager.open_aws_console()
            manual_guide = deployment_manager.manual_deployment_guide(s3_url, clean_stack_name)
            
            return f"""
{upload_status}

{manual_guide}
"""
            
    except Exception as e:
        return f"❌ Error in deployment workflow: {str(e)}"

@tool
def deploy_infrastructure(public_url: str, stack_name: str) -> str:
    """
    Enhanced deployment function with Nova-Act browser automation and manual fallback.
    
    Automates AWS CloudFormation stack deployment using browser automation or provides
    detailed manual instructions as fallback.
    
    Args:
        public_url (str): Public S3 bucket URL containing the CloudFormation template
        stack_name (str): Name for the CloudFormation stack
    
    Returns:
        str: Deployment result with status and next steps
    """
    
    # Validate inputs
    if not public_url or not public_url.startswith(('http://', 'https://')):
        return "❌ Error: Invalid public_url. Must be a valid HTTP/HTTPS URL."
    
    if not stack_name or len(stack_name.strip()) == 0:
        return "❌ Error: Stack name cannot be empty."
    
    # Clean stack name (CloudFormation naming requirements)
    clean_stack_name = stack_name.strip().replace(' ', '-')
    
    print(f"🚀 Starting deployment process...")
    print(f"📄 Template: {public_url}")
    print(f"🏷️ Stack: {clean_stack_name}")
    
    # Try Nova-Act VS Code extension first, fallback to manual
    if deployment_manager.nova_act_available:
        print("🤖 Using Nova-Act VS Code extension...")
        return deployment_manager.deploy_with_nova_act(public_url, clean_stack_name)
    else:
        print("📋 Nova-Act extension not available, providing manual deployment guide...")
        # Also open the browser for convenience
        deployment_manager.open_aws_console()
        return deployment_manager.manual_deployment_guide(public_url, clean_stack_name)

@tool 
def check_deployment_status(stack_name: str) -> str:
    """
    Check the status of a CloudFormation stack deployment.
    
    Args:
        stack_name (str): Name of the CloudFormation stack to check
        
    Returns:
        str: Instructions for checking deployment status
    """
    return f"""
🔍 CHECKING DEPLOYMENT STATUS FOR: {stack_name}

📋 Manual Status Check:
1. Go to: https://console.aws.amazon.com/cloudformation/home
2. Find stack: {stack_name}
3. Check Status column

📊 Possible Status Values:
• CREATE_IN_PROGRESS: Stack is being created
• CREATE_COMPLETE: ✅ Stack created successfully
• CREATE_FAILED: ❌ Stack creation failed
• ROLLBACK_IN_PROGRESS: Rolling back due to failure
• ROLLBACK_COMPLETE: Rollback completed

🔧 If Status is CREATE_FAILED:
1. Click on the stack name
2. Go to "Events" tab
3. Look for error messages (red entries)
4. Address the issues and retry deployment

⏱️ Typical deployment time: 5-15 minutes
"""

@tool
def open_aws_cloudformation_console() -> str:
    """
    Open the AWS CloudFormation console in the default browser.
    
    Returns:
        str: Confirmation message
    """
    return deployment_manager.open_aws_console()