from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager
from universal_mcp_google_mail.app import GoogleMailApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="google-mail", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = GoogleMailApp(integration=integration)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.list_messages)
# tool_manager.add_tool(app_instance.get_message)
# tool_manager.add_tool(app_instance.send_email)    

async def main():
    # Get a specific tool by name
    tool = tool_manager.get_tool("list_messages")
    # tool = tool_manager.get_tool("get_message")
    # tool=tool_manager.get_tool("send_email")
    
    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    # Get all tools
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    # List tools in different formats
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    
    # Execute the tool
    result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="get_message", arguments={"message_id": "1983231f80877805"})
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@a.dev", "subject": " Email", "body": " test email"})
    print(result)

if __name__ == "__main__":
    anyio.run(main)