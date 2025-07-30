"""
Utility functions and classes for Cogzia Alpha v1.5.

This module contains shared utilities including structure detection,
import resolution, prompt generation, and other helper functions.
"""
import os
import asyncio
import random
import string
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime

from config import PROJECT_ROOT


class StructureDetector:
    """Detects and manages new vs old repository structure."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or PROJECT_ROOT
        self.new_structure_path = self.project_root / "_new_structure"
        self.has_new_structure = self.new_structure_path.exists()
        
    def get_microservice_path(self, service_name: str) -> Path:
        """Get path to microservice, preferring new structure."""
        if self.has_new_structure:
            new_path = self.new_structure_path / "microservices" / service_name
            if new_path.exists():
                return new_path
        
        # Fallback to old structure
        old_paths = [
            self.project_root / "services" / service_name,
            self.project_root / service_name,
            self.project_root / "microservices" / service_name
        ]
        
        for path in old_paths:
            if path.exists():
                return path
                
        # Default to new structure path even if doesn't exist
        return self.new_structure_path / "microservices" / service_name
    
    def get_utility_path(self, utility_type: str, utility_name: str) -> Path:
        """Get path to utility, preferring new structure."""
        if self.has_new_structure:
            new_path = self.new_structure_path / "operations" / "utilities" / utility_type / utility_name
            if new_path.exists():
                return new_path
        
        # Fallback to old structure
        old_paths = [
            self.project_root / "scripts" / utility_name,
            self.project_root / "tools" / utility_name,
            self.project_root / "utils" / utility_name
        ]
        
        for path in old_paths:
            if path.exists():
                return path
                
        return self.new_structure_path / "operations" / "utilities" / utility_type / utility_name


def resolve_import(module_path: str, fallback_paths: List[str] = None, 
                  structure_detector: StructureDetector = None):
    """
    Resolve imports with new structure awareness.
    
    Args:
        module_path: The module path to import
        fallback_paths: Alternative paths to try
        structure_detector: StructureDetector instance
        
    Returns:
        Imported module or raises ImportError
    """
    fallback_paths = fallback_paths or []
    detector = structure_detector or StructureDetector()
    
    # Try new structure paths first
    if detector.has_new_structure:
        new_structure_paths = [
            f"_new_structure.{module_path}",
            f"_new_structure.microservices.{module_path}",
            f"_new_structure.operations.{module_path}"
        ]
        for path in new_structure_paths:
            try:
                return __import__(path, fromlist=[''])
            except ImportError:
                continue
    
    # Try original path
    try:
        return __import__(module_path, fromlist=[''])
    except ImportError:
        pass
    
    # Try fallback paths
    for fallback in fallback_paths:
        try:
            return __import__(fallback, fromlist=[''])
        except ImportError:
            continue
    
    # Final fallback - raise the original import error
    return __import__(module_path, fromlist=[''])


class PromptGenerator:
    """Generate system prompts for AI apps."""
    
    def __init__(self, enable_cache: bool = False):
        self.enable_cache = enable_cache
    
    async def generate_system_prompt_stream(self, requirements: str, servers: List[str], 
                                          server_capabilities: Dict[str, Dict] = None, 
                                          template_name: str = "ai_app_system",
                                          on_chunk: Callable = None):
        """
        Generate system prompt with streaming simulation.
        
        Args:
            requirements: User requirements
            servers: List of server names
            server_capabilities: Server capability information
            template_name: Template to use
            on_chunk: Callback for each chunk
            
        Yields:
            Prompt chunks
        """
        try:
            # Try to use real prompt generator from shared utils
            import sys
            from pathlib import Path
            
            # Add parent directory to path so we can import shared modules
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            from shared.utils.prompt_generator import PromptGenerator as RealPromptGenerator
            real_generator = RealPromptGenerator(enable_cache=self.enable_cache)
            async for chunk in real_generator.generate_system_prompt_stream(
                requirements=requirements, 
                servers=servers, 
                server_capabilities=server_capabilities, 
                template_name=template_name, 
                on_chunk=on_chunk
            ):
                yield chunk
        except ImportError:
            # Fallback to local implementation
            # Use simplified prompt generator for GCP deployment (with streaming)
            class LocalPromptGenerator:
                def __init__(self):
                    pass
                
                async def generate_system_prompt_stream(self, requirements, servers, server_capabilities=None, on_chunk=None, template_name=None):
                    """Generate a dynamic system prompt based on requirements and selected servers."""
                    
                    # Extract server information
                    server_names = []
                    server_descriptions = []
                    capabilities_list = []
                    
                    for server in servers:
                        if isinstance(server, dict):
                            name = server.get('name', 'unknown')
                            desc = server.get('description', '')
                            caps = server.get('capabilities', [])
                        else:
                            name = str(server)
                            desc = ''
                            caps = []
                        
                        server_names.append(name)
                        if desc:
                            server_descriptions.append(f"- {name}: {desc}")
                        if caps:
                            capabilities_list.extend(caps)
                    
                    # Remove duplicates from capabilities
                    unique_capabilities = list(set(capabilities_list))
                    
                    # Build dynamic prompt based on what tools are available
                    prompt_parts = [
                        f"You are an AI assistant created to help with: {requirements}",
                        "",
                        "Your capabilities include:"
                    ]
                    
                    # Add specific capabilities based on selected servers
                    if 'brave-search' in ' '.join(server_names).lower() or 'search' in ' '.join(server_names).lower():
                        prompt_parts.extend([
                            "- Search the web for current information",
                            "- Find answers to questions using web search",
                            "- Access up-to-date information from the internet"
                        ])
                    
                    if 'calculator' in ' '.join(server_names).lower() or 'math' in ' '.join(unique_capabilities):
                        prompt_parts.extend([
                            "- Perform mathematical calculations",
                            "- Solve complex equations",
                            "- Handle arithmetic operations"
                        ])
                    
                    if 'time' in ' '.join(server_names).lower():
                        prompt_parts.extend([
                            "- Provide current time in different timezones",
                            "- Convert between timezones",
                            "- Answer time-related questions"
                        ])
                    
                    if 'weather' in ' '.join(server_names).lower():
                        prompt_parts.extend([
                            "- Get current weather information",
                            "- Provide weather forecasts",
                            "- Answer weather-related questions for any location"
                        ])
                    
                    if 'filesystem' in ' '.join(server_names).lower():
                        prompt_parts.extend([
                            "- Manage files and directories",
                            "- Read and write files",
                            "- Navigate filesystem structures"
                        ])
                    
                    if 'workflow' in ' '.join(server_names).lower():
                        prompt_parts.extend([
                            "- Execute complex workflows",
                            "- Automate multi-step processes",
                            "- Coordinate between multiple tools"
                        ])
                    
                    # Add available tools section
                    prompt_parts.extend([
                        "",
                        "Available tools:",
                    ])
                    prompt_parts.extend(server_descriptions if server_descriptions else [f"- {name}" for name in server_names])
                    
                    # Add instructions
                    prompt_parts.extend([
                        "",
                        f"Your primary goal is to: {requirements}",
                        "",
                        "When responding:",
                        "1. Use the available tools to fulfill the user's request",
                        "2. Provide accurate and helpful information",
                        "3. Be clear about what you're doing when using tools",
                        "4. If a tool fails, explain the issue and try alternatives if available"
                    ])
                    
                    # Join the prompt
                    prompt = '\n'.join(prompt_parts)
                    
                    # Yield chunks to simulate streaming with visible speed
                    import asyncio
                    words = prompt.split()
                    for i, word in enumerate(words):
                        chunk = word
                        if i < len(words) - 1:
                            chunk += " "
                        yield chunk
                        if on_chunk:
                            on_chunk(chunk)
                        # Add small delay to make streaming visible
                        await asyncio.sleep(0.05)  # 50ms delay between words for better visibility
            
            local_generator = LocalPromptGenerator()
            async for chunk in local_generator.generate_system_prompt_stream(
                requirements=requirements, 
                servers=servers, 
                server_capabilities=server_capabilities, 
                template_name=template_name, 
                on_chunk=on_chunk
            ):
                yield chunk
    


def generate_app_id() -> str:
    """
    Generate a unique app ID.
    
    Returns:
        App ID in format app_xxxxxxxx
    """
    # Generate 8 random characters (lowercase letters and numbers, excluding confusing ones)
    chars = string.ascii_lowercase + string.digits
    exclude = '01l'  # Exclude confusing characters
    valid_chars = [c for c in chars if c not in exclude]
    
    random_id = ''.join(random.choices(valid_chars, k=8))
    return f"app_{random_id}"


def generate_test_query(requirements: str) -> str:
    """
    Generate a test query based on app requirements.
    
    Args:
        requirements: App requirements string
        
    Returns:
        A contextually relevant test query
    """
    requirements_lower = requirements.lower()
    
    # Generate relevant test queries
    if "time" in requirements_lower or "date" in requirements_lower:
        return "What time is it right now?"
    elif "news" in requirements_lower:
        return "What are today's top technology news?"
    elif "weather" in requirements_lower:
        return "What's the weather forecast for tomorrow?"
    elif "research" in requirements_lower:
        return "Find recent research on artificial intelligence"
    elif "summarize" in requirements_lower:
        return "Summarize the latest developments in climate change"
    elif "coding" in requirements_lower or "development" in requirements_lower:
        return "What are the best practices for Python async programming?"
    elif "search" in requirements_lower or "web" in requirements_lower:
        return "Search for recent advancements in quantum computing"
    else:
        # Generic fallback - use last word of requirements
        last_word = requirements.split()[-1] if requirements else "technology"
        return f"Tell me something interesting about {last_word}"


def format_duration(start_time: datetime) -> str:
    """
    Format duration from start time to now.
    
    Args:
        start_time: Start datetime
        
    Returns:
        Formatted duration string
    """
    duration = datetime.now() - start_time
    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


class AppManifest:
    """Handle app manifest operations."""
    
    @staticmethod
    def create_manifest(app_config: Dict[str, Any], app_id: str, 
                       skeleton_config: Any = None) -> Dict[str, Any]:
        """
        Create an app manifest.
        
        Args:
            app_config: App configuration
            app_id: App ID
            skeleton_config: Optional skeleton configuration
            
        Returns:
            Manifest dictionary
        """
        manifest = {
            "app_id": app_id,
            "created_at": datetime.now().isoformat(),
            "app_name": app_config.get("app_name", "Custom AI App"),
            "requirements": app_config.get("requirements", ""),
            "servers": app_config.get("servers", []),
            "system_prompt": app_config.get("system_prompt", ""),
            "version": "1.5.0"
        }
        
        if skeleton_config:
            manifest["skeleton_config"] = skeleton_config
        
        return manifest
    
    @staticmethod
    def save_manifest(manifest: Dict[str, Any], app_path: Path) -> None:
        """
        Save manifest to disk.
        
        Args:
            manifest: Manifest dictionary
            app_path: Path to save manifest
        """
        import yaml
        
        manifest_path = app_path / "manifest.yaml"
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)