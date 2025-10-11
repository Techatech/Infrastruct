from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import FastMCP
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands_tools import file_write

from dotenv import load_dotenv

# This line loads the variables from .env into the environment
load_dotenv()
# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"

)

# Removed - causing duplication issues

@tool
def estimate_price(query: str) -> str:
    """
   Handles cloud architecture plan pricing  by suggesting an estimate price for the provided cloud  architectural plan.


    Args:
        query: Personalized cloud architecture infrastructure plan from the plan_architecture tool

    Returns:
       A estimate total cost of ownership (TCO) table
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
            costing_agent = Agent(
                model=bedrock_model,
                tools=tools,
                system_prompt="""AWS cost estimator. Return ONLY a simple cost table.

                Format:
                Service | Monthly Cost
                S3 | $50
                CloudFront | $100
                MediaConvert | $200
                TOTAL | $350

                No explanations. Just the table.
                """
            )
            response = str(costing_agent(query))
            print("\n\n")

        if len(response) > 0:
            # Return just the pricing response without additional processing
            return response

        return "Unable to estimate costs. Please provide more details."

    # Return specific error message for English queries
    except Exception as e:
        return f"Error processing your query: {str(e)}"


#if __name__ == "__main__":
   # estimate_price("What is the cost of Amazon Bedrock Claude Models")
