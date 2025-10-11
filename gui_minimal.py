import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
from datetime import datetime
from strands import Agent
from strands.models import BedrockModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MinimalInfrastructGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AWS Infrastruct - Minimal GUI")
        self.root.geometry("1000x700")
        
        # Initialize the agent
        self.setup_agent()
        
        # Store current data
        self.current_plan = ""
        self.is_processing = False
        self.envid = "dev"
        
        # Create the interface
        self.create_widgets()
        
    def setup_agent(self):
        """Initialize the AWS Infrastructure Agent"""
        try:
            os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"
            
            self.bedrock_model = BedrockModel(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                region_name="us-east-1"
            )
            
            # Import tools individually to avoid circular imports
            from tools.planner_agent_tool import plan_architecture
            from tools.estimator_agent_tool import estimate_price
            from tools.templating_agent_tool import gen_template
            from tools.deployer_agent_tool import deploy_infrastructure
            
            self.plan_architecture = plan_architecture
            self.estimate_price = estimate_price
            self.gen_template = gen_template
            self.deploy_infrastructure = deploy_infrastructure
            
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
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 AWS Infrastruct - Minimal GUI", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(main_frame, height=25, width=100, 
                                                     font=('Consolas', 10), state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User input
        self.user_input = ttk.Entry(input_frame, font=('Arial', 10))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind('<Return>', self.send_message)
        
        # Send button
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)
        
        # Environment ID
        env_frame = ttk.Frame(main_frame)
        env_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(env_frame, text="Environment ID:").pack(side=tk.LEFT, padx=(0, 5))
        self.envid_var = tk.StringVar(value=self.envid)
        envid_entry = ttk.Entry(env_frame, textvariable=self.envid_var, width=10)
        envid_entry.pack(side=tk.LEFT)
        envid_entry.bind('<KeyRelease>', self.update_envid)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready", 
                                     font=('Arial', 10), foreground='green')
        self.status_label.pack()
        
        # Add welcome message
        welcome_msg = """Welcome to AWS Infrastruct Minimal GUI! 🚀

This is a simplified version that avoids problematic imports.

Describe your AWS infrastructure needs and I'll help you plan, estimate, template, and deploy!

Example: "I need a static website for my portfolio"
"""
        
        self.add_chat_message("🤖 InfrastructBot", welcome_msg)
    
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
        self.add_chat_message("🔄 Processing", "Working on your request...")
        
        # Process message in background thread
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message):
        """Process message with the agent"""
        try:
            self.root.after(0, lambda: self.status_label.config(text="Processing...", foreground='orange'))
            
            # Get response from agent
            response = str(self.aws_infrastruct_agent(message))
            
            # Add response to chat
            self.root.after(0, lambda: self.add_chat_message("🤖 InfrastructBot", response))
            
            self.root.after(0, lambda: self.status_label.config(text="Ready", foreground='green'))
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.root.after(0, lambda: self.add_chat_message("❌ Error", error_msg))
            self.root.after(0, lambda: self.status_label.config(text="Error", foreground='red'))
        finally:
            # Re-enable input
            self.root.after(0, self.enable_input)
    
    def enable_input(self):
        """Re-enable input controls after processing"""
        self.user_input.config(state='normal')
        self.send_btn.config(state='normal')
        self.is_processing = False
        self.user_input.focus()
    
    def update_envid(self, event=None):
        """Update environment ID"""
        self.envid = self.envid_var.get().strip() or "dev"

def main():
    root = tk.Tk()
    app = MinimalInfrastructGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()