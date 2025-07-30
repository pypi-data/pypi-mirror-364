# server.py
from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("sum")


# Add an addition tool
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    print("Hello from abin-add-two-num!")
    mcp.run(transport="stdio")

