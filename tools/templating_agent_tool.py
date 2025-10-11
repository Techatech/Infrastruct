from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from dotenv import load_dotenv

# This line loads the variables from .env into the environment
load_dotenv()

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"

)


@tool
def gen_template(query: str) -> str:
    """
   Generates InfraStructure as Code (Iac) template from the cloud infrastructure plan .


    Args:
        query (str): Personalized cloud architecture infrastructure plan generated from the plan_architecture tool.

    Returns:
       public_url: public S3 bUcket url where the IaC template is stored for use when deploying.
       stack_name: the stack name for the template for use when deploying
    """


    try:
        # Connect to an MCP server using stdio transport
        aws_docs_mcp_client = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uv", args=["tool", "run", "awslabs.aws-documentation-mcp-server@latest"]
                )
            )
        )

        # Connect to an MCP server using stdio transport
        cdk_mcp_client = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(command="uv", args=["tool", "run", "awslabs.cdk-mcp-server@latest"])
            )
        )

        # Create an agent with MCP tools
        with aws_docs_mcp_client, cdk_mcp_client:
            # Get the tools from the MCP server
            tools = aws_docs_mcp_client.list_tools_sync() + cdk_mcp_client.list_tools_sync()
            # Create the research agent with specific capabilities
            templating_agent = Agent(
                model=bedrock_model,
                tools=tools,
                system_prompt="""CloudFormation generator. Return ONLY the YAML template.

                Include:
                - Essential resources only
                - Basic parameters
                - Required tags
                - Simple outputs

                No explanations. Just clean YAML code.
                """
            )
            response = str(templating_agent(query))
            print("\n\n")

        if len(response) > 0:
            # Return just the template response without additional processing
            return response

        return "Unable to generate template. Please provide more details."

    # Return specific error message for English queries
    except Exception as e:
        return f"Error processing your query: {str(e)}"


