from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Fifth Elephant")


# Add a hello world tool
@mcp.tool()
def hello_world() -> str:
    """Returns a friendly greeting."""
    return "hello world"


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run()
