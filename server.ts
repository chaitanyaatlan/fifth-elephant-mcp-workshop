import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create an MCP server
const server = new McpServer({
  name: "fifth-elephant-mcp",
  version: "1.0.0"
});

// Add a hello world tool
server.registerTool(
  "hello_world",
  {
    title: "Hello World",
    description: "Returns a friendly greeting",
    inputSchema: {}
  },
  async () => ({
    content: [{ type: "text", text: "Hello, World!" }]
  })
);

// Simple BMI Calculator
server.registerTool(
  "calculate-bmi",
  {
    title: "BMI Calculator",
    description: "Calculate Body Mass Index",
    inputSchema: {
      weightKg: z.number(),
      heightM: z.number()
    }
  },
  async ({ weightKg, heightM }) => ({
    content: [{
      type: "text",
      text: String(weightKg / (heightM * heightM))
    }]
  })
);


// Start the server with stdio transport
const transport = new StdioServerTransport();
await server.connect(transport); 