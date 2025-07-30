from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager
from universal_mcp_reddit.app import RedditApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="reddit", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = RedditApp(integration=integration)
tool_manager = ToolManager()
# tool_manager.add_tool(app_instance.list_messages)
# tool_manager.add_tool(app_instance.get_message)
# tool_manager.add_tool(app_instance.send_email) 
# tool_manager.add_tool(app_instance.create_draft)
# tool_manager.add_tool(app_instance.send_draft)
# tool_manager.add_tool(app_instance.get_draft)
# tool_manager.add_tool(app_instance.get_profile)
# tool_manager.add_tool(app_instance.list_drafts)
# tool_manager.add_tool(app_instance.list_labels)
# tool_manager.add_tool(app_instance.create_label)
tool_manager.add_tool(app_instance.get_subreddit_posts)
tool_manager.add_tool(app_instance.search_subreddits)

async def main():
    # Get a specific tool by name
    # tool = tool_manager.get_tool("list_messages")
    # tool = tool_manager.get_tool("get_message")
    # tool=tool_manager.get_tool("send_email")
    # tool=tool_manager.get_tool("create_draft")
    # tool=tool_manager.get_tool("send_draft")    
    # tool=tool_manager.get_tool("get_draft")
    # tool=tool_manager.get_tool("get_profile")
    # tool=tool_manager.get_tool("list_drafts")
    # tool=tool_manager.get_tool("list_labels")
    # tool=tool_manager.get_tool("create_label")
    tool=tool_manager.get_tool("get_subreddit_posts")
    tool=tool_manager.get_tool("search_subreddits")
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
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="get_message", arguments={"message_id": "1983231f80877805"})
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": " Email", "body": " test email"})
    # result = await tool_manager.call_tool(name="create_draft", arguments={"to": "rishabh@agentr.dev", "subject": " Draft Email", "body": " test email"})
    # result = await tool_manager.call_tool(name="send_draft", arguments={"draft_id": "r354126479467734631"})
    # result = await tool_manager.call_tool(name="get_draft", arguments={"draft_id": "r5764319286899776116"})
    # result = await tool_manager.call_tool(name="get_profile",arguments={})
    # result = await tool_manager.call_tool(name="list_drafts", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="list_labels",arguments={})
    # result = await tool_manager.call_tool(name="create_label",arguments={"name": "test_label"})
    # result = await tool_manager.call_tool(name="get_subreddit_posts", arguments={"subreddit": "python", "limit": 5, "timeframe": "day"})
    result = await tool_manager.call_tool(name="search_subreddits", arguments={"query": "python", "limit": 5, "sort": "relevance"})
    print(result)

if __name__ == "__main__":
    anyio.run(main)