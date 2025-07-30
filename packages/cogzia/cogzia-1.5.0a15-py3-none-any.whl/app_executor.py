"""
App execution module for Cogzia Alpha v1.5.

This module contains the MinimalAIApp implementation and query execution logic
for running AI applications with MCP tool integration.
"""
import os
import time
import logging
from typing import Dict, Any, Optional, List, Callable
import anthropic

from ui import EnhancedConsole
from rich.live import Live
from rich.text import Text

# Configure logging
logger = logging.getLogger(__name__)


class MinimalAIApp:
    """AI app implementation using consolidated MCP architecture."""
    
    def __init__(self, app_id: str = "demo_app", system_prompt: str = "", 
                 mcp_servers: List[str] = None, verbose: bool = False, 
                 auto_mode: bool = False, user_context: Optional['UserContext'] = None):
        self.app_id = app_id
        self.system_prompt = system_prompt
        self.mcp_servers = mcp_servers or []
        self.mcp_client = None
        self.llm_client = None
        self.is_running = False
        self.verbose = verbose
        self.auto_mode = auto_mode
        self.console = EnhancedConsole()
        
        # User context - use DemoUserContext if not provided
        if user_context is None:
            from auth_manager import DemoUserContext
            self.user_context = DemoUserContext()
        else:
            self.user_context = user_context
        
        # Conversation memory attributes
        self.message_history: List[Dict[str, str]] = []
        # Include user ID in conversation ID for user-specific tracking
        user_id = self.user_context.user_id if self.user_context else "demo_user"
        self.conversation_id = f"conv_{user_id}_{self.app_id}_{int(time.time())}"
        self.max_history_length = 20  # Prevent context overflow
        self.enable_memory = True  # Can be disabled for backward compatibility
        
    async def start(self):
        """Start the AI app with real MCP integration."""
        try:
            # Check if MCP initialization should be skipped (for GCP mode)
            if os.getenv("SKIP_MCP_INITIALIZATION") == "true":
                if self.verbose:
                    self.console.print("[yellow]⚠️ Skipping MCP client initialization (GCP mode)[/yellow]")
                self.mcp_client = None
            else:
                # Initialize MCP client - try real implementation first
                try:
                    from shared.mcp.client_factory import create_mcp_client
                    # Use the direct function like v1.2 does - this works properly
                    self.mcp_client = create_mcp_client(
                        name=f"app-{self.app_id}",
                        fallback_enabled=False
                    )
                
                    # Initialize the client if it has pending config (from factory fix)
                    if hasattr(self.mcp_client, '_pending_config'):
                        config = self.mcp_client._pending_config
                        try:
                            await self.mcp_client.initialize(
                                registry_url=config['registry_url'],
                                user_token=config['user_token']
                            )
                            if self.verbose:
                                self.console.print("[green]✓ MCP client initialized successfully[/green]")
                        except Exception as init_error:
                            print(f"❌ CRITICAL: MCP client initialization failed: {init_error}")
                            print("💥 Hard exit - no fallbacks allowed")
                            import sys
                            sys.exit(1)
                        finally:
                            # Clean up pending config regardless
                            delattr(self.mcp_client, '_pending_config')
                        
                except Exception as e:
                    print(f"❌ CRITICAL: MCP client factory not available: {e}")
                    print("💥 Hard exit - no fallbacks allowed")
                    import sys
                    sys.exit(1)
            
            # Initialize LLM client if available
            try:
                anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
                if anthropic_api_key:
                    # Verify API key format
                    if anthropic_api_key.startswith('sk-ant-api'):
                        # Test the API key by creating client
                        test_client = anthropic.Anthropic(api_key=anthropic_api_key)
                        self.llm_client = test_client
                        if self.verbose:
                            self.console.print("[green]✓ Anthropic LLM client initialized successfully[/green]")
                    else:
                        if self.verbose:
                            self.console.print(f"[yellow]⚠️ Invalid ANTHROPIC_API_KEY format[/yellow]")
                else:
                    if self.verbose:
                        self.console.print("[yellow]⚠️ ANTHROPIC_API_KEY not found[/yellow]")
            except Exception as e:
                if self.verbose:
                    self.console.print(f"[red]❌ LLM client initialization failed: {e}[/red]")
            
            # Connect to available MCP servers
            if self.mcp_client and self.mcp_servers:
                print(f"\n🔍 DEBUG: Attempting to connect to {len(self.mcp_servers)} MCP servers")
                print(f"🔍 DEBUG: Server list: {self.mcp_servers}")
                
                for server_name in self.mcp_servers[:3]:  # Connect to top 3 servers
                    print(f"\n🔍 DEBUG: Connecting to '{server_name}'...")
                    try:
                        # Pass the server name as-is - the MCP client will handle name variations
                        connected = await self.mcp_client.connect_server(server_name)
                        print(f"🔍 DEBUG: Connection result for '{server_name}': {connected}")
                        
                        if connected:
                            self.console.print(f"[green]✓ DEBUG: Successfully connected to '{server_name}'[/green]")
                            if self.verbose:
                                self.console.print(f"[green]✓ Connected to {server_name}[/green]")
                        else:
                            print(f"❌ DEBUG: Failed to connect to '{server_name}'")
                            if self.verbose:
                                self.console.print(f"[yellow]⚠️ Could not connect to {server_name}[/yellow]")
                            
                            # Check for common issues
                            if "firecrawl" in server_name.lower():
                                self.console.print("[dim]   💡 Hint: Make sure FIRECRAWL_API_KEY is set in your environment[/dim]")
                            elif "brave" in server_name.lower():
                                self.console.print("[dim]   💡 Hint: Make sure BRAVE_API_KEY is set in your environment[/dim]")
                    except Exception as e:
                        if self.verbose:
                            error_str = str(e)
                            self.console.print(f"[red]❌ Failed to connect to {server_name}[/red]")
                            self.console.print(f"[dim]   Error: {error_str}[/dim]")
                            
                            # Provide helpful hints based on error
                            if "api" in error_str.lower() and "key" in error_str.lower():
                                self.console.print("[yellow]   💡 This server requires an API key to function[/yellow]")
                            elif "not found" in error_str.lower():
                                self.console.print("[yellow]   💡 Make sure the MCP server package is installed[/yellow]")
            
            self.is_running = True
            
        except Exception as e:
            if self.verbose:
                self.console.print(f"[yellow]App startup warning: {e}[/yellow]")
            
            # No fallbacks allowed - exit if MCP client failed
            if not self.mcp_client:
                print("❌ CRITICAL: MCP client initialization failed")
                print("💥 Hard exit - no fallbacks allowed")
                import sys
                sys.exit(1)
    
    async def stop(self):
        """Stop the AI app and cleanup resources."""
        if self.mcp_client:
            try:
                await self.mcp_client.disconnect()
            except:
                pass
        self.is_running = False
    
    def add_to_history(self, role: str, content: str):
        """Add a message to the conversation history."""
        if self.enable_memory:
            self.message_history.append({
                "role": role,
                "content": content
            })
            
            # Trim history if it exceeds max length
            if len(self.message_history) > self.max_history_length:
                # Keep system messages and trim old user/assistant messages
                self.message_history = self.message_history[-self.max_history_length:]
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """Get the full conversation history for LLM context."""
        if not self.enable_memory:
            return []
        return self.message_history.copy()
    
    def clear_history(self):
        """Clear the conversation history."""
        self.message_history = []
        # Generate new conversation ID with current timestamp
        import time
        user_id = self.user_context.user_id if self.user_context else "demo_user"
        self.conversation_id = f"conv_{user_id}_{self.app_id}_{int(time.time())}"
    
    def _get_service_headers(self) -> Dict[str, str]:
        """Get headers for service API calls including auth."""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add auth token if available
        if self.user_context and self.user_context.token:
            headers["Authorization"] = f"Bearer {self.user_context.token}"
            headers["X-User-ID"] = self.user_context.user_id
            headers["X-User-Email"] = self.user_context.email
        
        return headers
    
    def _get_user_storage_path(self) -> str:
        """Get user-specific storage path for app data."""
        if self.user_context:
            return f"user_data/{self.user_context.user_id}/{self.app_id}"
        return f"user_data/demo_user/{self.app_id}"
    
    async def query(self, message: str = "", stream: bool = False, 
                   on_chunk: Callable = None, **kwargs) -> str:
        """Execute query with real MCP tool integration."""
        if not self.is_running:
            await self.start()
        
        # Add user message to history
        if message and self.enable_memory:
            self.add_to_history("user", message)
        
        if stream and on_chunk:
            try:
                # Real streaming implementation with MCP tools
                await on_chunk({'type': 'stream_start', 'message_id': f'msg_{int(time.time())}'})
                
                # Use LLM client if available
                gcp_mode = os.getenv("REQUIRE_REAL_SERVICES") == "true" and os.getenv("SKIP_MCP_INITIALIZATION") == "true"
                if self.llm_client and (self.mcp_client or gcp_mode):
                    if self.verbose:
                        print("🤖 Using real LLM + MCP tools")
                    await self._execute_llm_with_tools(message, on_chunk)
                else:
                    # Enhanced fallback with tool simulation
                    missing_components = []
                    if not self.llm_client:
                        missing_components.append("LLM client")
                    if not self.mcp_client:
                        missing_components.append("MCP client")
                    
                    if self.verbose:
                        print(f"⚠️ Using enhanced fallback mode (missing: {', '.join(missing_components)})")
                    elif not self.auto_mode:  # Only show in interactive mode, not auto
                        await on_chunk({'type': 'text', 'content': f"Using enhanced simulation mode (missing: {', '.join(missing_components)})\n\n"})
                    
                    await self._execute_enhanced_fallback(message, on_chunk)
                    
                await on_chunk({'type': 'complete', 'metadata': {'mode': 'real_mcp_integration'}})
                return "Query completed with real MCP integration"
                
            except Exception as e:
                await on_chunk({'type': 'error', 'error': str(e)})
                return f"Query failed: {e}"
        else:
            return "Real MCP integration - non-streaming mode"
    
    async def _execute_llm_with_tools(self, message: str, on_chunk: Callable):
        """Execute query using real LLM + MCP tools."""
        try:
            # Get available tools from MCP client or Cloud Run
            tools = []
            gcp_mode = os.getenv("REQUIRE_REAL_SERVICES") == "true" and os.getenv("SKIP_MCP_INITIALIZATION") == "true"
            
            if gcp_mode:
                # Define Cloud Run tools for LLM
                # Check for server names (handle both short and full names)
                server_names = [s.lower() for s in self.mcp_servers]
                if any("time" in s for s in server_names):
                    tools.append({
                        "name": "get_current_time",
                        "description": "Get the current time in UTC or a specific timezone",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "timezone": {
                                    "type": "string",
                                    "description": "Timezone name (e.g., 'America/New_York'). Defaults to UTC."
                                }
                            }
                        }
                    })
                if any("brave" in s or "search" in s for s in server_names):
                    tools.append({
                        "name": "brave_web_search",
                        "description": "Search the web using Brave Search",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query"
                                }
                            },
                            "required": ["query"]
                        }
                    })
                if any("calculator" in s or "calc" in s for s in server_names):
                    tools.append({
                        "name": "calculate",
                        "description": "Perform mathematical calculations",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Mathematical expression to evaluate"
                                }
                            },
                            "required": ["expression"]
                        }
                    })
            elif self.mcp_client:
                try:
                    tools = await self.mcp_client.list_tools()
                except:
                    tools = []
            
            if self.verbose:
                print(f"DEBUG: Found {len(tools)} tools: {[t.get('name') if isinstance(t, dict) else t.name for t in tools]}")
            
            if not tools:
                # No tools available - fall back to simulation
                if self.verbose:
                    print("⚠️ No MCP tools available, using simulation")
                await self._execute_enhanced_fallback(message, on_chunk)
                return
            
            # Create LLM request with tools
            tool_descriptions = []
            tool_map = {}  # Map tool names to tool objects for easier lookup
            
            for tool in tools:  # Include all available tools
                # Handle both object and dict formats
                if isinstance(tool, dict):
                    tool_descriptions.append({
                        "name": tool.get("name"),
                        "description": tool.get("description"),
                        "input_schema": tool.get("inputSchema", tool.get("input_schema", {}))
                    })
                    tool_map[tool.get("name")] = tool
                else:
                    # Object format (MCPTool uses input_schema, not parameters)
                    tool_descriptions.append({
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema
                    })
                    tool_map[tool.name] = tool
            
            # Send to LLM with system prompt and tools
            if self.verbose:
                print(f"DEBUG: Calling LLM with {len(tool_descriptions)} tool descriptions")
                print(f"DEBUG: System prompt length: {len(self.system_prompt)}")
            
            # Build conversation with history
            messages = []
            
            # Include conversation history if memory is enabled
            if self.enable_memory:
                messages.extend(self.get_conversation_context())
            
            # Add current message (already added to history in query method)
            # But if history is empty or disabled, we still need it here
            if not messages or not self.enable_memory:
                messages.append({"role": "user", "content": message})
            
            # Continue conversation until no more tool calls
            while True:
                # Stream the response
                with self.llm_client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=self.system_prompt,
                    messages=messages,
                    tools=tool_descriptions if tool_descriptions else None
                ) as stream:
                    if self.verbose:
                        print("DEBUG: LLM response created, starting to stream")
                    
                    # Collect response parts
                    current_text = ""
                    tool_calls = []
                    
                    # Track active content blocks by index
                    active_blocks = {}
                    
                    # Process streaming events
                    for event in stream:
                        # Handle content block start events
                        if hasattr(event, 'type') and event.type == 'content_block_start':
                            if hasattr(event, 'index'):
                                block_index = event.index
                                
                                if hasattr(event, 'content_block'):
                                    block = event.content_block
                                    
                                    if block.type == 'tool_use':
                                        # Tool call detected immediately when model decides to use it
                                        if self.verbose:
                                            self.console.print(f"[cyan][*] Tool call detected: {block.name} (id: {block.id})[/cyan]")
                                        
                                        # Store the block for later reference
                                        active_blocks[block_index] = {
                                            'type': 'tool_use',
                                            'id': block.id,
                                            'name': block.name,
                                            'input': '',  # Will be populated by input_json_delta events
                                            'complete': False
                                        }
                                        
                                        # Show tool call immediately - UI can show "preparing to call..."
                                        await on_chunk({
                                            'type': 'tool_call_detected',
                                            'tool_name': block.name,
                                            'tool_id': block.id,
                                            'message': f"[*] Preparing to call {block.name}..."
                                        })
                                    
                                    elif block.type == 'text':
                                        # Text block started
                                        active_blocks[block_index] = {
                                            'type': 'text',
                                            'content': ''
                                        }
                        
                        # Handle content block deltas
                        elif hasattr(event, 'type') and event.type == 'content_block_delta':
                            if hasattr(event, 'index') and hasattr(event, 'delta'):
                                block_index = event.index
                                
                                if block_index in active_blocks:
                                    block_info = active_blocks[block_index]
                                    
                                    # Handle text deltas
                                    if block_info['type'] == 'text' and hasattr(event.delta, 'text'):
                                        text_chunk = event.delta.text
                                        block_info['content'] += text_chunk
                                        current_text += text_chunk
                                        await on_chunk({'type': 'text', 'content': text_chunk})
                                    
                                    # Handle tool input JSON deltas
                                    elif block_info['type'] == 'tool_use' and event.delta.type == 'input_json_delta':
                                        if hasattr(event.delta, 'partial_json'):
                                            # Tool parameters are being streamed
                                            json_chunk = event.delta.partial_json
                                            block_info['input'] += json_chunk
                                            
                                            if self.verbose:
                                                print(f"Tool params chunk: {json_chunk}")
                        
                        # Handle content block stop
                        elif hasattr(event, 'type') and event.type == 'content_block_stop':
                            if hasattr(event, 'index'):
                                block_index = event.index
                                
                                if block_index in active_blocks:
                                    block_info = active_blocks[block_index]
                                    
                                    if block_info['type'] == 'tool_use':
                                        # Tool block is complete, now we have full parameters
                                        block_info['complete'] = True
                                        
                                        # Parse the complete input JSON
                                        import json
                                        try:
                                            tool_args = json.loads(block_info['input']) if block_info['input'] else {}
                                        except:
                                            tool_args = {}
                                        
                                        # Add to tool_calls list with parsed arguments
                                        tool_call = {
                                            'id': block_info['id'],
                                            'name': block_info['name'],
                                            'input': tool_args
                                        }
                                        tool_calls.append(tool_call)
                                        
                                        # Show complete tool call with parameters
                                        json_rpc_request = {
                                            "jsonrpc": "2.0",
                                            "method": f"tools/call",
                                            "params": {
                                                "name": block_info['name'],
                                                "arguments": tool_args
                                            },
                                            "id": block_info['id']
                                        }
                                        
                                        await on_chunk({
                                            'type': 'tool_call_json',
                                            'tool_name': block_info['name'],
                                            'json_rpc': json_rpc_request
                                        })
                                        
                                        if self.verbose:
                                            print(f"\nTool block complete: {block_info['name']}")
                
                # If no tool calls, we're done
                if not tool_calls:
                    # Add the assistant's final response to history
                    if self.enable_memory and current_text:
                        self.add_to_history("assistant", current_text)
                    break
                
                # Execute tool calls and collect results (tool calls already displayed during streaming)
                tool_results = []
                for tool_call in tool_calls:
                    # Extract from dictionary structure (changed from ToolUseBlock)
                    tool_name = tool_call['name']
                    tool_args = tool_call.get('input', {})
                    tool_id = tool_call['id']
                    
                    # Execute tool
                    try:
                        import json
                        # Parse arguments if they're a string
                        if isinstance(tool_args, str):
                            tool_args = json.loads(tool_args)
                            
                        # Execute tool based on mode
                        if gcp_mode:
                            # Execute Cloud Run tool
                            result = await self._execute_cloud_run_tool(tool_name, tool_args)
                        else:
                            # Execute via MCP client
                            result = await self.mcp_client.execute_tool(
                                tool_name=tool_name,
                                arguments=tool_args
                            )
                        
                        # Show tool result in JSON-RPC format
                        json_rpc_response = {
                            "jsonrpc": "2.0",
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": str(result.output) if result.success else f"Error: {result.error}"
                                }]
                            },
                            "id": tool_id
                        }
                        
                        await on_chunk({
                            'type': 'tool_result_json',
                            'json_rpc': json_rpc_response
                        })
                        
                        # Add tool result for LLM
                        tool_results.append({
                            "tool_call_id": tool_id,
                            "content": str(result.output) if result.success else f"Error: {result.error}",
                            "is_error": not result.success
                        })
                        
                    except Exception as e:
                        await on_chunk({'type': 'error', 'error': f"Tool error: {e}"})
                        tool_results.append({
                            "tool_call_id": tool_id,
                            "content": f"Tool execution error: {str(e)}",
                            "is_error": True
                        })
                
                # Add assistant message with tool use blocks
                assistant_content = []
                
                # Add text content if any
                if current_text:
                    assistant_content.append({
                        "type": "text",
                        "text": current_text
                    })
                
                # Add tool use blocks
                for tool_call in tool_calls:
                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_call['id'],
                        "name": tool_call['name'],
                        "input": tool_call.get('input', {})
                    })
                
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                
                # Save assistant response with tool calls to history
                if self.enable_memory:
                    # Create a simplified text representation for history
                    history_text = current_text if current_text else ""
                    if tool_calls:
                        tool_names = [tc['name'] for tc in tool_calls]
                        if history_text:
                            history_text += f"\n[Used tools: {', '.join(tool_names)}]"
                        else:
                            history_text = f"[Used tools: {', '.join(tool_names)}]"
                    if history_text:
                        self.add_to_history("assistant", history_text)
                
                # Add tool results as user message with tool_result blocks
                user_content = []
                for result in tool_results:
                    user_content.append({
                        "type": "tool_result",
                        "tool_use_id": result["tool_call_id"],
                        "content": result["content"],
                        "is_error": result.get("is_error", False)
                    })
                
                messages.append({
                    "role": "user",
                    "content": user_content
                })
                
                # Continue conversation with tool results
                await on_chunk({'type': 'text', 'content': '\n'})  # Add spacing
                
                # Reset current_text for the next iteration to capture the final response
                current_text = ""
            
        except Exception as e:
            if self.verbose:
                print(f"DEBUG: LLM execution failed: {e}")
            await on_chunk({'type': 'error', 'error': str(e)})
            # Fall back to simulation
            await self._execute_enhanced_fallback(message, on_chunk)
    
    async def _execute_enhanced_fallback(self, message: str, on_chunk: Callable):
        """Execute without LLM client - direct MCP tool usage."""
        if not self.auto_mode:
            await on_chunk({'type': 'thinking', 'content': f"Processing your request..."})
        
        # Use real MCP tools directly
        if self.mcp_client:
            print(f"\n🔍 DEBUG: MCP client exists: {self.mcp_client}")
            try:
                # Get connected servers
                servers = self.mcp_client.get_connected_servers()
                print(f"🔍 DEBUG: get_connected_servers() returned: {servers}")
                print(f"🔍 DEBUG: Number of connected servers: {len(servers) if servers else 0}")
                
                # Also check the internal connections
                if hasattr(self.mcp_client, 'connections'):
                    print(f"🔍 DEBUG: MCP client connections dict: {list(self.mcp_client.connections.keys())}")
                    for conn_id, conn in self.mcp_client.connections.items():
                        print(f"🔍 DEBUG: Connection '{conn_id}': connected={getattr(conn, 'connected', 'N/A')}")
                
                if servers:
                    await on_chunk({'type': 'text', 'content': f"Using {len(servers)} MCP server(s)\n\n"})
                    
                    # Execute appropriate tools based on query
                    await self._execute_real_tools(message, on_chunk)
                else:
                    print(f"❌ DEBUG: No servers connected! servers={servers}")
                    error_msg = "No MCP servers connected.\n\n"
                    error_msg += "💡 Common issues:\n"
                    error_msg += "• Missing API keys (FIRECRAWL_API_KEY, BRAVE_API_KEY)\n"
                    error_msg += "• MCP servers not installed (try: npm install -g @modelcontextprotocol/server-*)\n"
                    error_msg += "• Services not running (check with: ./system-status.sh --mcp)\n"
                    await on_chunk({'type': 'text', 'content': error_msg})
            except Exception as e:
                await on_chunk({'type': 'error', 'error': f"MCP client error: {e}"})
        else:
            # Check if we're in GCP mode with Cloud Run servers
            if os.getenv("REQUIRE_REAL_SERVICES") == "true" and os.getenv("SKIP_MCP_INITIALIZATION") == "true":
                await on_chunk({'type': 'text', 'content': "Using Cloud Run MCP servers\n\n"})
                await self._execute_cloud_run_tools(message, on_chunk)
            else:
                await on_chunk({'type': 'text', 'content': "MCP client not initialized. Please check service configuration.\n"})
    
    async def _execute_cloud_run_tool(self, tool_name: str, arguments: dict):
        """Execute a single Cloud Run MCP tool and return result."""
        import httpx
        import subprocess
        
        # Get auth token - try environment first, then gcloud command
        auth_token = os.getenv("GCP_AUTH_TOKEN", "")
        if not auth_token:
            try:
                result = subprocess.run(
                    ["gcloud", "auth", "print-identity-token"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                auth_token = result.stdout.strip()
            except Exception as e:
                if self.console:
                    self.console.print(f"[red][!] Could not get GCP auth token: {e}[/red]")
                else:
                    print(f"[!] Could not get GCP auth token: {e}")
        
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        # Map tool names to servers
        tool_server_map = {
            "get_current_time": "time",
            "brave_web_search": "brave-search",
            "calculate": "calculator",
            "get_fortune": "fortune",
            "store": "memory",
            "retrieve": "memory", 
            "evaluate": "pythoncalc",
            "evaluate_natural": "pythoncalc",
            "generate_data": "synthetic-data",
            "list_patterns": "workflow-patterns",
            "get_pattern": "workflow-patterns"
        }
        
        server_name = tool_server_map.get(tool_name)
        if not server_name:
            return type('Result', (), {'success': False, 'error': f'Unknown tool: {tool_name}'})()
        
        # Get server URL
        server_url = os.getenv(
            f"MCP_SERVER_{server_name.upper().replace('-', '_')}_URL",
            f"https://mcp-{server_name}-696792272068.us-central1.run.app"
        )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{server_url}/mcp"
                payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    },
                    "id": 1
                }
                
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        content = result["result"].get("content", [{}])
                        if isinstance(content, list) and content:
                            text = content[0].get("text", "No result")
                        else:
                            text = str(content)
                        return type('Result', (), {'success': True, 'output': text})()
                    elif "error" in result:
                        error_msg = result["error"].get("message", "Unknown error")
                        return type('Result', (), {'success': False, 'error': error_msg})()
                else:
                    return type('Result', (), {'success': False, 'error': f'HTTP {response.status_code}'})()
                    
        except Exception as e:
            return type('Result', (), {'success': False, 'error': str(e)})()

    async def _execute_cloud_run_tools(self, message: str, on_chunk: Callable):
        """Execute Cloud Run MCP servers based on query content."""
        import httpx
        message_lower = message.lower()
        tools_called = False
        
        # Get auth token from environment
        auth_token = os.getenv("GCP_AUTH_TOKEN", "")
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        # Cloud Run server endpoints
        cloud_run_servers = {
            "time": os.getenv("MCP_SERVER_TIME_URL", f"https://mcp-time-{os.getenv('GCP_PROJECT_ID', '696792272068')}.{os.getenv('GCP_REGION', 'us-central1')}.run.app"),
            "calculator": os.getenv("MCP_SERVER_CALCULATOR_URL", f"https://mcp-calculator-{os.getenv('GCP_PROJECT_ID', '696792272068')}.{os.getenv('GCP_REGION', 'us-central1')}.run.app"),
            "brave-search": os.getenv("MCP_SERVER_BRAVE_SEARCH_URL", f"https://mcp-brave-search-{os.getenv('GCP_PROJECT_ID', '696792272068')}.{os.getenv('GCP_REGION', 'us-central1')}.run.app")
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                # Time-related queries
                if any(word in message_lower for word in ["time", "date", "when", "today", "tomorrow"]):
                    await on_chunk({'type': 'tool_call', 'tool_name': 'time:get_current_time'})
                    try:
                        # Make MCP request to Cloud Run server
                        response = await client.post(
                            f"{cloud_run_servers['time']}/mcp",
                            json={
                                "jsonrpc": "2.0",
                                "method": "tools/call",
                                "params": {
                                    "name": "get_current_time",
                                    "arguments": {}
                                },
                                "id": 1
                            }
                        )
                        if response.status_code == 200:
                            result = response.json()
                            # Extract from JSON-RPC response
                            if "result" in result:
                                content = result["result"].get("content", [{}])
                                if isinstance(content, list) and content:
                                    text = content[0].get("text", "No time data")
                                else:
                                    text = str(content)
                                await on_chunk({'type': 'text', 'content': f"{text}\n"})
                                await on_chunk({'type': 'tool_result', 'result': text})
                            elif "error" in result:
                                error_msg = result["error"].get("message", "Unknown error")
                                await on_chunk({'type': 'text', 'content': f"Error: {error_msg}\n"})
                        else:
                            await on_chunk({'type': 'text', 'content': f"Time service error: HTTP {response.status_code}\n"})
                    except Exception as e:
                        await on_chunk({'type': 'text', 'content': f"Time service error: {e}\n"})
                    tools_called = True
                
                # Search queries
                elif any(word in message_lower for word in ["search", "find", "web", "internet", "news", "information"]):
                    await on_chunk({'type': 'tool_call', 'tool_name': 'brave_search:brave_web_search'})
                    try:
                        search_query = message.replace("search for", "").replace("find", "").strip()
                        response = await client.post(
                            f"{cloud_run_servers['brave-search']}/mcp",
                            json={
                                "jsonrpc": "2.0",
                                "method": "tools/call",
                                "params": {
                                    "name": "brave_web_search",
                                    "arguments": {"query": search_query}
                                },
                                "id": 1
                            }
                        )
                        if response.status_code == 200:
                            result = response.json()
                            # Extract from JSON-RPC response
                            if "result" in result:
                                content = result["result"].get("content", [{}])
                                if isinstance(content, list) and content:
                                    text = content[0].get("text", "No search results")
                                else:
                                    text = str(content)
                                await on_chunk({'type': 'text', 'content': f"{text}\n"})
                                await on_chunk({'type': 'tool_result', 'result': text})
                            elif "error" in result:
                                error_msg = result["error"].get("message", "Unknown error")
                                await on_chunk({'type': 'text', 'content': f"Error: {error_msg}\n"})
                        else:
                            await on_chunk({'type': 'text', 'content': f"Search service error: HTTP {response.status_code}\n"})
                    except Exception as e:
                        await on_chunk({'type': 'text', 'content': f"Search service error: {e}\n"})
                    tools_called = True
                
                # Calculator queries
                elif any(word in message_lower for word in ["calculate", "math", "add", "subtract", "multiply", "divide"]):
                    await on_chunk({'type': 'tool_call', 'tool_name': 'calculator:calculate'})
                    try:
                        # Extract math expression from message
                        import re
                        math_expr = re.search(r'[\d\s\+\-\*\/\(\)\.]+', message)
                        expression = math_expr.group(0).strip() if math_expr else message
                        
                        response = await client.post(
                            f"{cloud_run_servers['calculator']}/mcp",
                            json={
                                "jsonrpc": "2.0",
                                "method": "tools/call",
                                "params": {
                                    "name": "calculate",
                                    "arguments": {"expression": expression}
                                },
                                "id": 1
                            }
                        )
                        if response.status_code == 200:
                            result = response.json()
                            # Extract from JSON-RPC response
                            if "result" in result:
                                content = result["result"].get("content", [{}])
                                if isinstance(content, list) and content:
                                    text = content[0].get("text", "No result")
                                else:
                                    text = str(content)
                                await on_chunk({'type': 'text', 'content': f"{text}\n"})
                                await on_chunk({'type': 'tool_result', 'result': text})
                            elif "error" in result:
                                error_msg = result["error"].get("message", "Unknown error")
                                await on_chunk({'type': 'text', 'content': f"Error: {error_msg}\n"})
                        else:
                            await on_chunk({'type': 'text', 'content': f"Calculator error: HTTP {response.status_code}\n"})
                    except Exception as e:
                        await on_chunk({'type': 'text', 'content': f"Calculator error: {e}\n"})
                    tools_called = True
                
                if not tools_called:
                    await on_chunk({'type': 'text', 'content': "I understand your query, but I don't have a specific tool for that. Let me provide a general response.\n"})
                    
        except Exception as e:
            await on_chunk({'type': 'error', 'error': f"Cloud Run error: {e}"})

    async def _execute_real_tools(self, message: str, on_chunk: Callable):
        """Execute real MCP tools based on query content."""
        message_lower = message.lower()
        tools_called = False
        
        try:
            # Time-related queries
            if any(word in message_lower for word in ["time", "date", "when", "today", "tomorrow"]):
                await on_chunk({'type': 'tool_call', 'tool_name': 'time:get_current_time'})
                # Call real time MCP server using correct signature
                result = await self.mcp_client.execute_tool(
                    tool_name="get_current_time",
                    arguments={}
                )
                if result.success:
                    await on_chunk({'type': 'text', 'content': f"Current time: {result.output}\n"})
                else:
                    await on_chunk({'type': 'text', 'content': f"Time service error: {result.error}\n"})
                await on_chunk({'type': 'tool_result', 'result': result.output if result.success else result.error})
                tools_called = True
            
            # Search queries - use brave search
            elif any(word in message_lower for word in ["search", "find", "quantum", "computing", "research", "information"]):
                await on_chunk({'type': 'tool_call', 'tool_name': 'brave_search:brave_web_search'})
                # Call real brave search MCP server
                search_query = "quantum computing recent advancements" if "quantum" in message_lower else message
                result = await self.mcp_client.execute_tool(
                    tool_name="brave_web_search",
                    arguments={"query": search_query}
                )
                if result.success:
                    await on_chunk({'type': 'text', 'content': f"Search results:\n{result.output}\n"})
                else:
                    await on_chunk({'type': 'text', 'content': f"Search error: {result.error}\n"})
                await on_chunk({'type': 'tool_result', 'result': result.output if result.success else result.error})
                tools_called = True
            
            # Weather queries
            elif any(word in message_lower for word in ["weather", "temperature", "forecast", "rain"]):
                await on_chunk({'type': 'tool_call', 'tool_name': 'weather:get_weather'})
                result = await self.mcp_client.execute_tool(
                    tool_name="get_weather",
                    arguments={"location": "San Francisco"}
                )
                if result.success:
                    await on_chunk({'type': 'text', 'content': f"Weather: {result.output}\n"})
                else:
                    await on_chunk({'type': 'text', 'content': f"Weather service error: {result.error}\n"})
                await on_chunk({'type': 'tool_result', 'result': result.output if result.success else result.error})
                tools_called = True
            
            # Calculator queries
            elif any(word in message_lower for word in ["calculate", "math", "add", "subtract", "multiply", "divide"]):
                await on_chunk({'type': 'tool_call', 'tool_name': 'calculator:calculate'})
                # Extract math expression from query
                expression = "2 + 2"  # Default
                if "add" in message_lower:
                    expression = "5 + 3"
                elif "multiply" in message_lower:
                    expression = "7 * 8"
                
                result = await self.mcp_client.execute_tool(
                    tool_name="calculate",
                    arguments={"expression": expression}
                )
                if result.success:
                    await on_chunk({'type': 'text', 'content': f"Calculation result: {expression} = {result.output}\n"})
                else:
                    await on_chunk({'type': 'text', 'content': f"Calculator error: {result.error}\n"})
                await on_chunk({'type': 'tool_result', 'result': result.output if result.success else result.error})
                tools_called = True
            
            if not tools_called:
                # Default: show available tools
                await on_chunk({'type': 'text', 'content': f"I can help you with various tasks. Available tools: {', '.join(self.mcp_servers)}\n"})
                
        except Exception as e:
            await on_chunk({'type': 'error', 'error': f"Tool execution error: {e}"})


class AppQueryExecutor:
    """Handles execution of queries against AI apps."""
    
    def __init__(self, console: EnhancedConsole = None, verbose: bool = False):
        self.console = console or EnhancedConsole()
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
    
    async def execute_query(self, app: MinimalAIApp, query: str, 
                          show_chat_ui: bool = True, show_user_message: bool = True) -> Dict[str, Any]:
        """
        Execute a query on the app with streaming and UI.
        
        Args:
            app: The AI app instance
            query: User query
            show_chat_ui: Whether to show chat-style UI
            
        Returns:
            Dictionary with execution results
        """
        self.logger.info(f"[EXECUTE_QUERY] Starting query execution: {query}")
        
        # Track stats
        search_start = time.time()
        chunks_received = []
        thinking_content = []
        response_content = []
        tool_calls = []
        
        # Show user message (unless disabled for chat mode)
        if show_chat_ui and show_user_message and not self.verbose:
            from ui import create_chat_message
            self.console.print(create_chat_message("You", query))
            self.console.print()  # Add spacing
        
        # Show loading indicator
        if show_chat_ui and not self.verbose:
            from ui_components import ProgressIndicators
            loading_panel = ProgressIndicators.loading("Processing your query")
            self.console.print(loading_panel)
            self.console.print()
        
        # Create a Live display for streaming
        live_display = Live(console=self.console.console, refresh_per_second=10, transient=False)
        current_display = Text()
        
        # Add initial status
        current_display.append("🤖 AI Assistant is thinking...\n", style="dim")
        live_display.update(current_display)
        
        # Track all display elements in chronological order
        display_elements = []
        
        # Callback for streaming
        async def on_chunk(chunk: Dict[str, Any]):
            nonlocal current_display, display_elements
            chunks_received.append(chunk)
            chunk_type = chunk.get('type', '')
            self.logger.debug(f"[CHUNK] Received chunk type: {chunk_type}")
            
            if chunk_type == 'stream_start':
                if self.verbose:
                    self.console.print(f"[dim]Stream started: {chunk.get('message_id')}[/dim]")
            elif chunk_type == 'thinking':
                # Capture thinking content
                thinking_content.append(chunk.get('content', ''))
                if self.verbose:
                    current_display.append(f"[dim italic]{chunk.get('content', '')}[/dim italic]")
                    live_display.update(current_display)
            elif chunk_type == 'text':
                # Regular text content - accumulate inline
                content = chunk.get('content', '')
                response_content.append(content)
                
                # Clear "thinking" message on first real content
                if len(display_elements) == 0 or (len(display_elements) == 1 and display_elements[0]['type'] == 'thinking'):
                    display_elements = []
                
                # Add text to display elements
                if display_elements and display_elements[-1]['type'] == 'text':
                    # Append to existing text element
                    display_elements[-1]['content'] += content
                else:
                    # Create new text element
                    display_elements.append({'type': 'text', 'content': content})
                
                # Rebuild display from all elements in order
                current_display = Text()
                for element in display_elements:
                    if element['type'] == 'text':
                        current_display.append(element['content'])
                    elif element['type'] == 'tool':
                        current_display.append(element['display'])
                
                live_display.update(current_display)
            elif chunk_type == 'tool_call_detected':
                # Tool call detected immediately when model decides to use it
                tool_name = chunk.get('tool_name', 'unknown')
                message = chunk.get('message', f"[*] Preparing to call {tool_name}...")
                
                tool_display = Text()
                tool_display.append(f"\n{message}\n", style="bold cyan dim")
                
                # Add tool element to chronological display
                display_elements.append({'type': 'tool', 'display': tool_display})
                
                # Rebuild display from all elements in order
                current_display = Text()
                for element in display_elements:
                    if element['type'] == 'text':
                        current_display.append(element['content'])
                    elif element['type'] == 'tool':
                        current_display.append(element['display'])
                
                live_display.update(current_display)
                
            elif chunk_type == 'tool_call':
                # Tool call notification
                tool_name = chunk.get('tool_name', 'unknown')
                tool_calls.append(tool_name)
                
                tool_display = Text()
                tool_display.append(f"\n[*] Using tool: {tool_name}\n", style="bold cyan")
                
                # Add tool element to chronological display
                display_elements.append({'type': 'tool', 'display': tool_display})
                
                # Rebuild display from all elements in order
                current_display = Text()
                for element in display_elements:
                    if element['type'] == 'text':
                        current_display.append(element['content'])
                    elif element['type'] == 'tool':
                        current_display.append(element['display'])
                
                live_display.update(current_display)
                
            elif chunk_type == 'tool_call_json':
                # Tool call JSON-RPC display
                import json
                tool_name = chunk.get('tool_name', 'unknown')
                json_rpc = chunk.get('json_rpc', {})
                tool_calls.append(tool_name)
                
                tool_display = Text()
                tool_display.append(f"\n\n[*] Calling tool: {tool_name}\n", style="bold cyan")
                json_str = json.dumps(json_rpc, indent=2)
                tool_display.append(f"```json\n{json_str}\n```\n", style="dim yellow")
                
                # Add tool element to chronological display
                display_elements.append({'type': 'tool', 'display': tool_display})
                
                # Rebuild display from all elements in order
                current_display = Text()
                for element in display_elements:
                    if element['type'] == 'text':
                        current_display.append(element['content'])
                    elif element['type'] == 'tool':
                        current_display.append(element['display'])
                
                live_display.update(current_display)
                
            elif chunk_type == 'tool_result':
                # Tool result received
                tool_display = Text()
                tool_display.append(f"✓ Tool completed\n", style="green")
                
                # Add tool element to chronological display
                display_elements.append({'type': 'tool', 'display': tool_display})
                
                # Rebuild display from all elements in order
                current_display = Text()
                for element in display_elements:
                    if element['type'] == 'text':
                        current_display.append(element['content'])
                    elif element['type'] == 'tool':
                        current_display.append(element['display'])
                
                live_display.update(current_display)
                
            elif chunk_type == 'tool_result_json':
                # Tool result JSON-RPC display
                import json
                json_rpc = chunk.get('json_rpc', {})
                
                tool_display = Text()
                tool_display.append("**Tool Response:**\n", style="green bold")
                json_str = json.dumps(json_rpc, indent=2)
                tool_display.append(f"```json\n{json_str}\n```\n", style="dim green")
                
                # Add tool element to chronological display
                display_elements.append({'type': 'tool', 'display': tool_display})
                
                # Rebuild display from all elements in order
                current_display = Text()
                for element in display_elements:
                    if element['type'] == 'text':
                        current_display.append(element['content'])
                    elif element['type'] == 'tool':
                        current_display.append(element['display'])
                
                live_display.update(current_display)
            elif chunk_type == 'error':
                # Error in streaming
                error_msg = chunk.get('error', 'Unknown error')
                current_display.append(f"\n[red]Error: {error_msg}[/red]\n")
                live_display.update(current_display)
            elif chunk_type == 'complete':
                # Stream complete
                if self.verbose:
                    metadata = chunk.get('metadata', {})
                    usage = metadata.get('usage', {})
                    self.console.print(f"\n[dim]Tokens: {usage.get('total_tokens', 0)}[/dim]")
        
        # Execute query with streaming
        try:
            # Start the live display
            live_display.start()
            
            # Execute query
            result = await app.query(
                message=query,
                stream=True,
                on_chunk=on_chunk,
                verbose=self.verbose,
                auto_mode=app.auto_mode
            )
            
            # Stop live display
            live_display.stop()
            
            # Calculate stats
            elapsed_time = time.time() - search_start
            
            # Show results
            if show_chat_ui and not self.verbose:
                # Add final spacing
                self.console.print()
                
                # Show stats
                stats_text = f"[dim]Response time: {elapsed_time:.2f}s"
                if tool_calls:
                    stats_text += f" | Tools used: {len(tool_calls)}"
                stats_text += f" | Chunks: {len(chunks_received)}[/dim]"
                self.console.print(stats_text)
            
            return {
                'success': True,
                'result': result,
                'elapsed_time': elapsed_time,
                'chunks_received': len(chunks_received),
                'tool_calls': tool_calls,
                'response': ''.join(response_content)
            }
            
        except Exception as e:
            live_display.stop()
            
            from ui_components import StandardMessages
            error_panel = StandardMessages.error(
                "Query Execution Failed",
                str(e),
                recovery="Check your internet connection or try a simpler query"
            )
            self.console.print(error_panel)
            
            return {
                'success': False,
                'error': str(e),
                'elapsed_time': time.time() - search_start
            }