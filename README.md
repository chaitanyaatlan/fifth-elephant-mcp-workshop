# Fifth Elephant MCP - DIY Guide

This guide will walk you through building a Model Context Protocol (MCP) server from scratch using TypeScript. By the end of this tutorial, you'll have created a functional MCP server with two tools: a simple "Hello World" tool and a BMI calculator.

## What is MCP?

The Model Context Protocol (MCP) is a standard for AI assistants to communicate with external data sources and tools. It enables AI models to access real-time information, perform calculations, and interact with various services through a standardized interface.

## Prerequisites

- Node.js (version 18 or higher)
- npm (comes with Node.js)
- Basic understanding of TypeScript/JavaScript

## Step 1: Initialize the Project

First, let's create a new directory and initialize a Node.js project:

```bash
mkdir fifth-elephant-mcp
cd fifth-elephant-mcp
npm init -y
```

This creates a `package.json` file with default values.

## Step 2: Install Dependencies

Install the MCP SDK and TypeScript development dependencies:

```bash
npm install @modelcontextprotocol/sdk
```


## Step 3: Create the MCP Server

Create a file called `server.ts` and add the following code:

```typescript
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
```

## Step 4: Understanding the Code

Let's break down what we just created:

### Server Setup
```typescript
const server = new McpServer({
  name: "fifth-elephant-mcp",
  version: "1.0.0"
});
```
This creates a new MCP server instance with a name and version.

### Tool Registration
```typescript
server.registerTool(
  "hello_world",  // Tool identifier
  {
    title: "Hello World",  // Human-readable title
    description: "Returns a friendly greeting",  // Tool description
    inputSchema: {}  // No input parameters needed
  },
  async () => ({  // Tool implementation
    content: [{ type: "text", text: "Hello, World!" }]
  })
);
```

### Input Schema with Zod
```typescript
inputSchema: {
  weightKg: z.number(),
  heightM: z.number()
}
```
We use Zod for input validation. This ensures that `weightKg` and `heightM` are numbers.

### Transport Layer
```typescript
const transport = new StdioServerTransport();
await server.connect(transport);
```
This sets up the communication channel using standard input/output.

## Step 5: Test Your MCP Server

Now it's time to test your MCP server! Use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector node server.ts
```

This command will:
1. Start the MCP Inspector (a testing tool)
2. Launch your server
3. Provide an interactive interface to test your tools

### Testing Your Tools

In the inspector, you can:

1. **Test the Hello World tool:**
   - Select the "hello_world" tool
   - Click "Call Tool"
   - You should see "Hello, World!" as the response

2. **Test the BMI Calculator:**
   - Select the "calculate-bmi" tool
   - Enter values for `weightKg` (e.g., 70) and `heightM` (e.g., 1.75)
   - Click "Call Tool"
   - You should see the calculated BMI value


## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Typescript SDK GitHub](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)

