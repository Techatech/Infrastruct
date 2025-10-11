#!/usr/bin/env python3
"""
Test script for direct Nova-Act deployment functionality
"""

from tools.enhanced_deployer_tool import deploy_to_aws_direct

# Sample CloudFormation template for testing
sample_template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Test deployment - Simple S3 bucket'

Resources:
  TestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'test-bucket-${AWS::StackName}-${AWS::AccountId}'
      PublicReadPolicy: false
      
Outputs:
  BucketName:
    Description: 'Name of the created S3 bucket'
    Value: !Ref TestBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'
"""

def test_direct_deployment():
    """Test the direct deployment functionality with login awareness"""
    print("🧪 Testing Login-Aware Direct Nova-Act Deployment")
    print("=" * 60)
    
    stack_name = "test-login-aware-deployment"
    
    print(f"📋 Stack Name: {stack_name}")
    print(f"📄 Template: Simple S3 bucket")
    print(f"🔐 Login Handling: Enhanced with 5-minute timeout")
    print(f"🚀 Launching deployment...")
    print()
    
    try:
        # This should:
        # 1. Save template to iac_templates/
        # 2. Upload to S3 bucket 'infrastruct'
        # 3. Open Chrome browser
        # 4. Check for AWS login screen
        # 5. Wait up to 5 minutes for user login
        # 6. Resume automation after successful login
        result = deploy_to_aws_direct(sample_template, stack_name)
        
        print("✅ DEPLOYMENT RESULT:")
        print(result)
        
        print("\n" + "=" * 60)
        print("🔐 LOGIN TESTING NOTES:")
        print("• If AWS login screen appears, you have 5 minutes to log in")
        print("• Automation will pause and wait for successful login")
        print("• After login, deployment will resume automatically")
        print("• Watch Chrome browser for real-time progress")
        print("• Check VS Code Output panel for Nova-Act logs")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def test_login_instructions():
    """Test the login instruction generation"""
    print("\n🧪 Testing Login Instructions Generation")
    print("=" * 50)
    
    from tools.enhanced_deployer_tool import deployment_manager
    
    login_guide = deployment_manager.create_login_instructions()
    print("📋 GENERATED LOGIN INSTRUCTIONS:")
    print(login_guide)

if __name__ == "__main__":
    test_direct_deployment()
    test_login_instructions()