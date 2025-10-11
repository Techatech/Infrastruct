import re
from typing import Dict, List, Tuple

class PlantUMLDiagramGenerator:
    def __init__(self):
        self.aws_icons = {
            'users': 'actor "👥 Users" as users',
            'internet': 'cloud "🌐 Internet" as internet',
            'cloudfront': 'component "🚀 CloudFront" as cloudfront',
            'route53': 'component "🌍 Route53" as route53',
            'loadbalancer': 'component "⚖️ Load Balancer" as loadbalancer',
            'ec2': 'node "🖥️ EC2 Instance" as ec2',
            'lambda': 'component "⚡ Lambda" as lambda',
            'rds': 'database "🗄️ RDS" as rds',
            'dynamodb': 'database "📊 DynamoDB" as dynamodb',
            's3': 'storage "📦 S3 Bucket" as s3',
            'apigateway': 'interface "🔌 API Gateway" as apigateway',
            'vpc': 'package "🏠 VPC" as vpc',
            'iam': 'component "🔐 IAM" as iam',
            'cloudwatch': 'component "📈 CloudWatch" as cloudwatch'
        }
    
    def create_plantuml_diagram(self, plan_text: str, title: str = "AWS Architecture") -> str:
        """Create a PlantUML diagram from architecture plan"""
        components = self.parse_components(plan_text)
        relationships = self.parse_relationships(plan_text, components)
        
        plantuml_code = self.build_plantuml_diagram(components, relationships, title)
        
        return f"""
PlantUML Diagram Code:
```plantuml
{plantuml_code}
```

To view this diagram:
1. Copy the code above
2. Paste it into http://www.plantuml.com/plantuml/
3. Or use PlantUML plugins in your IDE
4. Or integrate with documentation tools

{self.create_text_summary(components, relationships)}
"""
    
    def parse_components(self, plan_text: str) -> List[str]:
        """Parse components from the architecture plan"""
        components = []
        plan_lower = plan_text.lower()
        
        service_patterns = {
            'users': r'users?|clients?|customers?',
            'internet': r'internet|web|public',
            'cloudfront': r'cloudfront|cdn|content delivery',
            'route53': r'route\s?53|dns|domain',
            'loadbalancer': r'load\s?balancer|elb|alb',
            'ec2': r'ec2|server|instance|compute',
            'lambda': r'lambda|function|serverless',
            'rds': r'rds|database|mysql|postgres|aurora',
            'dynamodb': r'dynamodb|nosql|document database',
            's3': r's3|bucket|storage|static files',
            'apigateway': r'api\s?gateway|api|rest api',
            'vpc': r'vpc|virtual private cloud|network',
            'iam': r'iam|identity|access|authentication',
            'cloudwatch': r'cloudwatch|monitoring|logs|metrics'
        }
        
        for service, pattern in service_patterns.items():
            if re.search(pattern, plan_lower):
                components.append(service)
        
        return components
    
    def parse_relationships(self, plan_text: str, components: List[str]) -> List[Tuple[str, str, str]]:
        """Parse relationships with labels"""
        relationships = []
        
        # Define relationships with labels
        flow_patterns = [
            ('users', 'internet', 'requests'),
            ('internet', 'route53', 'DNS lookup'),
            ('route53', 'cloudfront', 'routes to'),
            ('internet', 'cloudfront', 'requests'),
            ('cloudfront', 's3', 'serves from'),
            ('internet', 'loadbalancer', 'requests'),
            ('loadbalancer', 'ec2', 'distributes to'),
            ('ec2', 'rds', 'queries'),
            ('ec2', 'dynamodb', 'reads/writes'),
            ('users', 'apigateway', 'API calls'),
            ('apigateway', 'lambda', 'invokes'),
            ('lambda', 'dynamodb', 'queries'),
            ('lambda', 'rds', 'queries'),
            ('ec2', 's3', 'stores/retrieves'),
            ('lambda', 's3', 'stores/retrieves')
        ]
        
        # Only include relationships where both components exist
        for source, target, label in flow_patterns:
            if source in components and target in components:
                relationships.append((source, target, label))
        
        return relationships
    
    def build_plantuml_diagram(self, components: List[str], relationships: List[Tuple], title: str) -> str:
        """Build the PlantUML diagram code"""
        lines = []
        
        # Start PlantUML
        lines.append("@startuml")
        lines.append(f"title {title}")
        lines.append("")
        lines.append("!theme aws-orange")
        lines.append("")
        
        # Define components
        lines.append("' Define components")
        for component in components:
            if component in self.aws_icons:
                lines.append(self.aws_icons[component])
        
        lines.append("")
        lines.append("' Define relationships")
        
        # Add relationships
        for source, target, label in relationships:
            lines.append(f"{source} --> {target} : {label}")
        
        # Add layout hints
        lines.append("")
        lines.append("' Layout hints")
        if 'users' in components and 'internet' in components:
            lines.append("users -[hidden]-> internet")
        
        # Group related components
        if any(comp in components for comp in ['ec2', 'lambda', 'loadbalancer']):
            lines.append("")
            lines.append("package \"Compute Layer\" {")
            for comp in ['loadbalancer', 'ec2', 'lambda']:
                if comp in components:
                    lines.append(f"  {comp}")
            lines.append("}")
        
        if any(comp in components for comp in ['rds', 'dynamodb', 's3']):
            lines.append("")
            lines.append("package \"Data Layer\" {")
            for comp in ['rds', 'dynamodb', 's3']:
                if comp in components:
                    lines.append(f"  {comp}")
            lines.append("}")
        
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)
    
    def create_text_summary(self, components: List[str], relationships: List[Tuple]) -> str:
        """Create a text summary of the diagram"""
        summary = "Architecture Summary:\n"
        summary += "=" * 50 + "\n"
        
        # Group components by layer
        layers = {
            'Presentation': ['users', 'internet'],
            'Network': ['route53', 'cloudfront', 'loadbalancer', 'apigateway'],
            'Compute': ['ec2', 'lambda'],
            'Data': ['rds', 'dynamodb', 's3'],
            'Management': ['iam', 'cloudwatch', 'vpc']
        }
        
        for layer_name, layer_components in layers.items():
            layer_items = [comp for comp in layer_components if comp in components]
            if layer_items:
                summary += f"\n{layer_name} Layer:\n"
                for comp in layer_items:
                    icon_def = self.aws_icons.get(comp, comp)
                    service_name = icon_def.split('"')[1] if '"' in icon_def else comp
                    summary += f"• {service_name}\n"
        
        summary += "\nData Flow:\n"
        for source, target, label in relationships:
            source_name = self.aws_icons.get(source, source).split('"')[1] if '"' in self.aws_icons.get(source, source) else source
            target_name = self.aws_icons.get(target, target).split('"')[1] if '"' in self.aws_icons.get(target, target) else target
            summary += f"• {source_name} → {target_name} ({label})\n"
        
        return summary

def create_plantuml_diagram(plan_text: str, title: str = "AWS Architecture") -> str:
    """Main function to create PlantUML diagram"""
    generator = PlantUMLDiagramGenerator()
    return generator.create_plantuml_diagram(plan_text, title)