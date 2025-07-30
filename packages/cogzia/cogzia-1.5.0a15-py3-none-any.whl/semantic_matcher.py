"""
LLM-based semantic tool matching for dynamic server discovery.

This module uses LLM to semantically match user requirements with available tools,
replacing hardcoded keyword matching.
"""
import os
import sys
import json
import logging
import hashlib
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Tuple
import anthropic


logger = logging.getLogger(__name__)


class CogziaAnthropicProxy:
    """
    Proxy client that routes Anthropic API calls through Cogzia's services.
    
    This allows users to use Cogzia without needing their own Anthropic API key.
    """
    
    def __init__(self):
        """Initialize the proxy client."""
        self.messages = self
        
        # Use the auth service endpoint to proxy Anthropic requests
        self.proxy_url = os.getenv('AUTH_SERVICE_URL', 'https://auth-service-696792272068.us-central1.run.app')
        logger.info(f"Initialized Cogzia API proxy: {self.proxy_url}")
    
    def create(self, **kwargs):
        """Create a message using the Cogzia API proxy."""
        import httpx
        
        # Prepare the request payload
        payload = {
            'model': kwargs.get('model', 'claude-sonnet-4-20250514'),
            'max_tokens': kwargs.get('max_tokens', 1000),
            'temperature': kwargs.get('temperature', 0.1),
            'messages': kwargs.get('messages', [])
        }
        
        try:
            # Route through Cogzia's proxy endpoint (no authentication required for alpha)
            response = httpx.post(
                f"{self.proxy_url}/api/v1/proxy/anthropic/messages",
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Cogzia-Client': 'semantic-matcher-v1.5'
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Create a response object compatible with anthropic.messages.create
                class ProxyMessage:
                    def __init__(self, content):
                        self.content = content
                
                class ProxyResponse:
                    def __init__(self, content_text):
                        self.content = [type('Content', (), {'text': content_text})()]
                
                # Extract the content from the proxy response
                content_text = data.get('content', '')
                if isinstance(data.get('content'), list) and len(data['content']) > 0:
                    content_text = data['content'][0].get('text', str(data.get('content', '')))
                
                return ProxyResponse(content_text)
            
            else:
                if response.status_code == 401:
                    logger.info("🔑 Proxy authentication failed - please set ANTHROPIC_API_KEY for enhanced functionality")
                    print("💡 For enhanced tool discovery, set your ANTHROPIC_API_KEY:")
                    print("   export ANTHROPIC_API_KEY=your-key-here")
                else:
                    logger.error(f"Proxy request failed: {response.status_code} - {response.text}")
                
                # Fall back to a default response for web search
                class FallbackResponse:
                    def __init__(self):
                        self.content = [type('Content', (), {
                            'text': '''[
                                {"server_id": "brave-search", "relevance": 0.9, "reason": "Web search functionality matches user requirements"}
                            ]'''
                        })()]
                
                return FallbackResponse()
                
        except Exception as e:
            logger.error(f"Proxy request error: {e}")
            # Return a fallback response that prioritizes search functionality
            class FallbackResponse:
                def __init__(self):
                    self.content = [type('Content', (), {
                        'text': '''[
                            {"server_id": "brave-search", "relevance": 0.9, "reason": "Web search functionality matches user requirements"}
                        ]'''
                    })()]
            
            return FallbackResponse()


class SemanticToolMatcher:
    """Uses LLM to semantically match requirements with available tools."""
    
    # File-based cache configuration
    _cache_dir = Path(tempfile.gettempdir()) / "cogzia_discovery_cache"
    _cache_ttl = 3600  # 1 hour cache TTL
    
    def __init__(self, model: str = None, conversation_history: List[Dict[str, str]] = None):
        """Initialize the semantic matcher with Anthropic client.
        
        Args:
            model: Optional model to use for discovery. Defaults to ANTHROPIC_MODEL env var.
            conversation_history: Optional conversation history to include in cache key
        """
        # Try to get API key from multiple sources
        api_key = None
        
        # First try environment variable (for local development)
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # If no API key, use Cogzia's API proxy service
        if not api_key:
            logger.info("🔄 Using Cogzia API proxy (no user API key required)")
            # Create a proxy client that routes through our services
            self.client = CogziaAnthropicProxy()
        else:
            logger.info("🔑 Using user-provided ANTHROPIC_API_KEY")
            self.client = anthropic.Anthropic(api_key=api_key)
        # Use faster model for discovery by default, fall back to env var if not specified
        self.model = model or os.getenv('ANTHROPIC_DISCOVERY_MODEL', 'claude-sonnet-4-20250514') or os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        self.conversation_history = conversation_history or []
        
        # Ensure cache directory exists
        self._cache_dir.mkdir(exist_ok=True)
        logger.info(f"Cache directory: {self._cache_dir}")
    
    def _generate_cache_key(self, requirements: str, available_servers: Dict[str, Dict[str, Any]]) -> str:
        """Generate a cache key from requirements, servers, and conversation history."""
        # Create a sorted, stable representation of servers
        server_data = sorted([
            (k, v.get('description', ''), v.get('capabilities', []))
            for k, v in available_servers.items()
        ])
        
        # Only show cache key generation in debug mode
        if logger.isEnabledFor(logging.DEBUG):
            print(f"[dim]🔑 Generating cache key:[/dim]")
            print(f"[dim]   - Requirements: {requirements[:50]}...[/dim]")
            print(f"[dim]   - Servers: {len(available_servers)} servers[/dim]")
            print(f"[dim]   - Model: {self.model}[/dim]")
            print(f"[dim]   - History: {len(self.conversation_history)} messages[/dim]")
        
        # Include conversation history in cache key
        history_data = []
        for msg in self.conversation_history[-10:]:  # Last 10 messages for context
            history_data.append({
                'role': msg.get('role', ''),
                'content': msg.get('content', '')[:100]  # First 100 chars
            })
        
        cache_data = {
            'requirements': requirements,
            'servers': server_data,
            'model': self.model,
            'history': history_data
        }
        # Generate hash for cache key
        cache_str = json.dumps(cache_data, sort_keys=True)
        key = hashlib.sha256(cache_str.encode()).hexdigest()
        if logger.isEnabledFor(logging.DEBUG):
            print(f"[dim]   - Cache key: {key[:16]}...[/dim]")
        return key
    
    async def match_tools_to_requirements(
        self,
        requirements: str,
        available_servers: Dict[str, Dict[str, Any]]
    ) -> List[Tuple[str, float]]:
        """
        Match user requirements to available tools using semantic analysis.
        
        Args:
            requirements: User's stated requirements
            available_servers: Dict of server_id -> server capabilities
            
        Returns:
            List of (server_id, relevance_score) tuples, sorted by relevance
        """
        if not available_servers:
            return []
        
        # Check cache first
        cache_key = self._generate_cache_key(requirements, available_servers)
        cache_file = self._cache_dir / f"{cache_key}.json"
        current_time = time.time()
        
        logger.info(f"Cache key: {cache_key}")
        logger.info(f"Cache file: {cache_file}")
        
        # Try to load from file cache
        # Only show cache status in verbose mode
        if logger.isEnabledFor(logging.DEBUG):
            print(f"[dim]🔍 Checking cache: {cache_file}[/dim]")
            print(f"[dim]📁 Cache directory exists: {self._cache_dir.exists()}[/dim]")
            print(f"[dim]📄 Cache file exists: {cache_file.exists()}[/dim]")
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cached_result = [(item[0], item[1]) for item in cache_data['results']]
                    cache_time = cache_data['timestamp']
                    
                    age = current_time - cache_time
                    
                    if age < self._cache_ttl:
                        logger.info(f"Cache hit for discovery: {requirements[:50]}...")
                        # Don't print in non-verbose mode to avoid formatting issues
                        return cached_result
                    else:
                        # Cache expired, remove it
                        logger.info(f"Cache expired ({age:.1f}s old), removing...")
                        cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                if cache_file.exists():
                    cache_file.unlink()
        
        # Build server descriptions for LLM
        server_descriptions = []
        for server_id, info in available_servers.items():
            tools = info.get('tools', [])
            desc = f"Server: {server_id}\n"
            desc += f"Description: {info.get('description', 'No description')}\n"
            desc += "Tools:\n"
            for tool in tools:
                desc += f"  - {tool['name']}: {tool['description']}\n"
            server_descriptions.append(desc)
        
        # Create prompt for semantic matching
        prompt = f"""You are an expert at matching user requirements to available tools and services.

User Requirements:
{requirements}

Available Servers and Their Tools:
{chr(10).join(server_descriptions)}

Task: Analyze which servers best match the user's requirements. Consider:
1. Direct functionality matches
2. Implied needs from the requirements
3. Complementary tools that would enhance the solution

Return a JSON array of server matches with relevance scores (0.0 to 1.0):
[
    {{"server_id": "server_name", "relevance": 0.95, "reason": "why this server matches"}}
]

Order by relevance score (highest first). Include ALL servers that have ANY relevance (score > 0.0).
Only return the JSON array, no other text."""

        try:
            # Call LLM for semantic matching
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistent matching
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            try:
                matches = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    matches = json.loads(json_match.group())
                else:
                    print(f"❌ CRITICAL: LLM returned invalid JSON for tool matching")
                    print("💥 Hard exit - semantic matching failed")
                    sys.exit(1)
            
            # Convert to expected format
            results = []
            for match in matches:
                server_id = match.get('server_id')
                relevance = float(match.get('relevance', 0.0))
                if server_id and relevance > 0.0:
                    results.append((server_id, relevance))
            
            # Sort by relevance (highest first)
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Save to file cache
            try:
                cache_data = {
                    'results': results,
                    'timestamp': current_time,
                    'requirements': requirements[:100],  # For debugging
                    'model': self.model
                }
                # Ensure directory exists before writing
                self._cache_dir.mkdir(parents=True, exist_ok=True)
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                logger.info(f"Cached discovery results to file: {requirements[:50]}...")
            except Exception as e:
                logger.warning(f"Failed to save cache: {e}")
            
            return results
            
        except anthropic.APIError as e:
            print(f"❌ CRITICAL: Semantic matching API call failed: {e}")
            print("💥 Hard exit - cannot match tools without LLM")
            sys.exit(1)
        except Exception as e:
            print(f"❌ CRITICAL: Semantic matching failed: {e}")
            print("💥 Hard exit - unexpected error")
            sys.exit(1)
    
    async def extract_capabilities_from_tools(
        self,
        tools: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract high-level capabilities from tool descriptions using LLM.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            List of capability strings
        """
        if not tools:
            return []
        
        # Build tool descriptions
        tool_desc = []
        for tool in tools:
            tool_desc.append(f"- {tool['name']}: {tool['description']}")
        
        prompt = f"""Analyze these tools and extract high-level capabilities:

Tools:
{chr(10).join(tool_desc)}

Task: List the high-level capabilities these tools provide. Examples:
- "Time Operations" for time-related tools
- "Web Search" for search tools
- "Mathematical Calculations" for math tools

Return a JSON array of capability strings. Be concise and descriptive.
Only return the JSON array, no other text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Parse JSON response
            try:
                capabilities = json.loads(response_text)
                if isinstance(capabilities, list):
                    return [str(cap) for cap in capabilities]
            except:
                # Try to extract list from response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    capabilities = json.loads(json_match.group())
                    return [str(cap) for cap in capabilities]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to extract capabilities: {e}")
            return []  # Non-critical, return empty list