import os
from strands import Agent, tool
from strands.models import BedrockModel
from tools.deployer_agent_tool import deploy_infrastructure
from tools.templating_agent_tool import gen_template
from tools.planner_agent_tool import plan_architecture
from tools.estimator_agent_tool import estimate_price
from tools.enhanced_diagramming_tool import EnhancedDiagramGenerator
from tools.enhanced_templating_tool import EnhancedTemplatingTool
from database.chat_history import ChatHistoryManager
from dotenv import load_dotenv
from datetime import datetime

# Show rich UI for tools in CLI
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"
# This line loads the variables from .env into the environment
load_dotenv()

class EnhancedInfrastructCLI:
    def __init__(self):
        # Initialize enhanced tools
        self.enhanced_diagram_generator = EnhancedDiagramGenerator()
        self.enhanced_templating_tool = EnhancedTemplatingTool()
        self.chat_history = ChatHistoryManager()
        
        # Environment ID
        self.envid = "dev"
        
        # Current session
        self.current_session_id = None
        
        # Create a BedrockModel
        self.bedrock_model = BedrockModel(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name="us-east-1"
        )

        SYSTEM_PROMPT = """
        You are a professional AWS CLOUD SOLUTIONS ARCHITECT that assists 
        AWS customers with end to end cloud infrastructure delivery from planning to deployment.

        You have access to the following tools :
        * plan_architecture :  Handles cloud architecture plan recommendation queries by suggesting appropriate cloud  architectural pattern.
        * estimate_price : Handles cloud architecture plan pricing by suggesting an estimate price for the provided cloud  architectural plan.
        * gen_template  : Generates InfraStructure as Code (IaC) template from the cloud infrastructure plan .
        * deploy_infrastructure : Automates tasks in browser based on instructions provided to deploy a cloudformation IaC. .

        When a users requests for  a cloud architecture infrastructure plan always follow this process from 1 to 7:
        1. First route the task enquiry to the plan_architecture tool to get the detailed cloud infrastructure plan.
        2. Present the detailed cloud infrastructure plan from the plan_architecture tool to the user and prompt the user  if they want to estimate
           the monthly cost of running the detailed cloud infrastructure plan from the plan_architecture tool.
        3. if the user agrees to the cost estimation, feed the detailed plan from the plan_architecture tool to the estimate_price tool.
           Else if they decline, offer a polite and contextually appropriate response.
        4. Present the cost estimation from the estimate_price tool to the user and prompt the user if they want to deploy the 
           cloud infrastructure plan to their AWS Account.
        5. if the user agrees, feed the detailed cloud infrastructure plan from the plan_architecture tool to the
           gen_template tool then provide a response to the user that says: Generating your Cloud Infrastructure Plan template...please wait.
           Else if they decline, offer a polite and contextually appropriate response.
        6. When the gen_template tool has completed execution, extract the public_url and stack_name and feed them to the
           deploy_infrastructure tool then provide a response to the user that says:
            Template ready...starting automated deployment: stand-by to provide AWS Account login details.
        7. Wait for the deploy_infrastructure tool to finish execution and then relay the response it generates back to the user.

        IMPORTANT: Always ensure the following for successful execution:
        - The initial enquiry is first handed over to the plan_architecture tool as a parameter after a determination that its a 
          planning enquiry, if not the appropriate agent can handle the enquiry.
        - The output of the plan_architecture tool in the form of a detailed cloud infrastructure plan should be handed over to both
          the estimate_price tool and the gen_template tool as a parameter.
        -  The output of the gen_template tool namely the 'public_url' and 'stack_name' should be handed over to the
          deploy_infrastructure tool as parameters.
        - in the event that the process order from 1 to 7 has been broken due to a user asking a direct question, you are to create
         a new process to extract the required information to answer  the user's enquiry. For example, a user instead of providing
         you with a description of what they what to build they may ask about a service or its price. Your role is to steer the
         conversation in a way that answers their question or enquiry then asks if they can provide details of what they want
         to build and deploy to the AWS Cloud.
         -Never assume parameters to tools, if they are not provided create a conversational loop to extract them from the user.
          
        You are to engage in conversations that are socially morally acceptable and polite in the professional context and stick
        to the Cloud Infrastructure  Architecture topics in particular AWS and its associated services. Any other topic that 
        the user may bring to your you are to politely tell the user that you do not have information about it and steer them 
        back to helping them build an amazing tech stack in the AWS Cloud.

        """

        self.aws_infrastruct_agent = Agent(model=self.bedrock_model,
                      system_prompt= SYSTEM_PROMPT,
                      tools=[
                       plan_architecture,
                       estimate_price,
                       gen_template,
                       deploy_infrastructure
                       ]
                     )
    
    def show_welcome(self):
        """Show enhanced welcome message"""
        print("=" * 80)
        print("🤖  WELCOME TO ENHANCED AWS INFRASTRUCT  🤖")
        print("=" * 80)
        print("✨ Enhanced features:")
        print("   📅 Planning Assistant - Plan the best architecture for your project")
        print("   🎨 Visual Diagramming - Generate actual architecture diagrams with AWS icons")
        print("   💰 Costing Assistant - Estimate the cost of running your plan in the AWS cloud")
        print("   📄 Enhanced Templating - Generate IaC templates with proper tagging")
        print("   🚀 Deployment Assistant - Deploy IaC template to your AWS Account")
        print("   📚 Chat History - All conversations automatically saved")
        print()
        print("🏷️  Enhanced Tagging Convention:")
        print(f"   • Name: {self.envid}-ResourceType-##")
        print(f"   • Environment: {self.envid}")
        print("   • CreatedBy: Infrastruct")
        print()
        print("🎯 I can handle end to end cloud infrastructure delivery from planning to deployment:")
        print("   • 'a static website for my portfolio'")
        print("   • 'i need a scalable web server for a new application'")
        print("   • 'We need a platform that can store and process data in real time'")
        print()
        print("💡 Commands:")
        print("   • 'history' - View recent sessions")
        print("   • 'load <session_id>' - Load a previous session")
        print("   • 'envid <environment>' - Set environment ID for tagging")
        print("   • 'exit' - Quit")
        print("=" * 80)
        print()
    
    def show_history(self):
        """Show recent chat sessions"""
        sessions = self.chat_history.get_recent_sessions(10)
        
        if not sessions:
            print("📚 No previous sessions found.")
            return
        
        print("\n📚 Recent Sessions:")
        print("-" * 60)
        for session in sessions:
            print(f"🔹 {session['session_id']}")
            print(f"   Title: {session['title']}")
            print(f"   Updated: {session['updated_at']}")
            print(f"   Interface: {session['interface_type']}")
            print(f"   State: {session['workflow_state']}")
            print()
    
    def load_session(self, session_id: str):
        """Load a previous session"""
        session_data = self.chat_history.get_session_data(session_id)
        messages = self.chat_history.get_session_messages(session_id)
        
        if not session_data:
            print(f"❌ Session {session_id} not found.")
            return
        
        print(f"\n📂 Loading session: {session_data['title']}")
        print("-" * 60)
        
        for message in messages:
            timestamp = message['timestamp'][:19]  # Remove microseconds
            print(f"[{timestamp}] {message['sender']}:")
            print(f"{message['message']}\n")
        
        self.current_session_id = session_id
        print(f"✅ Session loaded. Continue the conversation...")
    
    def set_envid(self, envid: str):
        """Set environment ID"""
        self.envid = envid.strip()
        self.enhanced_templating_tool.default_envid = self.envid
        print(f"🏷️  Environment ID set to: {self.envid}")
        print(f"   Resources will be tagged as: {self.envid}-ResourceType-##")
    
    def process_enhanced_workflow(self, user_input: str):
        """Process user input with enhanced workflow"""
        try:
            # Create session if needed
            if not self.current_session_id:
                title = user_input[:50] + "..." if len(user_input) > 50 else user_input
                self.current_session_id = self.chat_history.create_session(title, "CLI")
            
            # Save user message
            self.chat_history.add_message(self.current_session_id, "👤 You", user_input)
            
            print("🔄 Processing your request through enhanced workflow...")
            
            # Step 1: Plan Architecture
            print("\n📋 Step 1: Planning Architecture...")
            plan_response = plan_architecture(user_input)
            current_plan = str(plan_response)
            print(f"✅ Architecture plan created")
            
            # Save plan message
            self.chat_history.add_message(self.current_session_id, "📋 Architecture Plan", current_plan)
            
            # Step 2: Generate Enhanced Diagram
            print("\n🎨 Step 2: Generating Enhanced Diagram...")
            diagram_path = self.enhanced_diagram_generator.create_architecture_diagram(current_plan, f"{self.envid} Architecture")
            
            if diagram_path.endswith('.png'):
                diagram_msg = f"✅ Visual diagram created: {diagram_path}"
                print(diagram_msg)
                diagram_summary = self.enhanced_diagram_generator.get_diagram_summary(current_plan)
                print(f"\n🏗️ Diagram Summary:\n{diagram_summary}")
                current_diagram = f"{diagram_msg}\n\n{diagram_summary}"
            else:
                current_diagram = diagram_path
                print(f"✅ Text diagram created")
            
            # Save diagram message
            self.chat_history.add_message(self.current_session_id, "🏗️ Architecture Diagram", current_diagram)
            
            # Step 3: Cost Estimation
            print("\n💰 Step 3: Estimating Costs...")
            estimate_response = estimate_price(current_plan)
            current_estimate = str(estimate_response)
            print(f"✅ Cost estimate completed")
            
            # Save estimate message
            self.chat_history.add_message(self.current_session_id, "💰 Cost Estimate", current_estimate)
            
            # Step 4: Generate Enhanced Template
            print("\n📄 Step 4: Generating Enhanced Template with Proper Tagging...")
            enhanced_template = self.enhanced_templating_tool.create_enhanced_template(current_plan, self.envid)
            print(f"✅ Enhanced template generated with {self.envid} environment tagging")
            
            template_msg = f"""Enhanced Infrastructure template generated!

✨ Features:
• Environment ID: {self.envid}
• Proper resource tagging
• CloudFormation best practices

Template saved and ready for deployment."""
            
            # Save template message
            self.chat_history.add_message(self.current_session_id, "📄 Enhanced Template", template_msg)
            
            # Update session data
            self.chat_history.update_session_data(
                self.current_session_id,
                workflow_state="templating",
                plan_data=current_plan,
                diagram_data=current_diagram,
                estimate_data=current_estimate,
                template_data=enhanced_template
            )
            
            # Show completion
            print("\n🎉 Enhanced Workflow Complete!")
            print(f"📚 Session saved: {self.current_session_id}")
            print("🚀 Ready for deployment or further modifications")
            
        except Exception as e:
            error_msg = f"❌ Error in enhanced workflow: {str(e)}"
            print(error_msg)
            if self.current_session_id:
                self.chat_history.add_message(self.current_session_id, "❌ Error", error_msg)
    
    def run(self):
        """Run the enhanced CLI interface"""
        self.show_welcome()
        
        try:
            print("🔄 Initializing Enhanced AWS Infrastruct...")
            print("✅ Enhanced AWS Infrastruct ready!")
            print("🤖 All enhanced agents are available!")
            print()
        except Exception as e:
            print(f"❌ Error initializing Enhanced AWS Infrastruct: {str(e)}")

        # Run the agent in a loop for interactive conversation
        while True:
            try:
                user_input = input("👤 You: ").strip()
                if not user_input:
                    print("💭 Please tell me how I can help you, or type 'exit' to quit")
                    continue
                
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print()
                    print("=" * 60)
                    print("👋 Thank you for using Enhanced AWS Infrastruct!")
                    print("🎉 Have a productive day ahead!")
                    print("🤖 Come back anytime you need help!")
                    print("=" * 60)
                    break
                
                # Handle special commands
                if user_input.lower() == "history":
                    self.show_history()
                    continue
                
                if user_input.lower().startswith("load "):
                    session_id = user_input[5:].strip()
                    self.load_session(session_id)
                    continue
                
                if user_input.lower().startswith("envid "):
                    envid = user_input[6:].strip()
                    self.set_envid(envid)
                    continue
                
                # Process with enhanced workflow
                print("🤖 Enhanced InfrastructBot: Processing...")
                self.process_enhanced_workflow(user_input)
                print()

            except KeyboardInterrupt:
                print("\n")
                print("=" * 60)
                print("👋 Enhanced AWS Infrastruct interrupted!")
                print("🤖 See you next time!")
                print("=" * 60)
                break
            except Exception as e:
                print(f"❌ An error occurred: {str(e)}")
                print("🔧 Please try again or type 'exit' to quit")
                print()

def main():
    cli = EnhancedInfrastructCLI()
    cli.run()

if __name__ == "__main__":
    main()