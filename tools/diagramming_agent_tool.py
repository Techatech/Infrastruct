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
def create_architecture_diagram(query: str) -> str:
    """
    Creates visual architecture diagrams from cloud infrastructure plans using AWS documentation.

    Args:
        query (str): A cloud infrastructure plan for a project from user input

    Returns:
        str: Architecture diagram description and recommendations
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

            # Create the diagramming agent with specific capabilities
            diagramming_agent = Agent(
                model=bedrock_model,
                tools=tools,
                system_prompt="""You are an AWS architecture diagram creator. Provide SIMPLE diagram descriptions only.

                For each plan, provide:
                1. List of components (boxes)
                2. Connections between components (arrows)
                3. Data flow direction
                4. One recommended diagramming tool

                Format:
                Components: [S3, CloudFront, Route53]
                Flow: User → Route53 → CloudFront → S3
                Tool: draw.io or Lucidchart

                Keep under 50 words. No detailed explanations.
                """
            )
            response = str(diagramming_agent(query))
            print("\n\n")
            
            if len(response) > 0:
                return response

        return "I apologize, but I couldn't properly analyze your question. Could you please rephrase or provide more context?"

    except Exception as e:
        return f"Error processing your query: {str(e)}"