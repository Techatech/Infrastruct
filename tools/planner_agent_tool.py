import threading
import time
from datetime import timedelta

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

@tool
def plan_architecture(query: str) -> str:
    """
   Handles cloud architecture planning  queries by suggesting appropriate cloud  architectural pattern.


    Args:
        query (str): A cloud infrastructure inquiry for a project from  user input

    Returns:
       Personalized cloud architecture infrastructure plan
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
            planner_agent = Agent(
                model=bedrock_model,
                tools=tools,
                system_prompt="""AWS architecture planner. Be EXTREMELY concise.

                Format:
                Services needed:
                • Service 1 - reason (quantity)
                • Service 2 - reason (quantity)
                • Service 3 - reason (quantity)

                Key principle: [Well-Architected pillar]

                Max 100 words total. No explanations.
                """
            )
            response = str(planner_agent(query))
            print("\n\n")
            
            if len(response) > 0:
                return response

        return "I apologize, but I couldn't properly analyze your question. Could you please rephrase or provide more context?"

    # Return specific error message for English queries
    except Exception as e:
         return f"Error processing your query: {str(e)}"



