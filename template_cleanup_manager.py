#!/usr/bin/env python3
"""
Template Cleanup Manager
Handles cleanup of local templates and S3 files when chat sessions are deleted
"""

import os
import glob
import re
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TemplateCleanupManager:
    def __init__(self):
        self.templates_folder = os.getenv('IAC_TEMPLATES_FOLDER', 'iac_templates')
        self.s3_bucket = os.getenv('S3_BUCKET_NAME', 'infrastruct')
        self.aws_region = os.getenv('S3_BUCKET_AWS_REGION', 'us-east-1')
        
    def extract_stack_name_from_session(self, session_title: str, session_id: str) -> Optional[str]:
        """Extract likely stack name from session title or ID"""
        # Try to extract stack name from session title
        # Common patterns: "Deploy X", "Create X infrastructure", etc.
        
        # Clean the title to get potential stack name
        title_words = session_title.lower().replace('-', ' ').replace('_', ' ').split()
        
        # Remove common words
        common_words = {'deploy', 'create', 'build', 'infrastructure', 'aws', 'stack', 'template', 'for', 'a', 'an', 'the'}
        filtered_words = [word for word in title_words if word not in common_words and len(word) > 2]
        
        if filtered_words:
            # Use the first meaningful word as potential stack name
            potential_stack_name = filtered_words[0]
            return potential_stack_name
        
        # Fallback: try to extract from session_id
        # Session IDs often contain meaningful parts
        if '_' in session_id:
            parts = session_id.split('_')
            for part in parts:
                if len(part) > 3 and not part.isdigit():
                    return part.lower()
        
        return None
    
    def find_related_local_files(self, session_title: str, session_id: str) -> List[str]:
        """Find local template files related to a chat session"""
        related_files = []
        
        # Get potential stack name
        stack_name = self.extract_stack_name_from_session(session_title, session_id)
        
        if not stack_name:
            return related_files
        
        # Look for files in templates folder
        if os.path.exists(self.templates_folder):
            # Pattern 1: {stack_name}-template.yaml
            pattern1 = os.path.join(self.templates_folder, f"{stack_name}-template.yaml")
            if os.path.exists(pattern1):
                related_files.append(pattern1)
            
            # Pattern 2: {stack_name}-template.json
            pattern2 = os.path.join(self.templates_folder, f"{stack_name}-template.json")
            if os.path.exists(pattern2):
                related_files.append(pattern2)
            
            # Pattern 3: Look for files containing the stack name
            all_files = glob.glob(os.path.join(self.templates_folder, "*"))
            for file_path in all_files:
                filename = os.path.basename(file_path).lower()
                if stack_name in filename and file_path not in related_files:
                    related_files.append(file_path)
        
        # Also look for Nova-Act instruction files
        nova_pattern = f"nova_deploy_{stack_name.replace('-', '_')}.json"
        if os.path.exists(nova_pattern):
            related_files.append(nova_pattern)
        
        return related_files
    
    def delete_s3_template(self, stack_name: str) -> Tuple[bool, str]:
        """Delete template from S3 bucket"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            s3_client = boto3.client('s3', region_name=self.aws_region)
            
            # Try different possible S3 key patterns
            possible_keys = [
                f"{stack_name}-template.yaml",
                f"{stack_name}-template.json",
                f"{stack_name}.yaml",
                f"{stack_name}.json"
            ]
            
            deleted_files = []
            
            for s3_key in possible_keys:
                try:
                    # Check if object exists
                    s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
                    
                    # Delete the object
                    s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
                    deleted_files.append(s3_key)
                    
                except ClientError as e:
                    if e.response['Error']['Code'] != '404':
                        # Not a "not found" error, so it's a real error
                        continue
            
            if deleted_files:
                return True, f"✅ Deleted S3 files: {', '.join(deleted_files)}"
            else:
                return True, "ℹ️ No S3 files found to delete"
                
        except NoCredentialsError:
            return False, "❌ AWS credentials not available for S3 cleanup"
        except Exception as e:
            return False, f"❌ S3 cleanup failed: {str(e)}"
    
    def cleanup_session_files(self, session_title: str, session_id: str) -> dict:
        """Comprehensive cleanup of all files related to a chat session"""
        cleanup_result = {
            'local_files_deleted': [],
            'local_files_failed': [],
            's3_cleanup_success': False,
            's3_cleanup_message': '',
            'total_files_cleaned': 0
        }
        
        # Find and delete local files
        related_files = self.find_related_local_files(session_title, session_id)
        
        for file_path in related_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleanup_result['local_files_deleted'].append(file_path)
                    cleanup_result['total_files_cleaned'] += 1
            except Exception as e:
                cleanup_result['local_files_failed'].append(f"{file_path}: {str(e)}")
        
        # Try S3 cleanup
        stack_name = self.extract_stack_name_from_session(session_title, session_id)
        if stack_name:
            s3_success, s3_message = self.delete_s3_template(stack_name)
            cleanup_result['s3_cleanup_success'] = s3_success
            cleanup_result['s3_cleanup_message'] = s3_message
        
        return cleanup_result
    
    def bulk_cleanup_all_templates(self) -> dict:
        """Clean up all templates and Nova-Act files (for bulk session deletion)"""
        cleanup_result = {
            'local_files_deleted': [],
            'local_files_failed': [],
            's3_cleanup_attempted': False,
            's3_cleanup_message': '',
            'total_files_cleaned': 0
        }
        
        # Clean up local templates folder
        if os.path.exists(self.templates_folder):
            template_patterns = [
                os.path.join(self.templates_folder, "*.yaml"),
                os.path.join(self.templates_folder, "*.json"),
                os.path.join(self.templates_folder, "*.txt")
            ]
            
            for pattern in template_patterns:
                files = glob.glob(pattern)
                for file_path in files:
                    try:
                        os.remove(file_path)
                        cleanup_result['local_files_deleted'].append(file_path)
                        cleanup_result['total_files_cleaned'] += 1
                    except Exception as e:
                        cleanup_result['local_files_failed'].append(f"{file_path}: {str(e)}")
        
        # Clean up Nova-Act instruction files
        nova_files = glob.glob("nova_deploy_*.json")
        for file_path in nova_files:
            try:
                os.remove(file_path)
                cleanup_result['local_files_deleted'].append(file_path)
                cleanup_result['total_files_cleaned'] += 1
            except Exception as e:
                cleanup_result['local_files_failed'].append(f"{file_path}: {str(e)}")
        
        # Note: For bulk cleanup, we don't attempt S3 cleanup as it would require
        # listing all objects in the bucket, which might be too aggressive
        cleanup_result['s3_cleanup_message'] = "ℹ️ S3 cleanup skipped for bulk operation (too aggressive)"
        
        return cleanup_result

# Global instance
template_cleanup = TemplateCleanupManager()