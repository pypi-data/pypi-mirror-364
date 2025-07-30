"""
Tests for the config module.
"""
import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cogzia.config import (
    DebugLevel, DemoStep, validate_environment_variables,
    SERVICE_DESCRIPTIONS, DEFAULT_APP_CONFIG
)


class TestConfig(unittest.TestCase):
    """Test configuration settings and constants."""
    
    def test_debug_levels(self):
        """Test DebugLevel enum values."""
        self.assertEqual(DebugLevel.NONE.value, "none")
        self.assertEqual(DebugLevel.RUN.value, "run")
        self.assertEqual(DebugLevel.WALK.value, "walk")
        self.assertEqual(DebugLevel.CRAWL.value, "crawl")
    
    def test_demo_step_creation(self):
        """Test DemoStep namedtuple creation."""
        step = DemoStep("Test Step", "Test Description", lambda: None)
        self.assertEqual(step.name, "Test Step")
        self.assertEqual(step.description, "Test Description")
        self.assertIsNotNone(step.func)
    
    def test_service_descriptions(self):
        """Test SERVICE_DESCRIPTIONS structure."""
        self.assertIn("MCP Registry", SERVICE_DESCRIPTIONS)
        self.assertIn("Host Registry", SERVICE_DESCRIPTIONS)
        
        # Check MCP Registry configuration
        mcp_config = SERVICE_DESCRIPTIONS["MCP Registry"]
        self.assertIn("port", mcp_config)
        self.assertIn("purpose", mcp_config)
        self.assertIn("check_url", mcp_config)
        self.assertIn("required", mcp_config)
    
    def test_default_app_config(self):
        """Test DEFAULT_APP_CONFIG structure."""
        self.assertIn("app_name", DEFAULT_APP_CONFIG)
        self.assertIn("requirements", DEFAULT_APP_CONFIG)
        self.assertIn("servers", DEFAULT_APP_CONFIG)
        self.assertIn("system_prompt", DEFAULT_APP_CONFIG)
        
        # Check default values
        self.assertEqual(DEFAULT_APP_CONFIG["app_name"], "Custom AI App")
        self.assertEqual(DEFAULT_APP_CONFIG["requirements"], "")
        self.assertIsInstance(DEFAULT_APP_CONFIG["servers"], list)
    
    def test_validate_environment_variables(self):
        """Test environment variable validation."""
        # Test with verbose=False (should return dict)
        result = validate_environment_variables(verbose=False)
        self.assertIsInstance(result, dict)
        self.assertIn("ready_for_production", result)
        self.assertIn("anthropic_api_key", result)
        self.assertIn("mongodb_uri", result)
        self.assertIn("jwt_secret", result)


if __name__ == "__main__":
    unittest.main()