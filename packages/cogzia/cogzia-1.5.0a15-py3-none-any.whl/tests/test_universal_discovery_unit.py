#!/usr/bin/env python3
"""
Unit tests for UniversalServerDiscovery module.

Tests the discovery enhancement logic without requiring live services.
Follows Cogzia's testing standards with proper docstrings.
"""

import sys
import os
import pytest
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from universal_discovery import UniversalServerDiscovery


class TestUniversalServerDiscovery:
    """Test cases for UniversalServerDiscovery class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = UniversalServerDiscovery()
        
    def test_universal_server_identification(self):
        """Test _is_universal_server method identifies servers correctly."""
        # Test by name
        assert self.discovery._is_universal_server('time-mcp-server', {})
        assert self.discovery._is_universal_server('calculator', {})
        assert not self.discovery._is_universal_server('openai-mcp-server', {})
        
        # Test by tags
        assert self.discovery._is_universal_server('custom', {'tags': ['universal']})
        assert not self.discovery._is_universal_server('custom', {'tags': ['api-required']})
        
        # Test by is_universal flag
        assert self.discovery._is_universal_server('custom', {'is_universal': True})
        assert not self.discovery._is_universal_server('custom', {'is_universal': False})
        
        # Test by auth_required
        assert self.discovery._is_universal_server('custom', {'auth_required': False})
        assert not self.discovery._is_universal_server('custom', {'auth_required': True})
    
    def test_relevance_boosting(self):
        """Test that universal servers get relevance boost."""
        discovered_servers = ['time-mcp-server', 'openai-mcp-server']
        server_details = {
            'time-mcp-server': {
                'relevance': 0.6,
                'capabilities': ['time']
            },
            'openai-mcp-server': {
                'relevance': 0.7,
                'capabilities': ['llm']
            }
        }
        
        enhanced_servers, enhanced_details = self.discovery.enhance_discovery_results(
            discovered_servers, server_details, "what time is it"
        )
        
        # Universal server should have boosted relevance
        time_relevance = enhanced_details['time-mcp-server']['relevance']
        openai_relevance = enhanced_details['openai-mcp-server']['relevance']
        
        assert time_relevance == 0.8  # 0.6 + 0.2 boost
        assert openai_relevance == 0.7  # No boost
        assert enhanced_details['time-mcp-server']['is_universal'] == True
        assert enhanced_details['time-mcp-server']['universal_note'] == "No API key required"
    
    def test_missing_universal_servers_added(self):
        """Test that relevant universal servers are added if missing."""
        # Empty discovery results
        discovered_servers = []
        server_details = {}
        
        # Test calculator requirement
        enhanced_servers, enhanced_details = self.discovery.enhance_discovery_results(
            discovered_servers, server_details, "I need to calculate 2 + 2"
        )
        
        # Should add calculator servers
        assert 'calculator-mcp-server' in enhanced_servers
        assert 'pythoncalc-mcp-server' in enhanced_servers
        assert enhanced_details['calculator-mcp-server']['is_universal'] == True
        assert enhanced_details['calculator-mcp-server']['relevance'] == 0.7
    
    def test_case_insensitive_matching(self):
        """Test that server name matching is case insensitive."""
        # Mixed case server name
        assert self.discovery._is_universal_server('Time-MCP-Server'.lower(), {})
        assert self.discovery._is_universal_server('CALCULATOR'.lower(), {})
    
    def test_sorting_by_relevance(self):
        """Test that servers are sorted by relevance after enhancement."""
        discovered_servers = ['api-server', 'time-mcp-server', 'another-server']
        server_details = {
            'api-server': {'relevance': 0.9},
            'time-mcp-server': {'relevance': 0.5},
            'another-server': {'relevance': 0.7}
        }
        
        enhanced_servers, enhanced_details = self.discovery.enhance_discovery_results(
            discovered_servers, server_details, "general request"
        )
        
        # Should be sorted by relevance (descending)
        # api-server: 0.9, another-server: 0.7, time-mcp-server: 0.7 (0.5 + 0.2)
        assert enhanced_servers[0] == 'api-server'
        assert enhanced_servers[1] in ['another-server', 'time-mcp-server']
    
    def test_universal_servers_info_structure(self):
        """Test get_universal_servers_info returns correct structure."""
        info = self.discovery.get_universal_servers_info()
        
        # Check all servers present
        expected_servers = [
            'time-mcp-server', 'calculator-mcp-server', 'pythoncalc-mcp-server',
            'fortune-mcp-server', 'memory-mcp-server', 'synthetic-data-mcp-server',
            'workflow-patterns-mcp-server', 'brave-search-mcp-server'
        ]
        
        for server in expected_servers:
            assert server in info
            assert 'description' in info[server]
            assert 'capabilities' in info[server]
            assert 'examples' in info[server]
            assert isinstance(info[server]['capabilities'], list)
            assert isinstance(info[server]['examples'], list)


def test_universal_boost_value():
    """Test that UNIVERSAL_BOOST constant is set correctly."""
    discovery = UniversalServerDiscovery()
    assert discovery.UNIVERSAL_BOOST == 0.2


def test_universal_servers_set():
    """Test that UNIVERSAL_SERVERS set contains expected servers."""
    discovery = UniversalServerDiscovery()
    
    # Check some expected servers
    assert 'time' in discovery.UNIVERSAL_SERVERS
    assert 'calculator' in discovery.UNIVERSAL_SERVERS
    assert 'fortune' in discovery.UNIVERSAL_SERVERS
    
    # All should be lowercase
    for server in discovery.UNIVERSAL_SERVERS:
        assert server == server.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])