import re
from typing import Dict, List, Tuple

class ASCIIDiagramGenerator:
    def __init__(self):
        # Unicode box drawing characters
        self.chars = {
            'horizontal': '─',
            'vertical': '│',
            'top_left': '┌',
            'top_right': '┐',
            'bottom_left': '└',
            'bottom_right': '┘',
            'cross': '┼',
            'tee_down': '┬',
            'tee_up': '┴',
            'tee_right': '├',
            'tee_left': '┤',
            'arrow_right': '→',
            'arrow_left': '←',
            'arrow_up': '↑',
            'arrow_down': '↓',
            'double_arrow': '↔'
        }
        
        # Service icons using emojis
        self.service_icons = {
            'users': '👥',
            'internet': '🌐',
            'cdn': '🚀',
            'cloudfront': '🚀',
            'loadbalancer': '⚖️',
            'elb': '⚖️',
            'alb': '⚖️',
            'ec2': '🖥️',
            'server': '🖥️',
            'lambda': '⚡',
            'function': '⚡',
            'database': '🗄️',
            'rds': '🗄️',
            'dynamodb': '📊',
            's3': '📦',
            'storage': '📦',
            'bucket': '📦',
            'route53': '🌍',
            'dns': '🌍',
            'api': '🔌',
            'apigateway': '🔌',
            'vpc': '🏠',
            'security': '🔒',
            'iam': '🔐',
            'monitoring': '📈',
            'cloudwatch': '📈',
            'queue': '📬',
            'sqs': '📬',
            'notification': '📢',
            'sns': '📢'
        }
    
    def create_architecture_diagram(self, plan_text: str, title: str = "AWS Architecture") -> str:
        """Create an enhanced ASCII diagram from architecture plan"""
        components = self.parse_components(plan_text)
        relationships = self.parse_relationships(plan_text)
        
        if not components:
            return self.create_generic_diagram(plan_text, title)
        
        # Create the diagram
        diagram = self.build_diagram(components, relationships, title)
        return diagram
    
    def parse_components(self, plan_text: str) -> List[Dict]:
        """Parse components from the architecture plan"""
        components = []
        plan_lower = plan_text.lower()
        
        # Common AWS services and their patterns
        service_patterns = {
            'users': r'users?|clients?|customers?',
            'internet': r'internet|web|public',
            'cloudfront': r'cloudfront|cdn|content delivery',
            'route53': r'route\s?53|dns|domain',
            'loadbalancer': r'load\s?balancer|elb|alb|application load balancer',
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
                components.append({
                    'name': service,
                    'icon': self.service_icons.get(service, '📋'),
                    'label': service.replace('_', ' ').title()
                })
        
        return components
    
    def parse_relationships(self, plan_text: str) -> List[Tuple[str, str]]:
        """Parse relationships between components"""
        relationships = []
        plan_lower = plan_text.lower()
        
        # Common flow patterns
        flow_patterns = [
            ('users', 'internet'),
            ('internet', 'cloudfront'),
            ('internet', 'route53'),
            ('route53', 'cloudfront'),
            ('cloudfront', 's3'),
            ('cloudfront', 'loadbalancer'),
            ('loadbalancer', 'ec2'),
            ('ec2', 'rds'),
            ('ec2', 'dynamodb'),
            ('apigateway', 'lambda'),
            ('lambda', 'dynamodb'),
            ('lambda', 'rds')
        ]
        
        # Check which relationships exist based on components mentioned
        mentioned_services = []
        for service in self.service_icons.keys():
            if service in plan_lower:
                mentioned_services.append(service)
        
        for source, target in flow_patterns:
            if source in mentioned_services and target in mentioned_services:
                relationships.append((source, target))
        
        return relationships
    
    def build_diagram(self, components: List[Dict], relationships: List[Tuple], title: str) -> str:
        """Build the ASCII diagram"""
        diagram_lines = []
        
        # Title
        title_line = f"╔{'═' * (len(title) + 4)}╗"
        title_content = f"║  {title}  ║"
        title_bottom = f"╚{'═' * (len(title) + 4)}╝"
        
        diagram_lines.extend([title_line, title_content, title_bottom, ""])
        
        # Create component layout based on typical AWS architecture
        if len(components) <= 3:
            return self.create_simple_layout(components, relationships, diagram_lines)
        elif len(components) <= 6:
            return self.create_medium_layout(components, relationships, diagram_lines)
        else:
            return self.create_complex_layout(components, relationships, diagram_lines)
    
    def create_simple_layout(self, components: List[Dict], relationships: List[Tuple], diagram_lines: List[str]) -> str:
        """Create a simple vertical layout"""
        diagram_lines.append("┌─────────────────────────────────────────────┐")
        diagram_lines.append("│              SIMPLE ARCHITECTURE           │")
        diagram_lines.append("├─────────────────────────────────────────────┤")
        diagram_lines.append("│                                             │")
        
        for i, comp in enumerate(components):
            icon = comp['icon']
            label = comp['label']
            
            if i == 0:
                diagram_lines.append(f"│  {icon} {label:<35} │")
            else:
                diagram_lines.append("│                     │                       │")
                diagram_lines.append("│                     ▼                       │")
                diagram_lines.append(f"│  {icon} {label:<35} │")
        
        diagram_lines.append("│                                             │")
        diagram_lines.append("└─────────────────────────────────────────────┘")
        
        return "\n".join(diagram_lines)
    
    def create_medium_layout(self, components: List[Dict], relationships: List[Tuple], diagram_lines: List[str]) -> str:
        """Create a medium complexity layout"""
        diagram_lines.append("┌─────────────────────────────────────────────────────────────┐")
        diagram_lines.append("│                    MEDIUM ARCHITECTURE                      │")
        diagram_lines.append("├─────────────────────────────────────────────────────────────┤")
        diagram_lines.append("│                                                             │")
        
        # Arrange in layers
        layers = self.arrange_in_layers(components)
        
        for layer_idx, layer in enumerate(layers):
            if layer_idx > 0:
                diagram_lines.append("│                           │                             │")
                diagram_lines.append("│                           ▼                             │")
            
            if len(layer) == 1:
                comp = layer[0]
                diagram_lines.append(f"│           {comp['icon']} {comp['label']:<35}           │")
            else:
                # Side by side
                left = layer[0] if len(layer) > 0 else {'icon': '', 'label': ''}
                right = layer[1] if len(layer) > 1 else {'icon': '', 'label': ''}
                diagram_lines.append(f"│  {left['icon']} {left['label']:<15} ←→ {right['icon']} {right['label']:<15}  │")
        
        diagram_lines.append("│                                                             │")
        diagram_lines.append("└─────────────────────────────────────────────────────────────┘")
        
        return "\n".join(diagram_lines)
    
    def create_complex_layout(self, components: List[Dict], relationships: List[Tuple], diagram_lines: List[str]) -> str:
        """Create a complex multi-tier layout"""
        diagram_lines.append("┌─────────────────────────────────────────────────────────────────────┐")
        diagram_lines.append("│                        COMPLEX ARCHITECTURE                        │")
        diagram_lines.append("├─────────────────────────────────────────────────────────────────────┤")
        diagram_lines.append("│                                                                     │")
        diagram_lines.append("│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │")
        diagram_lines.append("│  │ PRESENTATION│    │   BUSINESS  │    │    DATA     │           │")
        diagram_lines.append("│  │    LAYER    │    │    LAYER    │    │   LAYER     │           │")
        diagram_lines.append("│  └─────────────┘    └─────────────┘    └─────────────┘           │")
        diagram_lines.append("│         │                   │                   │                 │")
        
        # Distribute components across layers
        presentation = [c for c in components if c['name'] in ['users', 'internet', 'cloudfront', 'route53']]
        business = [c for c in components if c['name'] in ['loadbalancer', 'ec2', 'lambda', 'apigateway']]
        data = [c for c in components if c['name'] in ['rds', 'dynamodb', 's3']]
        
        max_layer_size = max(len(presentation), len(business), len(data))
        
        for i in range(max_layer_size):
            p_comp = presentation[i] if i < len(presentation) else {'icon': ' ', 'label': ''}
            b_comp = business[i] if i < len(business) else {'icon': ' ', 'label': ''}
            d_comp = data[i] if i < len(data) else {'icon': ' ', 'label': ''}
            
            diagram_lines.append(f"│    {p_comp['icon']} {p_comp['label']:<8}      {b_comp['icon']} {b_comp['label']:<8}      {d_comp['icon']} {d_comp['label']:<8}    │")
            
            if i < max_layer_size - 1:
                diagram_lines.append("│         │                   │                   │                 │")
        
        diagram_lines.append("│                                                                     │")
        diagram_lines.append("└─────────────────────────────────────────────────────────────────────┘")
        
        return "\n".join(diagram_lines)
    
    def arrange_in_layers(self, components: List[Dict]) -> List[List[Dict]]:
        """Arrange components in logical layers"""
        layers = []
        
        # Define layer priorities
        layer_priority = {
            'users': 0, 'internet': 0,
            'route53': 1, 'cloudfront': 1,
            'loadbalancer': 2, 'apigateway': 2,
            'ec2': 3, 'lambda': 3,
            'rds': 4, 'dynamodb': 4, 's3': 4
        }
        
        # Group by layers
        layer_groups = {}
        for comp in components:
            layer = layer_priority.get(comp['name'], 5)
            if layer not in layer_groups:
                layer_groups[layer] = []
            layer_groups[layer].append(comp)
        
        # Convert to ordered list
        for layer_num in sorted(layer_groups.keys()):
            layers.append(layer_groups[layer_num])
        
        return layers
    
    def create_generic_diagram(self, plan_text: str, title: str) -> str:
        """Create a generic diagram when specific components aren't detected"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    {title:<40}                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  👥 Users/Clients                                            ║
║     │                                                        ║
║     ▼                                                        ║
║  🌐 Internet Gateway / Load Balancer                         ║
║     │                                                        ║
║     ▼                                                        ║
║  🖥️  Application Layer                                       ║
║     │                                                        ║
║     ▼                                                        ║
║  🗄️  Data Layer                                              ║
║     │                                                        ║
║     ▼                                                        ║
║  📦 Storage Layer                                            ║
║                                                              ║
║  Data Flow: Users → Gateway → App → Data → Storage          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Architecture Components Detected:
{self.extract_components_list(plan_text)}

Recommended Next Steps:
• Review the architecture plan in the Plan tab
• Generate cost estimates
• Create CloudFormation template
• Deploy to AWS
"""
    
    def extract_components_list(self, plan_text: str) -> str:
        """Extract a simple list of components mentioned"""
        components = []
        plan_lower = plan_text.lower()
        
        service_names = {
            'ec2': 'Amazon EC2 (Compute)',
            'rds': 'Amazon RDS (Database)',
            's3': 'Amazon S3 (Storage)',
            'cloudfront': 'Amazon CloudFront (CDN)',
            'route53': 'Amazon Route 53 (DNS)',
            'lambda': 'AWS Lambda (Serverless)',
            'dynamodb': 'Amazon DynamoDB (NoSQL)',
            'elb': 'Elastic Load Balancer',
            'vpc': 'Amazon VPC (Networking)',
            'iam': 'AWS IAM (Security)'
        }
        
        for service, description in service_names.items():
            if service in plan_lower:
                components.append(f"• {description}")
        
        return "\n".join(components) if components else "• Generic cloud infrastructure components"

def create_architecture_diagram(plan_text: str, title: str = "AWS Architecture") -> str:
    """Main function to create ASCII architecture diagram"""
    generator = ASCIIDiagramGenerator()
    return generator.create_architecture_diagram(plan_text, title)