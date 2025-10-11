import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
from datetime import datetime
import json
from strands import Agent
from strands.models import BedrockModel
try:
    from kiro_nova_act_deployer import deploy_to_aws_direct, deploy_infrastructure, check_deployment_status, open_aws_cloudformation_console
    ENHANCED_DEPLOYMENT_AVAILABLE = True
except ImportError:
    from tools.deployer_agent_tool import deploy_infrastructure
    ENHANCED_DEPLOYMENT_AVAILABLE = False
    print("Warning: Enhanced deployment not available. Using basic deployment.")
from tools.templating_agent_tool import gen_template
from tools.planner_agent_tool import plan_architecture
from tools.estimator_agent_tool import estimate_price
from tools.diagramming_agent_tool import create_architecture_diagram
from dotenv import load_dotenv

# Optional imports with fallbacks
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Image display will be limited.")

try:
    from tools.enhanced_diagramming_tool import EnhancedDiagramGenerator
    ENHANCED_DIAGRAMS_AVAILABLE = True
except ImportError:
    ENHANCED_DIAGRAMS_AVAILABLE = False
    print("Warning: Enhanced diagramming not available. Using text diagrams only.")

try:
    from tools.enhanced_templating_tool import EnhancedTemplatingTool
    ENHANCED_TEMPLATING_AVAILABLE = True
except ImportError:
    ENHANCED_TEMPLATING_AVAILABLE = False
    print("Warning: Enhanced templating not available. Using basic templating.")

try:
    from database.chat_history import ChatHistoryManager
    CHAT_HISTORY_AVAILABLE = True
except ImportError:
    CHAT_HISTORY_AVAILABLE = False
    print("Warning: Chat history not available. Sessions will not be saved.")

# Try to import webview for Mermaid rendering
try:
    import tkinter.html as tkhtml
    WEBVIEW_AVAILABLE = True
except ImportError:
    try:
        import webbrowser
        import tempfile
        WEBVIEW_AVAILABLE = "browser"
    except ImportError:
        WEBVIEW_AVAILABLE = False
        print("Warning: Webview not available. Mermaid diagrams will show as code only.")

# Load environment variables
load_dotenv()

class InfrastructGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AWS Infrastruct - Cloud Architecture Assistant")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize the agent
        self.setup_agent()
        
        # Store current plan and template data
        self.current_plan = ""
        self.current_template = ""
        self.current_diagram = ""
        self.current_estimate = ""
        self.current_diagram_image = None
        
        # Workflow state tracking
        self.workflow_state = "initial"  # initial -> planning -> diagramming -> estimating -> templating -> deploying
        self.is_processing = False
        
        # Initialize enhanced tools (with fallbacks)
        if ENHANCED_DIAGRAMS_AVAILABLE:
            self.enhanced_diagram_generator = EnhancedDiagramGenerator()
        else:
            self.enhanced_diagram_generator = None
            
        if ENHANCED_TEMPLATING_AVAILABLE:
            self.enhanced_templating_tool = EnhancedTemplatingTool()
        else:
            self.enhanced_templating_tool = None
        
        # Initialize chat history manager (with fallback)
        if CHAT_HISTORY_AVAILABLE:
            self.chat_history = ChatHistoryManager()
            self.current_session_id = None
        else:
            self.chat_history = None
            self.current_session_id = None
        
        # Environment ID for tagging
        self.envid = "dev"  # Default, can be changed by user
        
        # Create the main interface
        self.create_widgets()
        
    def setup_agent(self):
        """Initialize the AWS Infrastructure Agent"""
        try:
            # Show rich UI for tools in CLI
            os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"
            
            # Create a BedrockModel
            self.bedrock_model = BedrockModel(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                region_name="us-east-1"
            )
            
            SYSTEM_PROMPT = """
            You are a professional AWS CLOUD SOLUTIONS ARCHITECT that assists 
            AWS customers with end to end cloud infrastructure delivery from planning to deployment.
            
            Provide clear, concise responses suitable for a GUI interface.
            """
            
            self.aws_infrastruct_agent = Agent(
                model=self.bedrock_model,
                system_prompt=SYSTEM_PROMPT,
                tools=[
                    plan_architecture,
                    estimate_price,
                    gen_template,
                    deploy_infrastructure
                ]
            )
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize agent: {str(e)}")
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_container, text="🤖 AWS Infrastruct - Cloud Architecture Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Create left panel for chat history (if available)
        if CHAT_HISTORY_AVAILABLE:
            self.create_history_panel(main_container)
        
        # Create main content area
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_chat_tab()
        self.create_plan_tab()
        self.create_diagram_tab()
        self.create_template_tab()
        self.create_deployment_tab()
        
        # Load recent sessions (if available)
        if CHAT_HISTORY_AVAILABLE:
            self.load_recent_sessions()
        
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
        
        # Quick action buttons
        action_frame = ttk.Frame(chat_frame)
        action_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="📋 Plan Architecture", 
                  command=self.quick_plan).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="💰 Estimate Cost", 
                  command=self.quick_estimate).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📄 Generate Template", 
                  command=self.quick_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🚀 Deploy", 
                  command=self.quick_deploy).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status frame
        status_frame = ttk.Frame(chat_frame)
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", 
                                     font=('Arial', 10), foreground='green')
        self.status_label.pack(side=tk.LEFT)
        
        # Add welcome message
        welcome_msg = """Welcome to AWS Infrastruct! 🚀

I'll guide you through a complete infrastructure workflow:
1. 📋 Architecture Planning - Detailed technical specifications
2. 🏗️ Visual Diagramming - Component relationships and data flow
3. 💰 Cost Estimation - Monthly pricing breakdown with tables
4. 📄 Template Generation - Infrastructure as Code (YAML) with proper tagging
5. 🚀 AWS Deployment - One-click deployment to your account

Simply describe what you want to build (e.g., "a static website for my portfolio" or "a scalable web application with database") and I'll handle the complete workflow automatically!

Your chat history is automatically saved and can be accessed from the left panel."""
        
        self.add_chat_message("🤖 InfrastructBot", welcome_msg)
    
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
        
        ttk.Button(btn_frame, text="💰 Get Cost Estimate", 
                  command=self.get_cost_estimate).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📄 Generate Template", 
                  command=self.generate_template).pack(side=tk.LEFT, padx=(0, 5))
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
            print("Warning: Mermaid webview not available")
        
        # Buttons
        btn_frame = ttk.Frame(diagram_frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🎨 Generate Diagram", 
                  command=self.generate_diagram).pack(side=tk.LEFT, padx=(0, 5))
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
        
        # Template display with syntax highlighting simulation
        self.template_display = scrolledtext.ScrolledText(template_frame, height=25, width=100, 
                                                         font=('Consolas', 10), state='disabled')
        self.template_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        btn_frame = ttk.Frame(template_frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(btn_frame, text="📄 Generate Template", 
                  command=self.generate_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="💾 Save Template", 
                  command=self.save_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📂 Load Template", 
                  command=self.load_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="✅ Validate", 
                  command=self.validate_template).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_deployment_tab(self):
        """Create the deployment tab"""
        deploy_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(deploy_frame, text="🚀 Deployment")
        
        deploy_frame.columnconfigure(0, weight=1)
        deploy_frame.rowconfigure(1, weight=1)
        
        # Header
        ttk.Label(deploy_frame, text="Infrastructure Deployment", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # Deployment status display
        self.deploy_display = scrolledtext.ScrolledText(deploy_frame, height=20, width=100, 
                                                       font=('Consolas', 10), state='disabled')
        self.deploy_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Deployment controls
        controls_frame = ttk.Frame(deploy_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        controls_frame.columnconfigure(1, weight=1)
        
        # Stack name
        ttk.Label(controls_frame, text="Stack Name:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.stack_name_var = tk.StringVar()
        stack_entry = ttk.Entry(controls_frame, textvariable=self.stack_name_var, width=30)
        stack_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # Deploy button
        self.deploy_btn = ttk.Button(controls_frame, text="🚀 Deploy to AWS", 
                                    command=self.deploy_infrastructure)
        self.deploy_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Additional deployment controls
        deploy_controls_frame = ttk.Frame(deploy_frame)
        deploy_controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        if ENHANCED_DEPLOYMENT_AVAILABLE:
            ttk.Button(deploy_controls_frame, text="📊 Check Status", 
                      command=self.check_deployment_status).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(deploy_controls_frame, text="🌐 Open AWS Console", 
                      command=self.open_aws_console).pack(side=tk.LEFT, padx=(0, 5))
            
            # Deployment mode selection
            mode_frame = ttk.Frame(deploy_controls_frame)
            mode_frame.pack(side=tk.RIGHT)
            
            ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(10, 5))
            self.deployment_mode = tk.StringVar(value="auto")
            ttk.Radiobutton(mode_frame, text="🤖 Auto", variable=self.deployment_mode, 
                           value="auto").pack(side=tk.LEFT)
            ttk.Radiobutton(mode_frame, text="📋 Manual", variable=self.deployment_mode, 
                           value="manual").pack(side=tk.LEFT, padx=(5, 0))
        
        # Status frame
        status_frame = ttk.Frame(deploy_frame)
        status_frame.grid(row=3, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Ready for deployment", 
                                     font=('Arial', 10), foreground='green')
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
    
    def add_chat_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n{message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Send a message to the agent"""
        if self.is_processing:
            return
            
        message = self.user_input.get().strip()
        if not message:
            return
        
        # Disable input during processing
        self.user_input.config(state='disabled')
        self.send_btn.config(state='disabled')
        self.is_processing = True
        
        # Clear input
        self.user_input.delete(0, tk.END)
        
        # Add user message to chat
        self.add_chat_message("👤 You", message)
        
        # Add processing message
        self.add_chat_message("🔄 Processing", "Analyzing your request and planning architecture...")
        
        # Process message in background thread
        threading.Thread(target=self.process_message_workflow, args=(message,), daemon=True).start()
    
    def process_message_workflow(self, message):
        """Process message following the proper workflow sequence"""
        try:
            # Create new session if needed
            if not self.current_session_id:
                title = message[:50] + "..." if len(message) > 50 else message
                self.current_session_id = self.chat_history.create_session(title, "GUI")
                self.root.after(0, self.load_recent_sessions)
            
            # Step 1: Plan Architecture
            self.root.after(0, lambda: self.status_label.config(text="Step 1: Planning Architecture...", foreground='orange'))
            self.root.after(0, lambda: self.update_processing_message("🏗️ Planning", "Creating detailed architecture plan..."))
            
            plan_response = plan_architecture(message)
            self.current_plan = str(plan_response)
            self.workflow_state = "planning"
            
            self.root.after(0, lambda: self.add_chat_message("📋 Architecture Plan", self.current_plan))
            self.root.after(0, lambda: self.update_plan_display())
            self.root.after(0, lambda: self.notebook.select(1))  # Switch to plan tab
            
            # Step 2: Generate Architecture Diagram
            self.root.after(0, lambda: self.status_label.config(text="Step 2: Generating Diagram...", foreground='orange'))
            
            self.root.after(0, lambda: self.update_processing_message("🎨 Diagramming", "Creating enhanced architecture diagrams..."))
            
            # Use multiple diagramming approaches for better results
            try:
                from tools.ascii_diagramming_tool import create_architecture_diagram as create_ascii_diagram
                from tools.mermaid_diagramming_tool import create_mermaid_diagram
                from tools.plantuml_diagramming_tool import create_plantuml_diagram
                
                # Create ASCII diagram (always works)
                ascii_diagram = create_ascii_diagram(self.current_plan, f"{self.envid} Architecture")
                
                # Create web-based diagram codes
                mermaid_diagram = create_mermaid_diagram(self.current_plan, f"{self.envid} Architecture")
                plantuml_diagram = create_plantuml_diagram(self.current_plan, f"{self.envid} Architecture")
                
                # Combine all diagram types
                self.current_diagram = f"""
{ascii_diagram}

{mermaid_diagram}

{plantuml_diagram}

Multiple Diagram Formats Available:
• ASCII/Unicode: Displays directly in the interface
• Mermaid: Copy code to https://mermaid.live/ for web rendering
• PlantUML: Copy code to http://www.plantuml.com/plantuml/ for web rendering
"""
                
            except ImportError:
                # Fallback to basic diagram generator
                diagram_response = create_architecture_diagram(self.current_plan)
                self.current_diagram = str(diagram_response)
            
            self.workflow_state = "diagramming"
            
            self.root.after(0, lambda: self.add_chat_message("🏗️ Architecture Diagram", "Enhanced diagrams generated! Check the Architecture Diagram tab for multiple formats including interactive Mermaid diagrams."))
            self.root.after(0, lambda: self.update_diagram_display())
            self.root.after(0, lambda: self.notebook.select(2))  # Switch to diagram tab
            
            # Step 3: Cost Estimation
            self.root.after(0, lambda: self.status_label.config(text="Step 3: Estimating Costs...", foreground='orange'))
            self.root.after(0, lambda: self.update_processing_message("💰 Estimating", "Calculating infrastructure costs..."))
            
            estimate_response = estimate_price(self.current_plan)
            self.current_estimate = str(estimate_response)
            self.workflow_state = "estimating"
            
            # Format cost estimate as a table
            cost_table = self.format_cost_estimate(self.current_estimate)
            self.root.after(0, lambda: self.add_chat_message("💰 Cost Estimate", cost_table))
            self.root.after(0, lambda: self.update_plan_with_estimate())
            
            # Step 4: Generate Template
            self.root.after(0, lambda: self.status_label.config(text="Step 4: Generating Template...", foreground='orange'))
            
            if ENHANCED_TEMPLATING_AVAILABLE and self.enhanced_templating_tool:
                self.root.after(0, lambda: self.update_processing_message("📄 Templating", "Generating YAML Infrastructure as Code template with proper tagging..."))
                
                # Use enhanced templating tool
                enhanced_template = self.enhanced_templating_tool.create_enhanced_template(self.current_plan, self.envid)
                self.current_template = enhanced_template
                self.workflow_state = "templating"
                
                template_msg = f"""Enhanced Infrastructure template generated successfully! 

✨ Features included:
• Proper resource tagging with {self.envid} environment ID
• Name tags: {self.envid}-ResourceType-InstanceNumber
• Environment tags: {self.envid}
• CreatedBy tags: Infrastruct
• CloudFormation best practices

Check the YAML Template tab for the complete template."""
            else:
                self.root.after(0, lambda: self.update_processing_message("📄 Templating", "Generating YAML Infrastructure as Code template..."))
                
                # Use basic templating tool
                template_response = gen_template(self.current_plan)
                self.current_template = str(template_response)
                self.workflow_state = "templating"
                
                template_msg = "Infrastructure template generated successfully! Check the YAML Template tab for the complete template."
            
            self.root.after(0, lambda: self.add_chat_message("📄 Enhanced YAML Template", template_msg))
            self.root.after(0, lambda: self.update_template_display())
            self.root.after(0, lambda: self.notebook.select(3))  # Switch to template tab
            
            # Save session data (if available)
            if CHAT_HISTORY_AVAILABLE and self.chat_history and self.current_session_id:
                self.chat_history.update_session_data(
                    self.current_session_id,
                    workflow_state=self.workflow_state,
                    plan_data=self.current_plan,
                    diagram_data=self.current_diagram,
                    estimate_data=self.current_estimate,
                    template_data=self.current_template
                )
            
            # Final completion message
            completion_msg = f"""
✅ Enhanced Workflow Complete! Your {self.envid} infrastructure is ready:

📋 Architecture Plan: Detailed technical specifications
🏗️ Visual Diagram: Enhanced diagrams with proper AWS icons  
💰 Cost Estimate: Monthly pricing breakdown with tables
📄 YAML Template: Enhanced CloudFormation with proper tagging
   • Environment: {self.envid}
   • Naming: {self.envid}-ResourceType-##
   • CreatedBy: Infrastruct

Next Steps:
🚀 Review the template and deploy to AWS
💾 Save your artifacts for future reference
🔄 Make modifications if needed
📚 Session automatically saved to history
            """
            
            self.root.after(0, lambda: self.add_chat_message("🎉 Enhanced Complete", completion_msg.strip()))
            self.root.after(0, lambda: self.status_label.config(text="Enhanced Workflow Complete - Ready for Deployment", foreground='green'))
            
        except Exception as e:
            error_msg = f"Error in enhanced workflow: {str(e)}"
            self.root.after(0, lambda: self.add_chat_message("❌ Error", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="Error", foreground='red'))
        finally:
            # Re-enable input
            self.root.after(0, self.enable_input)
    
    def update_processing_message(self, title, message):
        """Update the last processing message in chat"""
        self.chat_display.config(state='normal')
        # Find and replace the last processing message
        content = self.chat_display.get(1.0, tk.END)
        lines = content.split('\n')
        
        # Find the last processing message and update it
        for i in range(len(lines)-1, -1, -1):
            if '🔄 Processing' in lines[i] or '🏗️ Planning' in lines[i] or '🎨 Diagramming' in lines[i] or '💰 Estimating' in lines[i] or '📄 Templating' in lines[i]:
                timestamp = datetime.now().strftime("%H:%M:%S")
                lines[i] = f"[{timestamp}] {title}:"
                if i+1 < len(lines):
                    lines[i+1] = message
                break
        
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.insert(1.0, '\n'.join(lines))
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def enable_input(self):
        """Re-enable input controls after processing"""
        self.user_input.config(state='normal')
        self.send_btn.config(state='normal')
        self.is_processing = False
        self.user_input.focus()
    
    def format_cost_estimate(self, estimate):
        """Format cost estimate as a readable table"""
        try:
            # This is a simple formatter - you might want to enhance based on your estimate format
            lines = estimate.split('\n')
            formatted = "┌─────────────────────────────────────────────────────────────┐\n"
            formatted += "│                     MONTHLY COST ESTIMATE                  │\n"
            formatted += "├─────────────────────────────────────────────────────────────┤\n"
            
            for line in lines:
                if line.strip():
                    # Pad line to fit table width
                    padded_line = f"│ {line[:55]:<55} │"
                    formatted += padded_line + "\n"
            
            formatted += "└─────────────────────────────────────────────────────────────┘"
            return formatted
        except:
            return estimate
    
    def update_plan_with_estimate(self):
        """Update plan display with cost estimate"""
        combined_text = f"{self.current_plan}\n\n{'='*60}\n"
        combined_text += f"💰 COST ESTIMATE\n{'='*60}\n{self.current_estimate}"
        
        self.plan_display.config(state='normal')
        self.plan_display.delete(1.0, tk.END)
        self.plan_display.insert(1.0, combined_text)
        self.plan_display.config(state='disabled')
    
    def update_diagram_display(self):
        """Update the diagram display with multiple formats"""
        # Update text diagram display
        self.diagram_display.config(state='normal')
        self.diagram_display.delete(1.0, tk.END)
        
        # If we have a diagram image, try to display it
        if PIL_AVAILABLE and self.current_diagram_image and os.path.exists(self.current_diagram_image):
            try:
                # Load and resize image
                image = Image.open(self.current_diagram_image)
                # Resize to fit display
                display_width = 800
                display_height = 600
                image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Insert image into text widget
                self.diagram_display.image_create(tk.END, image=photo)
                self.diagram_display.image = photo  # Keep a reference
                self.diagram_display.insert(tk.END, "\n\n")
                
            except Exception as e:
                print(f"Error displaying image: {e}")
                self.diagram_display.insert(tk.END, f"[Image available at: {self.current_diagram_image}]\n\n")
        elif self.current_diagram_image and os.path.exists(self.current_diagram_image):
            # PIL not available, just show path
            self.diagram_display.insert(tk.END, f"[Visual diagram saved to: {self.current_diagram_image}]\n\n")
        
        # Always show text description
        self.diagram_display.insert(tk.END, self.current_diagram)
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
                            self.mermaid_webview.update_diagram(mermaid_code, f"{self.envid} Architecture")
            except Exception as e:
                print(f"Error updating Mermaid webview: {e}")
    
    def process_message(self, message):
        """Legacy method - now redirects to workflow"""
        self.process_message_workflow(message)
    
    def quick_plan(self):
        """Quick action to plan architecture"""
        if self.workflow_state == "initial":
            self.user_input.delete(0, tk.END)
            self.user_input.insert(0, "Please create an architecture plan for ")
            self.user_input.focus()
        else:
            self.notebook.select(1)  # Switch to plan tab
    
    def quick_estimate(self):
        """Quick action to view cost estimate"""
        if self.current_estimate:
            self.notebook.select(1)  # Switch to plan tab (which shows estimate)
            messagebox.showinfo("Cost Estimate", "Cost estimate is displayed in the Architecture Plan tab")
        else:
            messagebox.showwarning("No Estimate", "Please complete the workflow first to get cost estimates")
    
    def quick_template(self):
        """Quick action to view template"""
        if self.current_template:
            self.notebook.select(3)  # Switch to template tab
        else:
            messagebox.showwarning("No Template", "Please complete the workflow first to generate templates")
    
    def quick_deploy(self):
        """Quick action to deploy"""
        if self.current_template:
            self.notebook.select(4)  # Switch to deployment tab
        else:
            messagebox.showwarning("No Template", "Please complete the workflow first to generate templates")
    
    def update_plan_display(self):
        """Update the plan display"""
        self.plan_display.config(state='normal')
        self.plan_display.delete(1.0, tk.END)
        self.plan_display.insert(1.0, self.current_plan)
        self.plan_display.config(state='disabled')
    
    def update_template_display(self):
        """Update the template display"""
        self.template_display.config(state='normal')
        self.template_display.delete(1.0, tk.END)
        self.template_display.insert(1.0, self.current_template)
        self.template_display.config(state='disabled')
        
        # Update template info
        self.template_info.config(text=f"Template generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_cost_estimate(self):
        """Get cost estimate for current plan - now part of automated workflow"""
        if not self.current_plan:
            messagebox.showwarning("No Plan", "Please start with describing your infrastructure needs in the chat")
            return
        
        if self.current_estimate:
            # Show existing estimate
            self.notebook.select(1)  # Switch to plan tab
            messagebox.showinfo("Cost Estimate Available", "Cost estimate is already available in the Architecture Plan tab")
        else:
            messagebox.showinfo("Workflow Required", "Cost estimation is part of the automated workflow. Please describe your infrastructure needs in the chat to start the complete process.")
    
    def generate_template(self):
        """Generate YAML template - now part of automated workflow"""
        if not self.current_plan:
            messagebox.showwarning("No Plan", "Please start with describing your infrastructure needs in the chat")
            return
        
        if self.current_template:
            # Show existing template
            self.notebook.select(3)  # Switch to template tab
            messagebox.showinfo("Template Available", "YAML template is already available in the YAML Template tab")
        else:
            messagebox.showinfo("Workflow Required", "Template generation is part of the automated workflow. Please describe your infrastructure needs in the chat to start the complete process.")
    
    def generate_diagram(self):
        """Generate architecture diagram - now part of automated workflow"""
        if not self.current_plan:
            messagebox.showwarning("No Plan", "Please start with describing your infrastructure needs in the chat")
            return
        
        if self.current_diagram:
            # Show existing diagram
            self.notebook.select(2)  # Switch to diagram tab
            messagebox.showinfo("Diagram Available", "Architecture diagram is already available in the Architecture Diagram tab")
        else:
            messagebox.showinfo("Workflow Required", "Diagram generation is part of the automated workflow. Please describe your infrastructure needs in the chat to start the complete process.")
    
    def deploy_infrastructure(self):
        """Deploy infrastructure to AWS using direct Nova-Act deployment"""
        if not self.current_template:
            messagebox.showwarning("No Template", "Please generate a template first")
            return
        
        stack_name = self.stack_name_var.get().strip()
        if not stack_name:
            messagebox.showwarning("Missing Stack Name", "Please enter a stack name")
            return
        
        try:
            self.status_label.config(text="Launching deployment...", foreground='orange')
            self.progress_var.set(20)
            
            # Disable deploy button during deployment
            self.deploy_btn.config(state='disabled')
            
            self.deploy_display.config(state='normal')
            self.deploy_display.insert(tk.END, f"🚀 DIRECT DEPLOYMENT INITIATED\n")
            self.deploy_display.insert(tk.END, f"📋 Stack Name: {stack_name}\n")
            self.deploy_display.insert(tk.END, f"🤖 Opening Chrome browser...\n")
            self.deploy_display.insert(tk.END, f"🔐 Checking AWS login status...\n")
            self.deploy_display.insert(tk.END, f"⚡ Starting Nova-Act automation...\n\n")
            self.deploy_display.insert(tk.END, f"💡 If AWS login screen appears:\n")
            self.deploy_display.insert(tk.END, f"   • Please log in to AWS Console\n")
            self.deploy_display.insert(tk.END, f"   • Automation will wait up to 5 minutes\n")
            self.deploy_display.insert(tk.END, f"   • Deployment resumes automatically after login\n\n")
            
            self.progress_var.set(40)
            self.deploy_display.see(tk.END)
            
            # Run direct deployment in background thread
            threading.Thread(target=self.run_direct_deployment, args=(stack_name,), daemon=True).start()
            
        except Exception as e:
            self.deploy_display.config(state='normal')
            self.deploy_display.insert(tk.END, f"❌ Deployment launch failed: {str(e)}\n")
            self.deploy_display.config(state='disabled')
            messagebox.showerror("Deployment Error", f"Failed to launch deployment: {str(e)}")
            self.status_label.config(text="Deployment failed", foreground='red')
            self.progress_var.set(0)
            self.deploy_btn.config(state='normal')
    
    def run_direct_deployment(self, stack_name: str):
        """Run the direct deployment in background thread"""
        try:
            self.root.after(0, lambda: self.progress_var.set(60))
            self.root.after(0, lambda: self.status_label.config(text="Chrome opening, checking AWS login...", foreground='orange'))
            
            # Call the direct deployment function with current template
            result = deploy_to_aws_direct(self.current_template, stack_name)
            
            # Update UI with result
            self.root.after(0, lambda: self.update_deployment_result(result, True))
            
        except Exception as e:
            error_msg = f"❌ Direct deployment failed: {str(e)}"
            self.root.after(0, lambda: self.update_deployment_result(error_msg, False))
    
    def update_deployment_result(self, result: str, success: bool):
        """Update the deployment display with results"""
        self.deploy_display.config(state='normal')
        self.deploy_display.insert(tk.END, f"\n{result}\n")
        self.deploy_display.config(state='disabled')
        self.deploy_display.see(tk.END)
        
        if success:
            self.progress_var.set(100)
            self.status_label.config(text="Deployment completed", foreground='green')
        else:
            self.progress_var.set(0)
            self.status_label.config(text="Deployment failed", foreground='red')
        
        # Re-enable deploy button
        self.deploy_btn.config(state='normal')
    
    def check_deployment_status(self):
        """Check the status of the current deployment"""
        stack_name = self.stack_name_var.get().strip()
        if not stack_name:
            messagebox.showwarning("Missing Stack Name", "Please enter a stack name to check")
            return
        
        if ENHANCED_DEPLOYMENT_AVAILABLE:
            try:
                result = check_deployment_status(stack_name)
                self.deploy_display.config(state='normal')
                self.deploy_display.insert(tk.END, f"\n{result}\n")
                self.deploy_display.config(state='disabled')
                self.deploy_display.see(tk.END)
            except Exception as e:
                messagebox.showerror("Status Check Error", f"Failed to check status: {str(e)}")
        else:
            messagebox.showinfo("Status Check", f"Please check the AWS Console for stack: {stack_name}")
    
    def open_aws_console(self):
        """Open AWS CloudFormation console"""
        if ENHANCED_DEPLOYMENT_AVAILABLE:
            try:
                result = open_aws_cloudformation_console()
                self.status_label.config(text="AWS Console opened", foreground='blue')
                self.deploy_display.config(state='normal')
                self.deploy_display.insert(tk.END, f"\n{result}\n")
                self.deploy_display.config(state='disabled')
                self.deploy_display.see(tk.END)
            except Exception as e:
                messagebox.showerror("Console Error", f"Failed to open console: {str(e)}")
        else:
            import webbrowser
            webbrowser.open("https://console.aws.amazon.com/cloudformation/home")
            self.status_label.config(text="AWS Console opened", foreground='blue')
    
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
    
    def validate_template(self):
        """Validate the current template"""
        if not self.current_template:
            messagebox.showwarning("No Template", "No template to validate")
            return
        
        # Simple YAML validation - you might want to add CloudFormation-specific validation
        try:
            import yaml
            yaml.safe_load(self.current_template)
            messagebox.showinfo("Validation", "Template is valid YAML")
        except yaml.YAMLError as e:
            messagebox.showerror("Validation Error", f"Invalid YAML: {str(e)}")
        except ImportError:
            messagebox.showwarning("Validation", "PyYAML not installed. Cannot validate YAML syntax.")
    
    def create_history_panel(self, parent):
        """Create the left panel for chat history"""
        if not CHAT_HISTORY_AVAILABLE:
            return
            
        history_frame = ttk.Frame(parent, width=250)
        history_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        history_frame.grid_propagate(False)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)
        
        # History header
        ttk.Label(history_frame, text="📚 Chat History", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(history_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.search_sessions)
        
        # Add simple placeholder functionality
        search_entry.insert(0, "Search sessions...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search sessions..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search sessions...") if not search_entry.get() else None)
        
        ttk.Button(search_frame, text="🔍", width=3,
                  command=self.search_sessions).grid(row=0, column=1)
        
        # Sessions list
        self.sessions_frame = ttk.Frame(history_frame)
        self.sessions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.sessions_frame.columnconfigure(0, weight=1)
        
        # Scrollable sessions list
        sessions_canvas = tk.Canvas(self.sessions_frame, height=400)
        sessions_scrollbar = ttk.Scrollbar(self.sessions_frame, orient="vertical", command=sessions_canvas.yview)
        self.scrollable_sessions = ttk.Frame(sessions_canvas)
        
        self.scrollable_sessions.bind(
            "<Configure>",
            lambda e: sessions_canvas.configure(scrollregion=sessions_canvas.bbox("all"))
        )
        
        sessions_canvas.create_window((0, 0), window=self.scrollable_sessions, anchor="nw")
        sessions_canvas.configure(yscrollcommand=sessions_scrollbar.set)
        
        sessions_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sessions_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Action buttons frame
        actions_frame = ttk.Frame(history_frame)
        actions_frame.grid(row=3, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        # New session button
        ttk.Button(actions_frame, text="➕ New Session", 
                  command=self.start_new_session).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Clear all button
        ttk.Button(actions_frame, text="🗑️ Clear All", 
                  command=self.clear_all_sessions).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
    
    def load_recent_sessions(self):
        """Load recent chat sessions into the history panel"""
        if not CHAT_HISTORY_AVAILABLE or not self.chat_history:
            return
            
        try:
            sessions = self.chat_history.get_recent_sessions(20)
            
            # Clear existing session widgets
            for widget in self.scrollable_sessions.winfo_children():
                widget.destroy()
            
            for i, session in enumerate(sessions):
                session_frame = ttk.Frame(self.scrollable_sessions, relief="solid", borderwidth=1)
                session_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2, padx=2)
                session_frame.columnconfigure(0, weight=1)
                
                # Create content frame for session info
                content_frame = ttk.Frame(session_frame)
                content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
                content_frame.columnconfigure(0, weight=1)
                
                # Session title
                title_label = ttk.Label(content_frame, text=session['title'][:30] + "..." if len(session['title']) > 30 else session['title'],
                                       font=('Arial', 9, 'bold'))
                title_label.grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
                
                # Session info
                info_text = f"{session['interface_type']} • {session['updated_at'][:16]}"
                info_label = ttk.Label(content_frame, text=info_text, 
                                      font=('Arial', 8), foreground='gray')
                info_label.grid(row=1, column=0, sticky=tk.W, padx=3, pady=(0, 2))
                
                # Delete button
                delete_btn = ttk.Button(session_frame, text="🗑️", width=3,
                                       command=lambda sid=session['session_id'], title=session['title']: self.delete_session_with_confirmation(sid, title))
                delete_btn.grid(row=0, column=1, padx=(2, 5), pady=2, sticky=tk.E)
                
                # Make content clickable (but not delete button)
                content_frame.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
                title_label.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
                info_label.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
                
                # Hover effects
                def on_enter(e, frame=session_frame):
                    frame.configure(relief="raised")
                def on_leave(e, frame=session_frame):
                    frame.configure(relief="solid")
                
                session_frame.bind("<Enter>", on_enter)
                session_frame.bind("<Leave>", on_leave)
                content_frame.bind("<Enter>", on_enter)
                content_frame.bind("<Leave>", on_leave)
                
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def delete_session_with_confirmation(self, session_id: str, session_title: str):
        """Delete a chat session with confirmation dialog and comprehensive cleanup"""
        if not CHAT_HISTORY_AVAILABLE or not self.chat_history:
            return
        
        # Show enhanced confirmation dialog
        result = messagebox.askyesno(
            "Delete Chat Session & Associated Files",
            f"Are you sure you want to delete this chat session?\n\n"
            f"Title: {session_title}\n"
            f"Session ID: {session_id}\n\n"
            f"This will permanently delete:\n"
            f"• All chat messages and session data\n"
            f"• Associated CloudFormation templates (local)\n"
            f"• Uploaded S3 template files\n"
            f"• Nova-Act instruction files\n\n"
            f"This action cannot be undone.",
            icon='warning'
        )
        
        if result:
            try:
                # Import template cleanup manager
                from template_cleanup_manager import template_cleanup
                
                # Perform comprehensive cleanup
                cleanup_result = template_cleanup.cleanup_session_files(session_title, session_id)
                
                # Delete from database
                self.chat_history.delete_session(session_id)
                
                # If this was the current session, clear it
                if self.current_session_id == session_id:
                    self.current_session_id = None
                    # Clear the chat display
                    if hasattr(self, 'chat_display'):
                        self.chat_display.config(state='normal')
                        self.chat_display.delete(1.0, tk.END)
                        self.chat_display.config(state='disabled')
                        # Add welcome message for new session
                        self.add_chat_message("🤖 InfrastructBot", 
                                            "Session deleted. Start a new conversation by sending a message!")
                
                # Refresh the sessions list
                self.load_recent_sessions()
                
                # Show detailed success message
                cleanup_summary = f"Chat session '{session_title}' has been deleted successfully.\n\n"
                cleanup_summary += f"Files cleaned up:\n"
                
                if cleanup_result['local_files_deleted']:
                    cleanup_summary += f"✅ Local files deleted ({len(cleanup_result['local_files_deleted'])}):\n"
                    for file_path in cleanup_result['local_files_deleted']:
                        cleanup_summary += f"   • {os.path.basename(file_path)}\n"
                
                if cleanup_result['s3_cleanup_message']:
                    cleanup_summary += f"\n📤 S3 cleanup: {cleanup_result['s3_cleanup_message']}\n"
                
                if cleanup_result['local_files_failed']:
                    cleanup_summary += f"\n⚠️ Some files couldn't be deleted:\n"
                    for failed_file in cleanup_result['local_files_failed']:
                        cleanup_summary += f"   • {failed_file}\n"
                
                cleanup_summary += f"\nTotal files cleaned: {cleanup_result['total_files_cleaned']}"
                
                messagebox.showinfo("Session & Files Deleted", cleanup_summary)
                
            except ImportError:
                # Fallback to basic deletion if cleanup manager not available
                self.chat_history.delete_session(session_id)
                self.load_recent_sessions()
                messagebox.showinfo("Session Deleted", 
                                  f"Chat session '{session_title}' deleted.\n"
                                  f"Note: Template cleanup not available - files may remain in iac_templates folder.")
                
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete session: {str(e)}")
    
    def clear_all_sessions(self):
        """Clear all chat sessions with confirmation and comprehensive file cleanup"""
        if not CHAT_HISTORY_AVAILABLE or not self.chat_history:
            return
        
        # Get session count for confirmation
        try:
            sessions = self.chat_history.get_recent_sessions(1000)  # Get all sessions
            session_count = len(sessions)
            
            if session_count == 0:
                messagebox.showinfo("No Sessions", "There are no chat sessions to delete.")
                return
            
            # Show enhanced confirmation dialog
            result = messagebox.askyesno(
                "Clear All Sessions & Associated Files",
                f"Are you sure you want to delete ALL {session_count} chat sessions?\n\n"
                f"This will permanently delete:\n"
                f"• All {session_count} chat sessions and messages\n"
                f"• All CloudFormation templates in iac_templates folder\n"
                f"• All Nova-Act instruction files\n"
                f"• Saved plans, diagrams, and deployment configurations\n\n"
                f"This action cannot be undone.\n"
                f"Consider exporting important data before proceeding.",
                icon='warning'
            )
            
            if result:
                try:
                    # Import template cleanup manager
                    from template_cleanup_manager import template_cleanup
                    
                    # Perform bulk template cleanup
                    cleanup_result = template_cleanup.bulk_cleanup_all_templates()
                    
                    # Delete all sessions from database
                    for session in sessions:
                        self.chat_history.delete_session(session['session_id'])
                    
                    # Clear current session
                    self.current_session_id = None
                    
                    # Clear the chat display
                    if hasattr(self, 'chat_display'):
                        self.chat_display.config(state='normal')
                        self.chat_display.delete(1.0, tk.END)
                        self.chat_display.config(state='disabled')
                        # Add welcome message
                        self.add_chat_message("🤖 InfrastructBot", 
                                            "All sessions and files cleared. Start a new conversation by sending a message!")
                    
                    # Refresh the sessions list
                    self.load_recent_sessions()
                    
                    # Show detailed success message
                    cleanup_summary = f"Successfully deleted all {session_count} chat sessions.\n\n"
                    cleanup_summary += f"Files cleaned up:\n"
                    
                    if cleanup_result['local_files_deleted']:
                        cleanup_summary += f"✅ Local files deleted ({len(cleanup_result['local_files_deleted'])}):\n"
                        # Show first few files, then summarize if many
                        shown_files = cleanup_result['local_files_deleted'][:5]
                        for file_path in shown_files:
                            cleanup_summary += f"   • {os.path.basename(file_path)}\n"
                        
                        if len(cleanup_result['local_files_deleted']) > 5:
                            remaining = len(cleanup_result['local_files_deleted']) - 5
                            cleanup_summary += f"   • ... and {remaining} more files\n"
                    
                    if cleanup_result['s3_cleanup_message']:
                        cleanup_summary += f"\n📤 S3 cleanup: {cleanup_result['s3_cleanup_message']}\n"
                    
                    if cleanup_result['local_files_failed']:
                        cleanup_summary += f"\n⚠️ Some files couldn't be deleted ({len(cleanup_result['local_files_failed'])}):\n"
                        for failed_file in cleanup_result['local_files_failed'][:3]:
                            cleanup_summary += f"   • {failed_file}\n"
                        if len(cleanup_result['local_files_failed']) > 3:
                            cleanup_summary += f"   • ... and more\n"
                    
                    cleanup_summary += f"\nTotal files cleaned: {cleanup_result['total_files_cleaned']}"
                    
                    messagebox.showinfo("All Sessions & Files Cleared", cleanup_summary)
                    
                except ImportError:
                    # Fallback to basic deletion if cleanup manager not available
                    for session in sessions:
                        self.chat_history.delete_session(session['session_id'])
                    
                    self.current_session_id = None
                    self.load_recent_sessions()
                    
                    messagebox.showinfo("Sessions Cleared", 
                                      f"Successfully deleted all {session_count} chat sessions.\n"
                                      f"Note: Template cleanup not available - files may remain in iac_templates folder.")
                
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear sessions: {str(e)}")
    
    def search_sessions(self, event=None):
        """Search sessions based on query"""
        query = self.search_var.get().strip()
        if query:
            sessions = self.chat_history.search_sessions(query, 10)
        else:
            sessions = self.chat_history.get_recent_sessions(20)
        
        # Update sessions display
        for widget in self.scrollable_sessions.winfo_children():
            widget.destroy()
        
        for i, session in enumerate(sessions):
            session_frame = ttk.Frame(self.scrollable_sessions, relief="solid", borderwidth=1)
            session_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2, padx=2)
            session_frame.columnconfigure(0, weight=1)
            
            # Create content frame for session info
            content_frame = ttk.Frame(session_frame)
            content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
            content_frame.columnconfigure(0, weight=1)
            
            # Session title
            title_label = ttk.Label(content_frame, text=session['title'][:30] + "..." if len(session['title']) > 30 else session['title'],
                                   font=('Arial', 9, 'bold'))
            title_label.grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
            
            # Session info
            info_text = f"{session['interface_type']} • {session['updated_at'][:16]}"
            info_label = ttk.Label(content_frame, text=info_text, 
                                  font=('Arial', 8), foreground='gray')
            info_label.grid(row=1, column=0, sticky=tk.W, padx=3, pady=(0, 2))
            
            # Delete button
            delete_btn = ttk.Button(session_frame, text="🗑️", width=3,
                                   command=lambda sid=session['session_id'], title=session['title']: self.delete_session_with_confirmation(sid, title))
            delete_btn.grid(row=0, column=1, padx=(2, 5), pady=2, sticky=tk.E)
            
            # Make content clickable (but not delete button)
            content_frame.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
            title_label.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
            info_label.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
            
            # Hover effects
            def on_enter(e, frame=session_frame):
                frame.configure(relief="raised")
            def on_leave(e, frame=session_frame):
                frame.configure(relief="solid")
            
            session_frame.bind("<Enter>", on_enter)
            session_frame.bind("<Leave>", on_leave)
            content_frame.bind("<Enter>", on_enter)
            content_frame.bind("<Leave>", on_leave)
            
            info_text = f"{session['interface_type']} • {session['updated_at'][:16]}"
            info_label = ttk.Label(session_frame, text=info_text, 
                                  font=('Arial', 8), foreground='gray')
            info_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=(0, 2))
            
            session_frame.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
            title_label.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
            info_label.bind("<Button-1>", lambda e, sid=session['session_id']: self.load_session(sid))
    
    def load_session(self, session_id: str):
        """Load a previous chat session"""
        try:
            # Get session data
            session_data = self.chat_history.get_session_data(session_id)
            messages = self.chat_history.get_session_messages(session_id)
            
            if not session_data:
                messagebox.showerror("Error", "Session not found")
                return
            
            # Clear current chat
            self.chat_display.config(state='normal')
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state='disabled')
            
            # Load messages
            for message in messages:
                self.add_chat_message(message['sender'], message['message'], save_to_db=False)
            
            # Restore session data
            self.current_session_id = session_id
            if session_data['plan_data']:
                self.current_plan = session_data['plan_data']
                self.update_plan_display()
            
            if session_data['diagram_data']:
                self.current_diagram = session_data['diagram_data']
                self.update_diagram_display()
            
            if session_data['estimate_data']:
                self.current_estimate = session_data['estimate_data']
            
            if session_data['template_data']:
                self.current_template = session_data['template_data']
                self.update_template_display()
            
            self.workflow_state = session_data['workflow_state'] or 'initial'
            
            # Update environment ID
            if 'envid' in session_data.get('plan_data', ''):
                # Try to extract envid from plan data
                pass
            
            messagebox.showinfo("Session Loaded", f"Loaded session: {session_data['title']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")
    
    def start_new_session(self):
        """Start a new chat session"""
        # Clear current session
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        
        # Reset data
        self.current_plan = ""
        self.current_template = ""
        self.current_diagram = ""
        self.current_estimate = ""
        self.current_session_id = None
        self.workflow_state = "initial"
        
        # Clear displays
        self.plan_display.config(state='normal')
        self.plan_display.delete(1.0, tk.END)
        self.plan_display.config(state='disabled')
        
        self.diagram_display.config(state='normal')
        self.diagram_display.delete(1.0, tk.END)
        self.diagram_display.config(state='disabled')
        
        self.template_display.config(state='normal')
        self.template_display.delete(1.0, tk.END)
        self.template_display.config(state='disabled')
        
        # Add welcome message
        welcome_msg = """Welcome to a new session! 🚀

Describe your AWS infrastructure needs and I'll guide you through the complete workflow."""
        
        self.add_chat_message("🤖 InfrastructBot", welcome_msg)
    
    def start_new_chat(self):
        """Start a new chat session from the chat interface"""
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
        self.current_diagram_image = None
        self.current_session_id = None
        self.workflow_state = "initial"
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
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Ready", foreground='green')
        
        # Re-enable input if it was disabled
        self.user_input.config(state='normal')
        self.send_btn.config(state='normal')
        
        # Focus on input field
        self.user_input.focus()
        
        # Switch back to chat tab
        self.notebook.select(0)
        
        # Refresh session list if chat history is available
        if CHAT_HISTORY_AVAILABLE and hasattr(self, 'load_recent_sessions'):
            self.load_recent_sessions()
        
        # Add welcome message for new session
        welcome_msg = """🆕 New Chat Session Started! 🚀

I'll guide you through a complete infrastructure workflow:
1. 📋 Architecture Planning - Detailed technical specifications
2. 🏗️ Visual Diagramming - Component relationships and data flow
3. 💰 Cost Estimation - Monthly pricing breakdown with tables
4. 📄 Template Generation - Infrastructure as Code (YAML) with proper tagging
5. 🚀 AWS Deployment - One-click deployment to your account

Simply describe what you want to build and I'll handle the complete workflow automatically!

What infrastructure would you like to create today?"""
        
        self.add_chat_message("🤖 InfrastructBot", welcome_msg)
    
    def update_envid(self, event=None):
        """Update environment ID"""
        self.envid = self.envid_var.get().strip() or "dev"
        self.enhanced_templating_tool.default_envid = self.envid
    
    def add_chat_message(self, sender, message, save_to_db=True):
        """Add a message to the chat display and optionally save to database"""
        self.chat_display.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n{message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
        # Save to database (if available)
        if save_to_db and CHAT_HISTORY_AVAILABLE and self.chat_history and self.current_session_id:
            self.chat_history.add_message(self.current_session_id, sender, message)

def main():
    root = tk.Tk()
    app = InfrastructGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()