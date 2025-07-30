"""
Enhanced discovery module that prioritizes universal MCP servers.

This module extends the existing discovery to highlight servers that don't require API keys,
making it easier for users to get started with zero configuration.
"""

from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class UniversalServerDiscovery:
    """Enhanced discovery that prioritizes universal servers."""
    
    # Universal servers that don't require API keys (all lowercase for case-insensitive matching)
    UNIVERSAL_SERVERS = {
        'time', 'time-mcp-server',
        'calculator', 'calculator-mcp-server', 
        'fortune', 'fortune-mcp-server',
        'memory', 'memory-mcp-server',
        'pythoncalc', 'pythoncalc-mcp-server',
        'synthetic-data', 'synthetic-data-mcp-server',
        'workflow-patterns', 'workflow-patterns-mcp-server',
        'brave-search', 'brave-search-mcp-server',  # Using mock data
    }
    
    # Relevance boost for universal servers
    UNIVERSAL_BOOST = 0.2  # Add 0.2 to relevance score
    
    def __init__(self):
        pass
    
    def enhance_discovery_results(self, 
                                discovered_servers: List[str],
                                server_details: Dict[str, Dict],
                                requirements: str) -> Tuple[List[str], Dict[str, Dict]]:
        """
        Enhance discovery results by boosting universal servers.
        
        Args:
            discovered_servers: List of discovered server names
            server_details: Dictionary of server details
            requirements: User requirements string
            
        Returns:
            Enhanced (servers, details) with universal server priority
        """
        enhanced_details = {}
        
        # First, boost relevance scores for universal servers
        for server_name, details in server_details.items():
            enhanced_details[server_name] = details.copy()
            
            # Check if this is a universal server
            is_universal = self._is_universal_server(server_name, details)
            
            if is_universal:
                # Boost relevance score
                original_relevance = details.get('relevance', 0.5)
                boosted_relevance = min(1.0, original_relevance + self.UNIVERSAL_BOOST)
                enhanced_details[server_name]['relevance'] = boosted_relevance
                enhanced_details[server_name]['is_universal'] = True
                enhanced_details[server_name]['universal_note'] = "No API key required"
                
                # Update source to indicate boost
                enhanced_details[server_name]['source'] = "Enhanced Discovery (Universal)"
        
        # Sort servers by relevance (universal servers will be higher)
        sorted_servers = sorted(
            discovered_servers,
            key=lambda s: enhanced_details.get(s, {}).get('relevance', 0),
            reverse=True
        )
        
        # Add universal servers that might be relevant but not discovered
        self._add_missing_universal_servers(sorted_servers, enhanced_details, requirements)
        
        return sorted_servers, enhanced_details
    
    def _is_universal_server(self, server_name: str, details: Dict) -> bool:
        """Check if a server is universal (no API key required)."""
        # Check by name
        if server_name.lower() in self.UNIVERSAL_SERVERS:
            return True
        
        # Check by tags
        tags = details.get('tags', [])
        if 'universal' in tags:
            return True
        
        # Check by is_universal flag
        if details.get('is_universal', False):
            return True
        
        # Check by auth_required flag
        if details.get('auth_required', True) == False:
            return True
        
        return False
    
    def _add_missing_universal_servers(self, 
                                     servers: List[str], 
                                     details: Dict[str, Dict],
                                     requirements: str):
        """Add relevant universal servers that weren't discovered."""
        requirements_lower = requirements.lower()
        
        # Check for specific universal server matches
        universal_matches = []
        
        # Time server
        if any(word in requirements_lower for word in ['time', 'date', 'timezone', 'clock']):
            if not any('time' in s for s in servers):
                universal_matches.append(('time-mcp-server', 0.7, 'Get current time and date'))
        
        # Calculator server  
        if any(word in requirements_lower for word in ['math', 'calculate', 'compute', 'arithmetic']):
            if not any('calc' in s for s in servers):
                universal_matches.append(('calculator-mcp-server', 0.7, 'Perform calculations'))
                universal_matches.append(('pythoncalc-mcp-server', 0.8, 'Advanced Python calculator'))
        
        # Fortune server
        if any(word in requirements_lower for word in ['fortune', 'quote', 'motivation', 'fun']):
            if not any('fortune' in s for s in servers):
                universal_matches.append(('fortune-mcp-server', 0.6, 'Get fortune cookie messages'))
        
        # Memory server
        if any(word in requirements_lower for word in ['remember', 'store', 'memory', 'persist']):
            if not any('memory' in s for s in servers):
                universal_matches.append(('memory-mcp-server', 0.7, 'Store data across queries'))
        
        # Synthetic data server
        if any(word in requirements_lower for word in ['test', 'mock', 'data', 'generate', 'synthetic']):
            if not any('synthetic' in s for s in servers):
                universal_matches.append(('synthetic-data-mcp-server', 0.6, 'Generate test data'))
        
        # Add matched universal servers
        for server_name, relevance, description in universal_matches:
            if server_name not in servers:
                servers.append(server_name)
                details[server_name] = {
                    'capabilities': [server_name.split('-')[0]],
                    'description': description,
                    'source': 'Universal Server Match',
                    'relevance': relevance,
                    'is_universal': True,
                    'universal_note': 'No API key required - Ready to use!',
                    'tools': []
                }
    
    def get_universal_servers_info(self) -> Dict[str, Dict]:
        """Get information about all available universal servers."""
        return {
            'time-mcp-server': {
                'description': 'Get current time in various timezones',
                'capabilities': ['time', 'timezone', 'date'],
                'examples': ['What time is it?', 'Show me the time in Tokyo'],
            },
            'calculator-mcp-server': {
                'description': 'Perform basic calculations',
                'capabilities': ['math', 'arithmetic', 'calculate'],
                'examples': ['Calculate 25 * 4', 'What is 100 divided by 3?'],
            },
            'pythoncalc-mcp-server': {
                'description': 'Advanced calculator with Python evaluation',
                'capabilities': ['math', 'scientific', 'python', 'advanced'],
                'examples': ['Calculate sin(45)', 'Solve x^2 + 5x + 6 = 0'],
            },
            'fortune-mcp-server': {
                'description': 'Get fortune cookie messages and quotes',
                'capabilities': ['fortune', 'quotes', 'motivation'],
                'examples': ['Give me a fortune', 'Show me a motivational quote'],
            },
            'memory-mcp-server': {
                'description': 'Store and retrieve data across conversations',
                'capabilities': ['storage', 'memory', 'persistence'],
                'examples': ['Remember that my name is Alice', 'What did I tell you earlier?'],
            },
            'synthetic-data-mcp-server': {
                'description': 'Generate realistic test data',
                'capabilities': ['data', 'testing', 'mock', 'generation'],
                'examples': ['Generate 10 user records', 'Create test order data'],
            },
            'workflow-patterns-mcp-server': {
                'description': 'Discover workflow patterns for automation',
                'capabilities': ['workflow', 'patterns', 'automation'],
                'examples': ['Show me data processing patterns', 'List automation workflows'],
            },
            'brave-search-mcp-server': {
                'description': 'Web search (using mock data in universal mode)',
                'capabilities': ['search', 'web', 'information'],
                'examples': ['Search for Python tutorials', 'Find information about AI'],
            },
        }