#!/usr/bin/env python3
"""
Test script for enhanced Nova-Act deployment with boto3 S3 upload and login detection
"""

from tools.enhanced_deployer_tool import deploy_to_aws_direct

# Sample CloudFormation template for testing
sample_template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Enhanced deployment test - Simple S3 bucket with boto3 upload'

Resources:
  TestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'enhanced-test-${AWS::StackName}-${AWS::AccountId}'
      PublicReadPolicy: false
      
Outputs:
  BucketName:
    Description: 'Name of the created S3 bucket'
    Value: !Ref TestBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'
"""

def test_enhanced_deployment():
    """Test the enhanced deployment with boto3 S3 upload and login detection"""
    print("🧪 Testing Enhanced Nova-Act Deployment")
    print("=" * 60)
    
    stack_name = "enhanced-deployment-test"
    
    print(f"📋 Stack Name: {stack_name}")
    print(f"📄 Template: Simple S3 bucket")
    print(f"🔧 S3 Upload: boto3 with AWS CLI fallback")
    print(f"🔐 Login Detection: Pre-check AWS Console access")
    print(f"🤖 Automation: Direct Nova-Act trigger via VS Code")
    print(f"🚀 Launching enhanced deployment...")
    print()
    
    try:
        # This enhanced version should:
        # 1. Save template to iac_templates/
        # 2. Upload to S3 using boto3 (fallback to AWS CLI)
        # 3. Check AWS Console login status before starting
        # 4. Open Chrome browser
        # 5. Trigger Nova-Act automation via VS Code commands
        # 6. Provide appropriate instructions based on login status
        result = deploy_to_aws_direct(sample_template, stack_name)
        
        print("✅ ENHANCED DEPLOYMENT RESULT:")
        print(result)
        
        print("\n" + "=" * 60)
        print("🔧 ENHANCEMENT TESTING NOTES:")
        print("• S3 upload now uses boto3 with AWS CLI fallback")
        print("• Login status is checked before starting automation")
        print("• Chrome launches automatically with AWS Console")
        print("• VS Code Nova-Act commands are triggered directly")
        print("• Instructions adapt based on login requirements")
        print("• 5-minute login timeout only applies if login needed")
        
        print("\n📋 NEXT STEPS:")
        print("1. Check if Chrome opened with AWS CloudFormation Console")
        print("2. If login screen: Complete authentication within 5 minutes")
        print("3. If already logged in: Automation should start immediately")
        print("4. Use VS Code Command Palette: Ctrl+Shift+P → 'Nova-Act: Start Browser Automation'")
        print("5. Monitor progress in both Chrome browser and VS Code Output panel")
        
    except Exception as e:
        print(f"❌ Enhanced deployment test failed: {str(e)}")

def test_s3_upload_methods():
    """Test both S3 upload methods"""
    print("\n🧪 Testing S3 Upload Methods")
    print("=" * 50)
    
    from tools.enhanced_deployer_tool import deployment_manager
    import tempfile
    import os
    
    # Create a test file
    test_content = "# Test CloudFormation Template\nAWSTemplateFormatVersion: '2010-09-09'"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        print(f"📄 Test file created: {test_file_path}")
        
        # Test boto3 upload
        print("\n🔧 Testing boto3 S3 upload...")
        success, message = deployment_manager.upload_template_to_s3_boto3(test_file_path, "test-boto3-upload.yaml")
        print(f"Boto3 result: {message}")
        
        # Test combined upload (boto3 + CLI fallback)
        print("\n🔧 Testing combined S3 upload...")
        success, message = deployment_manager.upload_template_to_s3(test_file_path, "test-combined-upload.yaml")
        print(f"Combined result: {message}")
        
    finally:
        # Clean up test file
        try:
            os.unlink(test_file_path)
            print(f"🧹 Cleaned up test file: {test_file_path}")
        except:
            pass

def test_login_detection():
    """Test AWS Console login detection"""
    print("\n🧪 Testing AWS Console Login Detection")
    print("=" * 50)
    
    from tools.enhanced_deployer_tool import deployment_manager
    
    aws_console_url = "https://console.aws.amazon.com/cloudformation/home"
    
    print(f"🔐 Checking login status for: {aws_console_url}")
    login_required, status_message = deployment_manager.check_cloudformation_access(aws_console_url)
    
    print(f"Login required: {login_required}")
    print(f"Status: {status_message}")
    
    if login_required:
        print("🔐 Login will be required - 5-minute timeout will be applied")
    else:
        print("✅ Already logged in - automation can start immediately")

if __name__ == "__main__":
    test_enhanced_deployment()
    test_s3_upload_methods()
    test_login_detection()