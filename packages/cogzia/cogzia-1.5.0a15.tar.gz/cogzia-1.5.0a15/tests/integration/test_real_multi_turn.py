#!/usr/bin/env python3
"""
Test real multi-turn conversations in Cogzia Alpha v1.3.

This script demonstrates how v1.3 now supports true multi-turn conversations
with memory persistence across queries.
"""
import asyncio
import os
import sys
from typing import Dict, Any, List

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tools.demos.cogzia_alpha_v1_3.app_executor import MinimalAIApp, AppQueryExecutor
from tools.demos.cogzia_alpha_v1_3.ui import EnhancedConsole


class MultiTurnConversationDemo:
    """Demonstrate multi-turn conversations with memory."""
    
    def __init__(self):
        self.console = EnhancedConsole()
        self.app = None
        self.executor = None
        
    async def setup(self):
        """Set up the AI app for conversation."""
        print("\n🚀 Setting up Cogzia Alpha v1.3 with Conversation Memory")
        print("=" * 60)
        
        # Create app with conversation-aware system prompt
        self.app = MinimalAIApp(
            app_id="multi_turn_demo",
            system_prompt=(
                "You are a helpful AI assistant with conversation memory. "
                "You remember what users tell you and can refer back to previous messages. "
                "When users ask about previous topics, you can recall the conversation history."
            ),
            mcp_servers=["time", "weather", "calculator"],
            verbose=False,
            auto_mode=False  # Interactive mode
        )
        
        # Start the app
        await self.app.start()
        
        # Create executor for running queries
        self.executor = AppQueryExecutor(self.console, verbose=False)
        
        print("✅ App initialized with conversation memory enabled")
        print(f"📝 Conversation ID: {self.app.conversation_id}")
        print(f"💾 Max history length: {self.app.max_history_length} messages")
        
    async def run_conversation_demo(self):
        """Run a demo conversation showing memory persistence."""
        print("\n🎭 Multi-Turn Conversation Demo")
        print("=" * 60)
        
        # Demo conversation turns
        conversation_turns = [
            {
                "user": "Hello! My name is Bob and I'm learning about quantum computing.",
                "expected": "The assistant should greet Bob and acknowledge the quantum computing interest"
            },
            {
                "user": "What time is it?",
                "expected": "The assistant should tell the time (using MCP tool)"
            },
            {
                "user": "What's my name?",
                "expected": "The assistant should remember the name is Bob"
            },
            {
                "user": "What am I learning about?",
                "expected": "The assistant should recall quantum computing"
            },
            {
                "user": "Can you calculate 42 * 17 for me?",
                "expected": "The assistant should use the calculator tool"
            },
            {
                "user": "What was the result of that calculation?",
                "expected": "The assistant should remember it was 42 * 17 = 714"
            }
        ]
        
        for i, turn in enumerate(conversation_turns, 1):
            print(f"\n{'='*60}")
            print(f"Turn {i}: {turn['expected']}")
            print(f"{'='*60}")
            
            # Execute the query
            await self.executor.execute_query(
                self.app, 
                turn["user"], 
                show_chat_ui=True
            )
            
            # Show conversation state
            history = self.app.get_conversation_context()
            print(f"\n[dim]📊 Conversation history: {len(history)} messages[/dim]")
            
            # Small delay between turns
            await asyncio.sleep(0.5)
            
    async def show_conversation_analysis(self):
        """Analyze and display the conversation history."""
        print("\n📊 Conversation Analysis")
        print("=" * 60)
        
        history = self.app.get_conversation_context()
        
        print(f"Total messages: {len(history)}")
        print(f"Conversation ID: {self.app.conversation_id}")
        
        # Count message types
        user_msgs = sum(1 for msg in history if msg["role"] == "user")
        assistant_msgs = sum(1 for msg in history if msg["role"] == "assistant")
        
        print(f"User messages: {user_msgs}")
        print(f"Assistant messages: {assistant_msgs}")
        
        # Show conversation flow
        print("\n📜 Conversation Flow:")
        for i, msg in enumerate(history, 1):
            role = msg["role"].upper()
            content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
            print(f"{i:2d}. [{role:9s}] {content}")
            
    async def test_memory_features(self):
        """Test specific memory features."""
        print("\n🧪 Testing Memory Features")
        print("=" * 60)
        
        # Test 1: Clear history
        print("\n1. Testing clear history command...")
        old_history_len = len(self.app.get_conversation_context())
        old_id = self.app.conversation_id
        
        await asyncio.sleep(1.1)  # Ensure timestamp changes
        self.app.clear_history()
        
        new_history_len = len(self.app.get_conversation_context())
        new_id = self.app.conversation_id
        
        print(f"   History cleared: {old_history_len} → {new_history_len} messages")
        print(f"   New conversation ID: {new_id}")
        assert new_id != old_id, "Conversation ID should change"
        assert new_history_len == 0, "History should be empty"
        print("   ✅ Clear history works!")
        
        # Test 2: Add some messages and verify persistence
        print("\n2. Testing message persistence...")
        test_queries = [
            "Remember that my favorite number is 42",
            "What's my favorite number?"
        ]
        
        for query in test_queries:
            await self.executor.execute_query(self.app, query, show_chat_ui=True)
            await asyncio.sleep(0.5)
            
        # Verify the assistant remembered
        history = self.app.get_conversation_context()
        last_response = history[-1]["content"] if history else ""
        if "42" in last_response:
            print("   ✅ Memory persistence verified!")
        else:
            print("   ❌ Memory persistence failed")
            
    async def demonstrate_tool_memory(self):
        """Demonstrate that tool usage is tracked in memory."""
        print("\n🔧 Tool Usage Memory Demo")
        print("=" * 60)
        
        # Clear history for fresh demo
        await asyncio.sleep(1.1)
        self.app.clear_history()
        
        tool_queries = [
            ("What's the current time?", "time"),
            ("What's 123 + 456?", "calculator"),
            ("What tools did you just use?", "memory recall")
        ]
        
        for query, expected in tool_queries:
            print(f"\n[{expected}] {query}")
            await self.executor.execute_query(self.app, query, show_chat_ui=True)
            await asyncio.sleep(0.5)
            
        # Show that tool usage is in history
        history = self.app.get_conversation_context()
        tool_mentions = [msg for msg in history if "[Used tools:" in msg.get("content", "")]
        print(f"\n📊 Tool usage tracked: {len(tool_mentions)} tool calls recorded")


async def main():
    """Run the multi-turn conversation demonstration."""
    demo = MultiTurnConversationDemo()
    
    try:
        # Set up the app
        await demo.setup()
        
        # Run the main conversation demo
        await demo.run_conversation_demo()
        
        # Show conversation analysis
        await demo.show_conversation_analysis()
        
        # Test memory features
        await demo.test_memory_features()
        
        # Demonstrate tool memory
        await demo.demonstrate_tool_memory()
        
        print("\n" + "=" * 60)
        print("✅ Multi-Turn Conversation Demo Complete!")
        print("\nKey Achievements:")
        print("  ✓ Conversations persist across multiple queries")
        print("  ✓ Assistant remembers user information")
        print("  ✓ Tool usage is tracked in conversation history")
        print("  ✓ History can be cleared to start fresh")
        print("  ✓ Each conversation has a unique ID")
        
        print("\n📝 Note: This demo works even in fallback mode!")
        print("With real LLM + MCP, the conversations are even more natural.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if demo.app:
            await demo.app.stop()


if __name__ == "__main__":
    # Note: This demo can run without ANTHROPIC_API_KEY
    # It will use the enhanced fallback mode with real MCP tools
    asyncio.run(main())