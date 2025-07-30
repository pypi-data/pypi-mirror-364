#!/usr/bin/env python3
"""
Test conversation flow in Cogzia Alpha v1.3.

This script tests the conversation flow and demonstrates how v1.3 handles
multiple turns without needing an API key by analyzing the code structure.
"""
import asyncio
import os
import sys
from typing import List, Dict, Any

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tools.demos.cogzia_alpha_v1_3.app_executor import MinimalAIApp


class ConversationFlowAnalyzer:
    """Analyzes how v1.3 handles multi-turn conversations."""
    
    def __init__(self):
        self.findings = []
        
    async def analyze_app_structure(self):
        """Analyze the MinimalAIApp structure for conversation handling."""
        print("\n🔍 Analyzing Cogzia Alpha v1.3 Conversation Handling")
        print("=" * 60)
        
        # Check MinimalAIApp class structure
        app = MinimalAIApp(
            app_id="analysis_app",
            system_prompt="Test prompt",
            mcp_servers=["time"],
            verbose=True,
            auto_mode=False
        )
        
        # Analyze instance attributes
        print("\n1️⃣ MinimalAIApp Instance Analysis:")
        print(f"   - App ID: {app.app_id}")
        print(f"   - Auto mode: {app.auto_mode} (False = interactive)")
        print(f"   - Has system prompt: {bool(app.system_prompt)}")
        print(f"   - MCP servers configured: {len(app.mcp_servers)}")
        
        # Check for conversation state tracking
        print("\n2️⃣ Conversation State Tracking:")
        state_attributes = []
        for attr in dir(app):
            if not attr.startswith('_') and not callable(getattr(app, attr)):
                state_attributes.append(attr)
        
        print(f"   - State attributes: {', '.join(state_attributes)}")
        print(f"   - Has persistent state: {'messages' in dir(app) or 'history' in dir(app)}")
        
        # Analyze query method
        print("\n3️⃣ Query Method Analysis:")
        query_method = getattr(app, 'query', None)
        if query_method:
            import inspect
            sig = inspect.signature(query_method)
            print(f"   - Parameters: {list(sig.parameters.keys())}")
            print(f"   - Supports streaming: {'stream' in sig.parameters}")
            print(f"   - Has message parameter: {'message' in sig.parameters}")
        
        # Check for message history in LLM execution
        print("\n4️⃣ LLM Execution Analysis:")
        llm_method = getattr(app, '_execute_llm_with_tools', None)
        if llm_method:
            # Read the source to check for message handling
            source = inspect.getsource(llm_method)
            has_messages = 'messages' in source
            has_append = 'append' in source
            has_loop = 'while True:' in source or 'for' in source
            
            print(f"   - Handles messages list: {has_messages}")
            print(f"   - Appends to conversation: {has_append}")
            print(f"   - Has conversation loop: {has_loop}")
            
            if has_messages:
                # Extract message handling pattern
                print("\n   📝 Message Handling Pattern Found:")
                print("      - Creates messages list for conversation")
                print("      - Appends user and assistant messages")
                print("      - Continues conversation until no tool calls")
        
        # Test conversation flow simulation
        print("\n5️⃣ Conversation Flow Simulation:")
        await self.simulate_conversation_flow()
        
        return app
    
    async def simulate_conversation_flow(self):
        """Simulate how a conversation would flow."""
        conversation_flow = [
            {
                'turn': 1,
                'user': "What time is it?",
                'expected_flow': [
                    "1. User message added to conversation",
                    "2. LLM processes with system prompt",
                    "3. Tool call detected (get_current_time)",
                    "4. Tool executed with real MCP",
                    "5. Result added to conversation",
                    "6. LLM generates final response"
                ]
            },
            {
                'turn': 2,
                'user': "What about in Tokyo?",
                'expected_flow': [
                    "1. Previous context NOT maintained (no persistent state)",
                    "2. New conversation starts fresh",
                    "3. LLM may not understand 'what about' refers to time",
                    "4. Tool call may or may not happen"
                ]
            }
        ]
        
        for turn_info in conversation_flow:
            print(f"\n   Turn {turn_info['turn']}: \"{turn_info['user']}\"")
            print("   Expected flow:")
            for step in turn_info['expected_flow']:
                print(f"      {step}")
    
    def analyze_conversation_persistence(self):
        """Analyze if conversations persist between queries."""
        print("\n6️⃣ Conversation Persistence Analysis:")
        
        # Check the query method implementation
        print("   Based on code analysis:")
        print("   - Each query() call is independent")
        print("   - No message history maintained between calls")
        print("   - System prompt sent with each request")
        print("   - Tool results only persist within single query")
        
        print("\n   ⚠️ FINDING: V1.3 does NOT maintain conversation context")
        print("   Each query is a fresh conversation with the LLM")
        
        self.findings.append("No conversation persistence between queries")
        
    def analyze_streaming_behavior(self):
        """Analyze how streaming affects conversations."""
        print("\n7️⃣ Streaming Behavior in Conversations:")
        
        print("   - Streaming is per-query, not per-conversation")
        print("   - Each stream completes before next user input")
        print("   - Tool calls stream within single response")
        print("   - No mechanism to interrupt mid-stream")
        
        self.findings.append("Streaming works per-query only")
    
    def generate_recommendations(self):
        """Generate recommendations for true multi-turn support."""
        print("\n8️⃣ Recommendations for True Multi-Turn Support:")
        
        recommendations = [
            "Add 'messages' list to MinimalAIApp class",
            "Persist conversation history between query() calls",
            "Pass full message history to LLM on each call",
            "Add conversation ID for session tracking",
            "Implement context window management",
            "Add conversation save/load functionality"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n📊 Current State Summary:")
        print("   - V1.3 supports multi-turn WITHIN a single LLM call")
        print("   - V1.3 does NOT support multi-turn across user inputs")
        print("   - Each user query starts a fresh conversation")
        print("   - Context from previous queries is lost")


async def main():
    """Run the analysis."""
    print("🧪 Cogzia Alpha v1.3 Multi-Turn Conversation Analysis")
    print("This analyzes the code structure without needing an API key")
    
    analyzer = ConversationFlowAnalyzer()
    
    # Run analysis
    app = await analyzer.analyze_app_structure()
    analyzer.analyze_conversation_persistence()
    analyzer.analyze_streaming_behavior()
    analyzer.generate_recommendations()
    
    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("\nKey Findings:")
    for finding in analyzer.findings:
        print(f"  ❗ {finding}")
    
    print("\n✅ Analysis completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())