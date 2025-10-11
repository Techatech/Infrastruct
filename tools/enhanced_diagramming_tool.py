import os
import tempfile
from datetime import datetime
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda, ECS
from diagrams.aws.database import RDS, DynamoDB, ElastiCache
from diagrams.aws.network import ELB, CloudFront, Route53, VPC, APIGateway
from diagrams.aws.storage import S3
from diagrams.aws.analytics import Kinesis, Glue
from diagrams.aws.integration import SQS, SNS
from diagrams.aws.security import IAM, Cognito
from diagrams.aws.management import Cloudwatch, CloudFormation
from diagrams.onprem.client import Users
from diagrams.onprem.network import Internet
import re

class EnhancedDiagramGenerator:
    def __init__(self):
        self.output_dir = "diagrams_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Service mapping for automatic detection
        self.service_mapping = {
            # Compute
            'ec2': EC2,
            'lambda': Lambda,
            'ecs': ECS,
            'server': EC2,
            'compute': EC2,
            
            # Database
            'rds': RDS,
            'dynamodb': DynamoDB,
            'database': RDS,
            'db': RDS,
            'redis': ElastiCache,
            'elasticache': ElastiCache,
            
            # Network
            'elb': ELB,
            'loadbalancer': ELB,
            'load balancer': ELB,
            'cloudfront': CloudFront,
            'cdn': CloudFront,
            'route53': Route53,
            'dns': Route53,
            'vpc': VPC,
            'api gateway': APIGateway,
            'apigateway': APIGateway,
            
            # Storage
            's3': S3,
            'storage': S3,
            'bucket': S3,
            
            # Analytics
            'kinesis': Kinesis,
            'glue': Glue,
            
            # Integration
            'sqs': SQS,
            'sns': SNS,
            'queue': SQS,
            'notification': SNS,
            
            # Security
            'iam': IAM,
            'cognito': Cognito,
            'auth': Cognito,
            'authentication': Cognito,
            
            # Management
            'cloudwatch': Cloudwatch,
            'monitoring': Cloudwatch,
            'cloudformation': CloudFormation,
            
            # External
            'users': Users,
            'internet': Internet,
            'user': Users
        }
    
    def parse_architecture_plan(self, plan_text: str) -> dict:
        """Parse architecture plan to extract components and relationships"""
        components = {}
        relationships = []
        
        # Convert to lowercase for easier parsing
        plan_lower = plan_text.lower()
        
        # Extract services mentioned in the plan
        for service_name, service_class in self.service_mapping.items():
            if service_name in plan_lower:
                # Count occurrences to handle multiple instances
                count = plan_lower.count(service_name)
                if count > 1:
                    for i in range(count):
                        components[f"{service_name}_{i+1}"] = {
                            'class': service_class,
                            'label': f"{service_name.title()} {i+1}"
                        }
                else:
                    components[service_name] = {
                        'class': service_class,
                        'label': service_name.title()
                    }
        
        # Extract relationships based on common patterns
        relationship_patterns = [
            (r'(\w+)\s+connects?\s+to\s+(\w+)', 'connects'),
            (r'(\w+)\s+sends?\s+to\s+(\w+)', 'sends'),
            (r'(\w+)\s+receives?\s+from\s+(\w+)', 'receives'),
            (r'(\w+)\s+→\s+(\w+)', 'flows'),
            (r'(\w+)\s+->\s+(\w+)', 'flows'),
            (r'(\w+)\s+through\s+(\w+)', 'through'),
        ]
        
        for pattern, relation_type in relationship_patterns:
            matches = re.findall(pattern, plan_lower)
            for match in matches:
                source, target = match
                if source in components and target in components:
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': relation_type
                    })
        
        return {
            'components': components,
            'relationships': relationships
        }
    
    def create_architecture_diagram(self, plan_text: str, title: str = "AWS Architecture") -> str:
        """Create a visual architecture diagram from the plan"""
        try:
            # Parse the plan
            architecture = self.parse_architecture_plan(plan_text)
            
            if not architecture['components']:
                return self.create_text_diagram(plan_text)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"architecture_{timestamp}"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create the diagram
            with Diagram(title, filename=filepath, show=False, direction="TB"):
                # Create component instances
                component_instances = {}
                
                # Group components by type for better organization
                compute_components = []
                database_components = []
                network_components = []
                storage_components = []
                other_components = []
                
                for comp_name, comp_info in architecture['components'].items():
                    instance = comp_info['class'](comp_info['label'])
                    component_instances[comp_name] = instance
                    
                    # Categorize components
                    if comp_info['class'] in [EC2, Lambda, ECS]:
                        compute_components.append(instance)
                    elif comp_info['class'] in [RDS, DynamoDB, ElastiCache]:
                        database_components.append(instance)
                    elif comp_info['class'] in [ELB, CloudFront, Route53, VPC, APIGateway]:
                        network_components.append(instance)
                    elif comp_info['class'] in [S3]:
                        storage_components.append(instance)
                    else:
                        other_components.append(instance)
                
                # Create clusters for better organization
                if len(architecture['components']) > 3:
                    if compute_components:
                        with Cluster("Compute Layer"):
                            for comp in compute_components:
                                pass
                    
                    if database_components:
                        with Cluster("Database Layer"):
                            for comp in database_components:
                                pass
                    
                    if network_components:
                        with Cluster("Network Layer"):
                            for comp in network_components:
                                pass
                
                # Create relationships
                for relationship in architecture['relationships']:
                    source = component_instances.get(relationship['source'])
                    target = component_instances.get(relationship['target'])
                    
                    if source and target:
                        if relationship['type'] == 'sends':
                            source >> Edge(label="sends") >> target
                        elif relationship['type'] == 'receives':
                            target >> Edge(label="receives") >> source
                        elif relationship['type'] == 'through':
                            source >> Edge(label="through") >> target
                        else:
                            source >> target
            
            # Return the path to the generated diagram
            png_path = f"{filepath}.png"
            if os.path.exists(png_path):
                return png_path
            else:
                return self.create_text_diagram(plan_text)
                
        except Exception as e:
            print(f"Error creating visual diagram: {e}")
            return self.create_text_diagram(plan_text)
    
    def create_text_diagram(self, plan_text: str) -> str:
        """Create a text-based diagram as fallback"""
        diagram_text = """
╔══════════════════════════════════════════════════════════════╗
║                    ARCHITECTURE DIAGRAM                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📱 Users                                                    ║
║     │                                                        ║
║     ▼                                                        ║
║  🌐 Internet Gateway                                         ║
║     │                                                        ║
║     ▼                                                        ║
║  ⚖️  Load Balancer                                           ║
║     │                                                        ║
║     ▼                                                        ║
║  🖥️  Application Servers                                     ║
║     │                                                        ║
║     ▼                                                        ║
║  🗄️  Database Layer                                          ║
║     │                                                        ║
║     ▼                                                        ║
║  📦 Storage Layer                                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Components Identified:
"""
        
        # Extract components from plan
        plan_lower = plan_text.lower()
        identified_components = []
        
        for service_name in self.service_mapping.keys():
            if service_name in plan_lower:
                identified_components.append(f"• {service_name.title()}")
        
        if identified_components:
            diagram_text += "\n".join(identified_components)
        else:
            diagram_text += "• Please provide more specific service details for better diagram generation"
        
        diagram_text += f"""

Data Flow:
• User requests → Load Balancer → Application Layer → Database
• Static content served via CDN
• Monitoring and logging across all layers

Recommended Tools:
• AWS Architecture Center diagrams
• draw.io with AWS icons
• Lucidchart AWS templates
"""
        
        return diagram_text
    
    def get_diagram_summary(self, plan_text: str) -> str:
        """Get a summary of the diagram components"""
        architecture = self.parse_architecture_plan(plan_text)
        
        summary = "Architecture Components:\n"
        for comp_name, comp_info in architecture['components'].items():
            summary += f"• {comp_info['label']}\n"
        
        if architecture['relationships']:
            summary += "\nData Flow:\n"
            for rel in architecture['relationships']:
                summary += f"• {rel['source'].title()} {rel['type']} {rel['target'].title()}\n"
        
        return summary