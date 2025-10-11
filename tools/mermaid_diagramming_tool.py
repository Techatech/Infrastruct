import re
from typing import Dict, List, Tuple

class MermaidDiagramGenerator:
    def __init__(self):
        self.service_mapping = {
            'users': 'Users[👥 Users]',
            'internet': 'Internet[🌐 Internet]',
            'cloudfront': 'CloudFront[🚀 CloudFront CDN]',
            'route53': 'Route53[🌍 Route 53 DNS]',
            'loadbalancer': 'LoadBalancer[⚖️ Load Balancer]',
            'ec2': 'EC2[🖥️ EC2 Instance]',
            'lambda': 'Lambda[⚡ Lambda Function]',
            'rds': 'RDS[🗄️ RDS Database]',
            'dynamodb': 'DynamoDB[📊 DynamoDB]',
            's3': 'S3[📦 S3 Bucket]',
            'apigateway': 'APIGateway[🔌 API Gateway]',
            'vpc': 'VPC[🏠 VPC]',
            'iam': 'IAM[🔐 IAM]',
            'cloudwatch': 'CloudWatch[📈 CloudWatch]'
        }
    
    def create_mermaid_diagram(self, plan_text: str, title: str = "AWS Architecture") -> str:
        """Create a Mermaid diagram from architecture plan"""
        components = self.parse_components(plan_text)
        relationships = self.parse_relationships(plan_text, components)
        
        mermaid_code = self.build_mermaid_diagram(components, relationships, title)
        
        return f"""
Mermaid Diagram Code:
```mermaid
{mermaid_code}
```

To view this diagram:
1. Copy the code above
2. Paste it into https://mermaid.live/
3. Or use it in GitHub/GitLab markdown
4. Or integrate with documentation tools

{self.create_text_representation(components, relationships)}
"""
    
    def parse_components(self, plan_text: str) -> List[str]:
        """Parse components from the architecture plan"""
        components = []
        plan_lower = plan_text.lower()
        
        for service, mermaid_def in self.service_mapping.items():
            if service in plan_lower or self.check_service_patterns(service, plan_lower):
                components.append(service)
        
        return components
    
    def check_service_patterns(self, service: str, plan_text: str) -> bool:
        """Check for service-specific patterns"""
        patterns = {
            'ec2': r'server|instance|compute|virtual machine',
            'rds': r'database|mysql|postgres|aurora|sql',
            's3': r'bucket|storage|static files|object storage',
            'cloudfront': r'cdn|content delivery|cache',
            'route53': r'dns|domain|routing',
            'loadbalancer': r'load balancer|elb|alb|balancing',
            'lambda': r'function|serverless|event-driven',
            'dynamodb': r'nosql|document database|key-value',
            'apigateway': r'api|rest|http api|gateway',
            'vpc': r'network|virtual private cloud|subnet',
            'iam': r'identity|access|authentication|authorization',
            'cloudwatch': r'monitoring|logs|metrics|alerts'
        }
        
        pattern = patterns.get(service, '')
        return bool(pattern and re.search(pattern, plan_text))
    
    def parse_relationships(self, plan_text: str, components: List[str]) -> List[Tuple[str, str]]:
        """Parse relationships between components"""
        relationships = []
        
        # Common AWS architecture flows
        common_flows = [
            ('users', 'internet'),
            ('internet', 'route53'),
            ('route53', 'cloudfront'),
            ('internet', 'cloudfront'),
            ('cloudfront', 's3'),
            ('internet', 'loadbalancer'),
            ('loadbalancer', 'ec2'),
            ('ec2', 'rds'),
            ('ec2', 'dynamodb'),
            ('users', 'apigateway'),
            ('apigateway', 'lambda'),
            ('lambda', 'dynamodb'),
            ('lambda', 'rds'),
            ('ec2', 's3'),
            ('lambda', 's3')
        ]
        
        # Only include relationships where both components exist
        for source, target in common_flows:
            if source in components and target in components:
                relationships.append((source, target))
        
        return relationships
    
    def build_mermaid_diagram(self, components: List[str], relationships: List[Tuple], title: str) -> str:
        """Build the Mermaid diagram code"""
        lines = []
        
        # Start with flowchart
        lines.append("flowchart TD")
        lines.append(f"    title[\"{title}\"]")
        lines.append("")
        
        # Define nodes
        lines.append("    %% Define nodes")
        for component in components:
            if component in self.service_mapping:
                lines.append(f"    {self.service_mapping[component]}")
        
        lines.append("")
        lines.append("    %% Define relationships")
        
        # Add relationships
        for source, target in relationships:
            lines.append(f"    {source} --> {target}")
        
        # Add styling
        lines.append("")
        lines.append("    %% Styling")
        lines.append("    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff")
        lines.append("    classDef user fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff")
        lines.append("    classDef network fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff")
        lines.append("    classDef compute fill:#FF5722,stroke:#D84315,stroke-width:2px,color:#fff")
        lines.append("    classDef storage fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff")
        lines.append("    classDef database fill:#795548,stroke:#5D4037,stroke-width:2px,color:#fff")
        
        # Apply classes
        lines.append("")
        for component in components:
            css_class = self.get_component_class(component)
            lines.append(f"    class {component} {css_class}")
        
        return "\n".join(lines)
    
    def get_component_class(self, component: str) -> str:
        """Get CSS class for component styling"""
        class_mapping = {
            'users': 'user',
            'internet': 'network',
            'route53': 'network',
            'cloudfront': 'network',
            'loadbalancer': 'network',
            'apigateway': 'network',
            'ec2': 'compute',
            'lambda': 'compute',
            'rds': 'database',
            'dynamodb': 'database',
            's3': 'storage',
            'vpc': 'network',
            'iam': 'aws',
            'cloudwatch': 'aws'
        }
        return class_mapping.get(component, 'aws')
    
    def create_text_representation(self, components: List[str], relationships: List[Tuple]) -> str:
        """Create a text representation of the diagram"""
        text = "Text Representation:\n"
        text += "=" * 50 + "\n"
        
        text += "Components:\n"
        for component in components:
            service_name = self.service_mapping.get(component, component).split('[')[1].split(']')[0]
            text += f"• {service_name}\n"
        
        text += "\nData Flow:\n"
        for source, target in relationships:
            source_name = self.service_mapping.get(source, source).split('[')[1].split(']')[0]
            target_name = self.service_mapping.get(target, target).split('[')[1].split(']')[0]
            text += f"• {source_name} → {target_name}\n"
        
        return text

def create_mermaid_diagram(plan_text: str, title: str = "AWS Architecture") -> str:
    """Main function to create Mermaid diagram"""
    generator = MermaidDiagramGenerator()
    return generator.create_mermaid_diagram(plan_text, title)