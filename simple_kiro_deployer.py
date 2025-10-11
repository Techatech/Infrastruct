#!/usr/bin/env python3
"""
Simple Kiro Nova-Act Deployer - Clean version without indentation issues
"""

import os
import webbrowser
import subprocess
import json
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleKiroDeployer:
    def __init__(self):
        self.nova_act_available = True
        print("✅ Simple Kiro Nova-Act Deployer initialized")
    
    def upload_template_to_s3(self, local_path: str, s3_key: str) -> Tuple[bool, str]:
        """Upload template to S3 using boto3"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
            aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
            
            s3_client = boto3.client('s3', region_name=aws_region)
            s3_client.upload_file(local_path, s3_bucket, s3_key)
            
            public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_key}"
            return True, f"✅ Template uploaded to {public_url}"
            
        except Exception as e:
            return False, f"❌ Upload failed: {str(e)}"
    
    def create_nova_act_instructions(self, public_url: str, stack_name: str) -> str:
        """Create Nova-Act instruction file"""
        instructions = {
            "task": f"Deploy CloudFormation Stack: {stack_name}",
            "template_url": public_url,
            "stack_name": stack_name,
            "steps": [
                "Navigate to AWS CloudFormation Console",
                "Click Create Stack",
                "Select S3 URL template source",
                f"Enter template URL: {public_url}",
                f"Enter stack name: {stack_name}",
                "Complete stack creation process"
            ]
        }
        
        instructions_file = f"nova_deploy_{stack_name.replace('-', '_')}.json"
        with open(instructions_file, 'w') as f:
            json.dump(instructions, f, indent=2)
        
        return instructions_file
    
    def launch_chrome_and_vscode(self, instructions_file: str) -> bool:
        """Launch Chrome with AWS Console and VS Code with instructions"""
        try:
            # Launch Chrome
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ]
            
            chrome_launched = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, "https://console.aws.amazon.com/cloudformation/home"])
                    chrome_launched = True
                    break
            
            if not chrome_launched:
                webbrowser.open("https://console.aws.amazon.com/cloudformation/home")
            
            # Try to launch VS Code
            try:
                subprocess.Popen(["code", instructions_file])
                print("✅ VS Code launched with instructions")
            except:
                print("⚠️ VS Code launch failed - use manual method")
            
            return True
            
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            return False
    
    def deploy_to_aws_direct(self, template_content: str, stack_name: str) -> str:
        """Simple direct deployment function"""
        try:
            # Save template
            templates_folder = os.getenv('IAC_TEMPLATES_FOLDER', 'iac_templates')
            os.makedirs(templates_folder, exist_ok=True)
            
            template_filename = f"{stack_name}-template.yaml"
            local_path = os.path.join(templates_folder, template_filename)
            
            with open(local_path, 'w') as f:
                f.write(template_content)
            
            print(f"✅ Template saved: {local_path}")
            
            # Upload to S3
            success, message = self.upload_template_to_s3(local_path, template_filename)
            
            if success:
                s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
                aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
                public_url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{template_filename}"
                
                # Create instructions
                instructions_file = self.create_nova_act_instructions(public_url, stack_name)
                
                # Launch Chrome and VS Code
                self.launch_chrome_and_vscode(instructions_file)
                
                return f"""
🎉 KIRO NOVA-ACT DEPLOYMENT LAUNCHED!

✅ Template uploaded: {public_url}
✅ Chrome opened with AWS Console
✅ VS Code opened with instructions: {instructions_file}

📋 Next Steps:
1. Complete AWS login if prompted
2. In VS Code: Press Ctrl+Shift+P
3. Type: "Nova-Act: Start Browser Automation"
4. Follow the automation process

🚀 Deployment ready for Nova-Act automation!
"""
            else:
                return f"""
⚠️ PARTIAL DEPLOYMENT SETUP

❌ S3 upload failed: {message}
✅ Chrome opened with AWS Console
✅ Template saved locally: {local_path}

📋 Manual Steps Required:
1. Upload {local_path} to S3 bucket manually
2. Use the uploaded S3 URL in CloudFormation
3. Complete deployment in AWS Console

🔧 Manual Upload Command:
aws s3 cp {local_path} s3://infrastruct/{template_filename}
"""
                
        except Exception as e:
            return f"❌ Deployment setup failed: {str(e)}"

# Create global instance
simple_deployer = SimpleKiroDeployer()

def deploy_to_aws_direct(template_content: str, stack_name: str) -> str:
    """Simple deployment function for GUI integration"""
    return simple_deployer.deploy_to_aws_direct(template_content, stack_name)