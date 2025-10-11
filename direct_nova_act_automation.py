#!/usr/bin/env python3
"""
Direct Nova-Act Browser Automation Integration
Runs Nova-Act automation directly from the Python app
"""

import os
import time
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DirectNovaActAutomation:
    def __init__(self):
        self.api_key = os.getenv('NOVA_ACT_API_KEY')
        self.nova_act_available = False
        
        # Try to import Nova-Act SDK
        try:
            from nova_act import NovaAct
            self.NovaAct = NovaAct
            
            if self.api_key:
                self.nova_act_available = True
                print("✅ Nova-Act SDK available for direct automation")
            else:
                print("⚠️ Nova-Act SDK found but no API key configured")
                print("💡 Add NOVA_ACT_API_KEY to your .env file")
                
        except ImportError:
            print("⚠️ Nova-Act SDK not available")
            print("💡 Install with: pip install nova-act")
            self.NovaAct = None
    
    def deploy_cloudformation_stack(self, template_url: str, stack_name: str, 
                                  progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Deploy CloudFormation stack using direct Nova-Act automation
        
        Args:
            template_url: S3 URL of the CloudFormation template
            stack_name: Name for the CloudFormation stack
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict with deployment result and status
        """
        
        if not self.nova_act_available:
            return {
                'success': False,
                'error': 'Nova-Act SDK not available or API key missing',
                'fallback': 'manual_deployment'
            }
        
        try:
            if progress_callback:
                progress_callback("🚀 Starting Nova-Act browser automation...")
            
            # Initialize Nova-Act with AWS Console
            with self.NovaAct(
                starting_page="https://console.aws.amazon.com/cloudformation/home",
                api_key=self.api_key
            ) as browser:
                
                if progress_callback:
                    progress_callback("🌐 Browser opened, navigating to CloudFormation...")
                
                # Step 1: Navigate and check login
                result = browser.act("""
                Check if we're on the AWS CloudFormation console page.
                If we see a login screen, wait for user to log in (up to 5 minutes).
                Once logged in and on the CloudFormation console, proceed to create a new stack.
                """)
                
                if progress_callback:
                    progress_callback("🔐 Login check completed, proceeding with stack creation...")
                
                # Step 2: Create stack with template
                result = browser.act(f"""
                Create a new CloudFormation stack with these details:
                1. Click "Create stack" button
                2. Select "With new resources (standard)"
                3. Choose "Amazon S3 URL" as template source
                4. Enter this S3 URL: {template_url}
                5. Wait for template validation
                6. Click "Next" to proceed
                """)
                
                if progress_callback:
                    progress_callback("📋 Template loaded, configuring stack details...")
                
                # Step 3: Configure stack details
                result = browser.act(f"""
                Configure the stack details:
                1. Enter stack name: {stack_name}
                2. Leave other parameters as default unless required
                3. Click "Next" to proceed to configuration options
                """)
                
                if progress_callback:
                    progress_callback("⚙️ Stack configured, proceeding to review...")
                
                # Step 4: Configure options and review
                result = browser.act("""
                Configure stack options and review:
                1. Leave all configuration options as default
                2. Click "Next" to proceed to review
                3. Review all settings
                4. Check any required acknowledgment boxes (like IAM resource creation)
                5. Click "Submit" or "Create stack" to start deployment
                """)
                
                if progress_callback:
                    progress_callback("🚀 Stack creation initiated, monitoring deployment...")
                
                # Step 5: Monitor deployment
                result = browser.act(f"""
                Monitor the stack deployment:
                1. Wait for the stack status to change from "CREATE_IN_PROGRESS"
                2. Check the status every 30 seconds
                3. If status becomes "CREATE_COMPLETE", capture any outputs
                4. If status becomes "CREATE_FAILED", capture the error details from Events tab
                5. Return the final status and any relevant information
                
                Stack name to monitor: {stack_name}
                Maximum wait time: 15 minutes
                """)
                
                if progress_callback:
                    progress_callback("✅ Deployment monitoring completed")
                
                # Parse the result
                if "CREATE_COMPLETE" in result.response:
                    return {
                        'success': True,
                        'status': 'CREATE_COMPLETE',
                        'message': f'Stack {stack_name} deployed successfully',
                        'details': result.response,
                        'stack_name': stack_name,
                        'template_url': template_url
                    }
                elif "CREATE_FAILED" in result.response:
                    return {
                        'success': False,
                        'status': 'CREATE_FAILED',
                        'message': f'Stack {stack_name} deployment failed',
                        'details': result.response,
                        'stack_name': stack_name
                    }
                else:
                    return {
                        'success': True,
                        'status': 'IN_PROGRESS',
                        'message': f'Stack {stack_name} deployment in progress',
                        'details': result.response,
                        'stack_name': stack_name
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Nova-Act automation failed: {str(e)}',
                'stack_name': stack_name,
                'fallback': 'manual_deployment'
            }
    
    def check_stack_status(self, stack_name: str) -> Dict[str, Any]:
        """Check the status of a CloudFormation stack"""
        
        if not self.nova_act_available:
            return {
                'success': False,
                'error': 'Nova-Act SDK not available'
            }
        
        try:
            with self.NovaAct(
                starting_page="https://console.aws.amazon.com/cloudformation/home",
                api_key=self.api_key
            ) as browser:
                
                result = browser.act(f"""
                Check the status of CloudFormation stack: {stack_name}
                1. Find the stack in the list
                2. Check its current status
                3. If there are any errors, get details from the Events tab
                4. Return the current status and any relevant information
                """)
                
                return {
                    'success': True,
                    'stack_name': stack_name,
                    'status_info': result.response
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Status check failed: {str(e)}',
                'stack_name': stack_name
            }

# Global instance
direct_automation = DirectNovaActAutomation()

def deploy_with_direct_automation(template_url: str, stack_name: str, 
                                progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """
    Main function for direct Nova-Act automation deployment
    """
    return direct_automation.deploy_cloudformation_stack(template_url, stack_name, progress_callback)

def check_deployment_status_direct(stack_name: str) -> Dict[str, Any]:
    """
    Check deployment status using direct Nova-Act automation
    """
    return direct_automation.check_stack_status(stack_name)