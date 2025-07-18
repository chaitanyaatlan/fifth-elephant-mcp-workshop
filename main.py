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

@mcp.prompt()
def prompt(task: str) -> str:
    """Returns a friendly greeting."""
    return f"You are a helpful assistant that can help with the following task: {task}"

@mcp.resource("greeting:/greeting.txt")
def greeting() -> str:
    """Returns a greeting."""
    return "Hey there, how are you? This is a greeting from the greeting resource."

if __name__ == "__main__":
    mcp.run()
