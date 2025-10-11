import os
from strands import Agent, tool
from strands.models import BedrockModel
from tools.deployer_agent_tool import deploy_infrastructure
from tools.templating_agent_tool import gen_template
from tools.planner_agent_tool import plan_architecture
from tools.estimator_agent_tool import estimate_price
from dotenv import load_dotenv

# Show rich UI for tools in CLI
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"
# This line loads the variables from .env into the environment
load_dotenv()



# Create a BedrockModel
bedrock_model = BedrockModel(
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



aws_infrastruct_agent = Agent(model=bedrock_model,
              system_prompt= SYSTEM_PROMPT,
              tools=[
               plan_architecture,
               estimate_price,
               gen_template,
               deploy_infrastructure

               ]


             )

if __name__ == "__main__":
    print("=============================================================================")
    print("🤖  WELCOME TO AWS INFRASTRUCT  🤖")
    print("=============================================================================")
    print("✨ I'm your intelligent AWS Cloud Architect with access to:")
    print("   📅 Planning Assistant - Plan the best architecture for your project")
    print("   💰 Costing Assistant - Estimate the cost of running your plan in the AWS cloud")
    print("   💻 Templating Assistant - Generate Infrastructure as Code template (IaC) for your plan")
    print("   🚀 Deployment Assistant - Deploy IaC template to your AWS Account")
    print()
    print("🎯 I can handle end to end cloud infrastructure delivery from planning to deployment:")
    print("   • 'a static website for my portfolio'")
    print("   • 'i need a scalable web server for a new application'")
    print("   • 'We need a platform that can store and process data in real time'")
    print()
    print("💡 Just tell me what you need - I'll coordinate everything!")
    print("🚪 Type 'exit' to quit anytime")
    print("=============================================================================")
    print()

    # Initialize the personal assistant
    try:
        print("🔄 Initializing AWS Infrastruct...")
        print("✅ AWS Infrastruct ready!")
        print("🤖 All specialized agents are available!")
        print()
    except Exception as e:
        print(f"❌ Error initializing AWS Infrastruct: {str(e)}")

    # Run the agent in a loop for interactive conversation
    while True:
        try:
            user_input = input("👤 You: ").strip()
            if not user_input:
                print("💭 Please tell me how I can help you, or type 'exit' to quit")
                continue
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print()
                print("=========================================================")
                print("👋 Thank you for using AWS Infrastruct!")
                print("🎉 Have a productive day ahead!")
                print("🤖 Come back anytime you need help!")
                print("=========================================================")
                break

            print("🤖 InfrastructBot: ", end="")
            response = aws_infrastruct_agent(user_input)
            print("\n")

        except KeyboardInterrupt:
            print("\n")
            print("=========================================================")
            print("👋 AWS Infrastruct interrupted!")
            print("🤖 See you next time!")
            print("=========================================================")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("🔧 Please try again or type 'exit' to quit")
            print()