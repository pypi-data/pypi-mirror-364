"""
Tests for the utils module.
"""
import unittest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from tools.demos.cogzia_alpha_v1_3.utils import (
    StructureDetector, generate_app_id, generate_test_query,
    format_duration, AppManifest, PromptGenerator
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_generate_app_id(self):
        """Test app ID generation."""
        # Generate multiple IDs
        ids = [generate_app_id() for _ in range(10)]
        
        # Check format
        for app_id in ids:
            self.assertTrue(app_id.startswith("app_"))
            self.assertEqual(len(app_id), 12)  # "app_" + 8 chars
            
            # Check no confusing characters
            id_part = app_id[4:]
            self.assertNotIn('0', id_part)
            self.assertNotIn('1', id_part)
            self.assertNotIn('l', id_part)
        
        # Check uniqueness
        self.assertEqual(len(ids), len(set(ids)))
    
    def test_generate_test_query(self):
        """Test test query generation."""
        # Test various requirement patterns
        test_cases = [
            ("I need an app that tells time", "What time is it right now?"),
            ("I want to track news", "What are today's top technology news?"),
            ("weather forecast application", "What's the weather forecast for tomorrow?"),
            ("research assistant", "Find recent research on artificial intelligence"),
            ("summarize documents", "Summarize the latest developments in climate change"),
            ("coding helper", "What are the best practices for Python async programming?"),
            ("web search tool", "Search for recent advancements in quantum computing"),
            ("random requirements", "Tell me something interesting about requirements")
        ]
        
        for requirements, expected in test_cases:
            query = generate_test_query(requirements)
            self.assertIsInstance(query, str)
            self.assertTrue(len(query) > 0)
            
            # For specific patterns, check exact match
            if requirements.lower() in ["i need an app that tells time"]:
                self.assertEqual(query, expected)
    
    def test_format_duration(self):
        """Test duration formatting."""
        now = datetime.now()
        
        # Test seconds
        start = now - timedelta(seconds=45)
        self.assertEqual(format_duration(start), "45s")
        
        # Test minutes
        start = now - timedelta(minutes=2, seconds=30)
        self.assertEqual(format_duration(start), "2m 30s")
        
        # Test hours
        start = now - timedelta(hours=1, minutes=30)
        self.assertEqual(format_duration(start), "1h 30m")
    
    def test_structure_detector(self):
        """Test StructureDetector functionality."""
        detector = StructureDetector()
        
        # Test initialization
        self.assertIsInstance(detector.project_root, Path)
        self.assertIsInstance(detector.has_new_structure, bool)
        
        # Test microservice path resolution
        path = detector.get_microservice_path("test_service")
        self.assertIsInstance(path, Path)
        
        # Test utility path resolution
        path = detector.get_utility_path("scripts", "test_script.py")
        self.assertIsInstance(path, Path)
    
    def test_app_manifest(self):
        """Test AppManifest operations."""
        # Test manifest creation
        app_config = {
            "app_name": "Test App",
            "requirements": "Test requirements",
            "servers": ["server1", "server2"],
            "system_prompt": "Test prompt"
        }
        
        manifest = AppManifest.create_manifest(app_config, "app_test1234")
        
        # Verify manifest structure
        self.assertEqual(manifest["app_id"], "app_test1234")
        self.assertEqual(manifest["app_name"], "Test App")
        self.assertEqual(manifest["requirements"], "Test requirements")
        self.assertEqual(manifest["servers"], ["server1", "server2"])
        self.assertEqual(manifest["system_prompt"], "Test prompt")
        self.assertEqual(manifest["version"], "1.3.0")
        self.assertIn("created_at", manifest)


class TestPromptGenerator(unittest.TestCase):
    """Test PromptGenerator async functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = PromptGenerator()
    
    def test_generate_fallback_prompt(self):
        """Test fallback prompt generation."""
        requirements = "search the web"
        servers = ["web-search", "time-tool"]
        
        prompt = self.generator.generate_fallback_prompt(requirements, servers)
        
        self.assertIn(requirements, prompt)
        self.assertIn("web-search", prompt)
        self.assertIn("time-tool", prompt)
    
    def test_async_prompt_generation(self):
        """Test async prompt generation with streaming."""
        async def run_test():
            requirements = "analyze data"
            servers = ["data-analyzer"]
            chunks = []
            
            async def on_chunk(chunk):
                chunks.append(chunk)
            
            full_prompt = ""
            async for chunk in self.generator.generate_system_prompt_stream(
                requirements, servers, on_chunk=on_chunk
            ):
                full_prompt += chunk
            
            # Verify we got chunks
            self.assertTrue(len(chunks) > 0)
            
            # Verify full prompt contains requirements
            self.assertIn(requirements, full_prompt)
            
            return full_prompt
        
        # Run async test
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()