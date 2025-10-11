import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
from datetime import datetime

class StandaloneInfrastructGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AWS Infrastruct - Standalone GUI")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Store current data
        self.current_plan = ""
        self.current_template = ""
        self.current_diagram = ""
        self.current_estimate = ""
        self.is_processing = False
        self.envid = "dev"
        
        # Create the main interface
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_container, text="🤖 AWS Infrastruct - Standalone GUI", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_chat_tab()
        self.create_plan_tab()
        self.create_diagram_tab()
        self.create_template_tab()
        
    def create_chat_tab(self):
        """Create the main chat interface tab"""
        chat_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(chat_frame, text="💬 Chat Assistant")
        
        # Configure grid
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(1, weight=1)
        
        # Instructions
        instructions = ttk.Label(chat_frame, 
                                text="Describe your AWS infrastructure needs (e.g., 'a static website for my portfolio')",
                                font=('Arial', 10))
        instructions.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=20, width=80, 
                                                     font=('Consolas', 10), state='disabled')
        self.chat_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # User input
        self.user_input = ttk.Entry(input_frame, font=('Arial', 10))
        self.user_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.user_input.bind('<Return>', self.send_message)
        
        # Button frame for Send and New Chat buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1)
        
        # Send button
        self.send_btn = ttk.Button(button_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # New Chat button
        self.new_chat_btn = ttk.Button(button_frame, text="🆕 New Chat", command=self.start_new_chat)
        self.new_chat_btn.pack(side=tk.LEFT)
        
        # Environment ID input
        env_frame = ttk.Frame(chat_frame)
        env_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        env_frame.columnconfigure(1, weight=1)
        
        ttk.Label(env_frame, text="Environment ID:").grid(row=0, column=0, padx=(0, 5))
        self.envid_var = tk.StringVar(value=self.envid)
        envid_entry = ttk.Entry(env_frame, textvariable=self.envid_var, width=10)
        envid_entry.grid(row=0, column=1, sticky=tk.W)
        envid_entry.bind('<KeyRelease>', self.update_envid)
        
        # Status frame
        status_frame = ttk.Frame(chat_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready (Demo Mode - No Agent Connected)", 
                                     font=('Arial', 10), foreground='orange')
        self.status_label.pack(side=tk.LEFT)
        
        # Add welcome message
        welcome_msg = """Welcome to AWS Infrastruct Standalone GUI! 🚀

This is a demo version that works without the agent backend.

Features:
✅ Clean tabbed interface
✅ Chat-like interaction
✅ Plan, diagram, and template tabs
✅ Environment ID configuration
✅ File save/load functionality

Note: This is a UI demonstration. To connect to the actual AWS infrastructure agent, 
you'll need to resolve the import issues with the strands library.

Try typing a message to see the interface in action!"""
        
        self.add_chat_message("🤖 InfrastructBot (Demo)", welcome_msg)
    
    def create_plan_tab(self):
        """Create the architecture plan display tab"""
        plan_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(plan_frame, text="📋 Architecture Plan")
        
        plan_frame.columnconfigure(0, weight=1)
        plan_frame.rowconfigure(1, weight=1)
        
        # Header
        ttk.Label(plan_frame, text="Architecture Plan & Cost Estimate", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # Plan display
        self.plan_display = scrolledtext.ScrolledText(plan_frame, height=25, width=100, 
                                                     font=('Consolas', 10), state='disabled')
        self.plan_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        btn_frame = ttk.Frame(plan_frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(btn_frame, text="💾 Save Plan", 
                  command=self.save_plan).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_diagram_tab(self):
        """Create the architecture diagram display tab"""
        diagram_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(diagram_frame, text="🏗️ Architecture Diagram")
        
        diagram_frame.columnconfigure(0, weight=1)
        diagram_frame.rowconfigure(1, weight=1)
        
        # Header
        ttk.Label(diagram_frame, text="Architecture Diagram", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # Create notebook for different diagram views
        self.diagram_notebook = ttk.Notebook(diagram_frame)
        self.diagram_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ASCII/Text diagram tab
        text_frame = ttk.Frame(self.diagram_notebook, padding="5")
        self.diagram_notebook.add(text_frame, text="📝 Text Diagram")
        
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.diagram_display = scrolledtext.ScrolledText(text_frame, height=20, width=80, 
                                                        font=('Consolas', 10), state='disabled')
        self.diagram_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mermaid webview tab
        try:
            from tools.mermaid_webview import MermaidWebView
            self.mermaid_webview = MermaidWebView(self.diagram_notebook)
            mermaid_frame = self.mermaid_webview.create_webview_frame(self.diagram_notebook)
            self.diagram_notebook.add(mermaid_frame, text="🌐 Interactive Mermaid")
            self.mermaid_available = True
        except ImportError:
            self.mermaid_available = False
        
        # Buttons
        btn_frame = ttk.Frame(diagram_frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(btn_frame, text="💾 Save Diagram", 
                  command=self.save_diagram).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_template_tab(self):
        """Create the YAML template display tab"""
        template_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(template_frame, text="📄 YAML Template")
        
        template_frame.columnconfigure(0, weight=1)
        template_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(template_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(header_frame, text="Infrastructure as Code (YAML Template)", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        # Template info
        self.template_info = ttk.Label(header_frame, text="No template generated yet", 
                                      font=('Arial', 10), foreground='gray')
        self.template_info.grid(row=1, column=0, sticky=tk.W)
        
        # Template display
        self.template_display = scrolledtext.ScrolledText(template_frame, height=25, width=100, 
                                                         font=('Consolas', 10), state='disabled')
        self.template_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        btn_frame = ttk.Frame(template_frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(btn_frame, text="💾 Save Template", 
                  command=self.save_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📂 Load Template", 
                  command=self.load_template).pack(side=tk.LEFT, padx=(0, 5))
    
    def add_chat_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n{message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Send a message (demo mode)"""
        if self.is_processing:
            return
            
        message = self.user_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.user_input.delete(0, tk.END)
        
        # Add user message to chat
        self.add_chat_message("👤 You", message)
        
        # Simulate processing
        self.is_processing = True
        self.status_label.config(text="Processing (Demo Mode)...", foreground='orange')
        
        # Simulate response after a short delay
        self.root.after(1000, lambda: self.simulate_response(message))
    
    def simulate_response(self, message):
        """Simulate an agent response"""
        # Create demo responses based on keywords
        if any(word in message.lower() for word in ['website', 'static', 'portfolio']):
            plan = f"""Demo Architecture Plan for {self.envid} Environment:

1. Amazon S3 Bucket
   - Static website hosting
   - Public read access
   - Versioning enabled

2. Amazon CloudFront
   - Global CDN distribution
   - HTTPS enforcement
   - Custom domain support

3. Amazon Route 53
   - DNS management
   - Health checks
   - Failover routing

4. AWS Certificate Manager
   - SSL/TLS certificates
   - Automatic renewal

Tags:
- Name: {self.envid}-StaticWebsite-01
- Environment: {self.envid}
- CreatedBy: Infrastruct"""
            
            # Create enhanced diagrams
            try:
                from tools.ascii_diagramming_tool import create_architecture_diagram as create_ascii_diagram
                from tools.mermaid_diagramming_tool import create_mermaid_diagram
                
                plan_text = f"static website with s3 cloudfront route53 for {self.envid}"
                ascii_diagram = create_ascii_diagram(plan_text, f"{self.envid} Static Website")
                mermaid_diagram = create_mermaid_diagram(plan_text, f"{self.envid} Static Website")
                
                diagram = f"{ascii_diagram}\n\n{mermaid_diagram}"
                
            except ImportError:
                diagram = """Architecture Diagram:

┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Users    │───▶│  CloudFront  │───▶│  S3 Bucket  │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   Route 53   │
                   └──────────────┘

Data Flow:
1. User requests → Route 53 DNS
2. Route 53 → CloudFront CDN
3. CloudFront → S3 Static Files
4. Response cached at edge locations"""
            
            template = f"""# AWS CloudFormation Template
# Generated by Infrastruct for {self.envid} environment

AWSTemplateFormatVersion: '2010-09-09'
Description: Static website infrastructure

Parameters:
  EnvironmentId:
    Type: String
    Default: {self.envid}

Resources:
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${{EnvironmentId}}-website-${{AWS::AccountId}}'
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html
      Tags:
        - Key: Name
          Value: !Sub '${{EnvironmentId}}-Bucket-01'
        - Key: Environment
          Value: !Ref EnvironmentId
        - Key: CreatedBy
          Value: Infrastruct

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt WebsiteBucket.DomainName
            Id: S3Origin
            S3OriginConfig:
              OriginAccessIdentity: ''
        Enabled: true
        DefaultRootObject: index.html
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          Compress: true
      Tags:
        - Key: Name
          Value: !Sub '${{EnvironmentId}}-CDN-01'
        - Key: Environment
          Value: !Ref EnvironmentId
        - Key: CreatedBy
          Value: Infrastruct

Outputs:
  WebsiteURL:
    Description: Website URL
    Value: !GetAtt CloudFrontDistribution.DomainName"""
            
            estimate = """Monthly Cost Estimate:

┌─────────────────────────────────────────┐
│            SERVICE COSTS                │
├─────────────────────────────────────────┤
│ S3 Storage (1GB)           $0.23        │
│ S3 Requests (10K)          $0.04        │
│ CloudFront (100GB)         $8.50        │
│ Route 53 Hosted Zone       $0.50        │
│ Certificate Manager        $0.00        │
├─────────────────────────────────────────┤
│ TOTAL MONTHLY COST         $9.27        │
└─────────────────────────────────────────┘"""
            
        else:
            plan = f"""Demo Architecture Plan for {self.envid} Environment:

Based on your request: "{message}"

This is a demo response. In the full version, the AI agent would:
1. Analyze your requirements
2. Suggest appropriate AWS services
3. Create a detailed architecture plan
4. Provide cost estimates
5. Generate CloudFormation templates

Current Environment: {self.envid}"""
            
            diagram = "Demo diagram would be generated here..."
            template = "Demo YAML template would be generated here..."
            estimate = "Demo cost estimate would be calculated here..."
        
        # Update displays
        self.current_plan = plan
        self.current_diagram = diagram
        self.current_template = template
        self.current_estimate = estimate
        
        # Add response to chat
        self.add_chat_message("🤖 InfrastructBot (Demo)", "Demo architecture plan generated! Check the other tabs to see the results.")
        
        # Update displays
        self.update_plan_display()
        self.update_diagram_display()
        self.update_template_display()
        
        # Switch to plan tab
        self.notebook.select(1)
        
        # Reset status
        self.status_label.config(text="Ready (Demo Mode)", foreground='green')
        self.is_processing = False
    
    def update_envid(self, event=None):
        """Update environment ID"""
        self.envid = self.envid_var.get().strip() or "dev"
    
    def start_new_chat(self):
        """Start a new chat session"""
        # Check if user wants to clear current session if there's content
        if self.current_plan or self.current_template or self.current_diagram:
            result = messagebox.askyesno(
                "New Chat Session", 
                "This will clear your current session including:\n"
                "• Architecture plan\n"
                "• Diagrams\n" 
                "• Templates\n"
                "• Chat history\n\n"
                "Are you sure you want to start a new session?"
            )
            if not result:
                return
        
        # Clear current session
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        
        # Reset data
        self.current_plan = ""
        self.current_template = ""
        self.current_diagram = ""
        self.current_estimate = ""
        self.is_processing = False
        
        # Clear all tab displays
        self.plan_display.config(state='normal')
        self.plan_display.delete(1.0, tk.END)
        self.plan_display.config(state='disabled')
        
        self.diagram_display.config(state='normal')
        self.diagram_display.delete(1.0, tk.END)
        self.diagram_display.config(state='disabled')
        
        self.template_display.config(state='normal')
        self.template_display.delete(1.0, tk.END)
        self.template_display.config(state='disabled')
        
        # Reset template info
        if hasattr(self, 'template_info'):
            self.template_info.config(text="No template generated yet")
        
        # Reset status
        self.status_label.config(text="Ready (Demo Mode - No Agent Connected)", foreground='orange')
        
        # Focus on input field
        self.user_input.focus()
        
        # Switch back to chat tab
        self.notebook.select(0)
        
        # Add welcome message for new session
        welcome_msg = """🆕 New Demo Session Started! 🚀

This is a demo version that works without the agent backend.

Features:
✅ Clean tabbed interface
✅ Chat-like interaction
✅ Plan, diagram, and template tabs
✅ Environment ID configuration
✅ File save/load functionality

Try typing a message to see the interface in action!
Example: "I need a static website for my portfolio" """
        
        self.add_chat_message("🤖 InfrastructBot (Demo)", welcome_msg)
    
    def update_plan_display(self):
        """Update the plan display"""
        self.plan_display.config(state='normal')
        self.plan_display.delete(1.0, tk.END)
        combined_text = f"{self.current_plan}\n\n{'='*60}\n💰 COST ESTIMATE\n{'='*60}\n{self.current_estimate}"
        self.plan_display.insert(1.0, combined_text)
        self.plan_display.config(state='disabled')
    
    def update_diagram_display(self):
        """Update the diagram display with multiple formats"""
        # Update text diagram display
        self.diagram_display.config(state='normal')
        self.diagram_display.delete(1.0, tk.END)
        self.diagram_display.insert(1.0, self.current_diagram)
        self.diagram_display.config(state='disabled')
        
        # Update Mermaid webview if available
        if hasattr(self, 'mermaid_available') and self.mermaid_available and hasattr(self, 'mermaid_webview'):
            try:
                # Extract Mermaid code from current diagram
                if "```mermaid" in self.current_diagram:
                    # Find the mermaid section
                    mermaid_start = self.current_diagram.find("Mermaid Diagram Code:")
                    if mermaid_start != -1:
                        mermaid_section = self.current_diagram[mermaid_start:]
                        # Extract just the mermaid code part
                        code_start = mermaid_section.find("```mermaid")
                        code_end = mermaid_section.find("```", code_start + 10)
                        if code_start != -1 and code_end != -1:
                            mermaid_code = mermaid_section[code_start:code_end + 3]
                            self.mermaid_webview.update_diagram(mermaid_code, f"{self.envid} Demo Architecture")
            except Exception as e:
                print(f"Error updating Mermaid webview: {e}")
    
    def update_template_display(self):
        """Update the template display"""
        self.template_display.config(state='normal')
        self.template_display.delete(1.0, tk.END)
        self.template_display.insert(1.0, self.current_template)
        self.template_display.config(state='disabled')
        
        # Update template info
        self.template_info.config(text=f"Template generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def save_plan(self):
        """Save the current plan to file"""
        if not self.current_plan:
            messagebox.showwarning("No Plan", "No plan to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.current_plan)
                messagebox.showinfo("Saved", f"Plan saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plan: {str(e)}")
    
    def save_template(self):
        """Save the current template to file"""
        if not self.current_template:
            messagebox.showwarning("No Template", "No template to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("YML files", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.current_template)
                messagebox.showinfo("Saved", f"Template saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save template: {str(e)}")
    
    def save_diagram(self):
        """Save the current diagram to file"""
        if not self.current_diagram:
            messagebox.showwarning("No Diagram", "No diagram to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.current_diagram)
                messagebox.showinfo("Saved", f"Diagram saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save diagram: {str(e)}")
    
    def load_template(self):
        """Load a template from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("YML files", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.current_template = f.read()
                self.update_template_display()
                messagebox.showinfo("Loaded", f"Template loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load template: {str(e)}")

def main():
    root = tk.Tk()
    app = StandaloneInfrastructGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()