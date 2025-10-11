#!/usr/bin/env python3
"""
Test script for Kiro Nova-Act deployment functionality
"""

from kiro_nova_act_deployer import deploy_to_aws_direct

def test_kiro_deployment():
    """Test the Kiro Nova-Act deployment"""
    print("🧪 Testing Kiro Nova-Act Deployment")
    print("=" * 50)
    
    # Sample CloudFormation template
    test_template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Kiro Nova-Act Test Deployment - Simple S3 bucket'

Resources:
  KiroTestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'kiro-test-${AWS::StackName}-${AWS::AccountId}'
      PublicReadPolicy: false
      
Outputs:
  BucketName:
    Description: 'Name of the created S3 bucket'
    Value: !Ref KiroTestBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'
"""
    
    stack_name = "kiro-nova-act-test"
    
    print(f"📋 Stack Name: {stack_name}")
    print(f"📄 Template: Simple S3 bucket for testing")
    print(f"🚀 Launching Kiro Nova-Act deployment...")
    print()
    
    try:
        result = deploy_to_aws_direct(test_template, stack_name)
        
        print("✅ KIRO DEPLOYMENT RESULT:")
        print("=" * 50)
        print(result)
        
        print("\n" + "=" * 50)
        print("🎯 EXPECTED BEHAVIOR:")
        print("✅ Chrome should open with AWS CloudFormation Console")
        print("✅ VS Code should open with Nova-Act instruction file")
        print("✅ Template should be uploaded to S3 (if permissions allow)")
        print("✅ Instruction file should be created locally")
        
        print("\n📋 NEXT STEPS:")
        print("1. Check if Chrome opened with AWS Console")
        print("2. Check if VS Code opened with instruction file")
        print("3. In VS Code: Press Ctrl+Shift+P")
        print("4. Type: 'Nova-Act: Start Browser Automation'")
        print("5. Follow the automation process")
        
        print("\n🔧 ALTERNATIVE LAUNCHER:")
        print("Run: python launch_nova_act_kiro.py")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_kiro_deployment()