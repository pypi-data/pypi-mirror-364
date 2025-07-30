#!/usr/bin/env python3
"""
Test script for multi-turn conversations in Cogzia Alpha v1.3.

This script tests the v1.3 system with multiple user messages in a single
conversation session, ensuring context is maintained and tools work correctly
across turns.
"""
import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tools.demos.cogzia_alpha_v1_3.main import (
    validate_environment, 
    show_available_servers,
    get_app_requirements,
    find_matching_servers,
    generate_system_prompt,
    create_ai_app,
    query_app
)
from tools.demos.cogzia_alpha_v1_3.app_executor import MinimalAIApp, AppQueryExecutor
from tools.demos.cogzia_alpha_v1_3.ui import EnhancedConsole
from tools.demos.cogzia_alpha_v1_3.config import validate_environment_variables


class ConversationTestRunner:
    """Runs multi-turn conversation tests with real services."""
    
    def __init__(self):
        self.console = EnhancedConsole()
        self.executor = AppQueryExecutor(console=self.console, verbose=False)
        
    async def run_conversation_test(self, 
                                  app_requirements: str,
                                  conversation_turns: List[str],
                                  test_name: str = "Multi-turn Test") -> Dict[str, Any]:
        """
        Run a multi-turn conversation test.
        
        Args:
            app_requirements: Requirements for the AI app
            conversation_turns: List of user messages to send
            test_name: Name of the test
            
        Returns:
            Test results with timing and response data
        """
        self.console.print(f"\n[bold cyan]═══ {test_name} ═══[/bold cyan]")
        self.console.print(f"Requirements: {app_requirements}")
        self.console.print(f"Turns: {len(conversation_turns)}")
        self.console.print()
        
        results = {
            'test_name': test_name,
            'requirements': app_requirements,
            'turns': [],
            'total_time': 0,
            'tools_used': set(),
            'success': True
        }
        
        try:
            # Step 1: Create the app
            self.console.print("[dim]Creating AI app...[/dim]")
            
            # Find matching servers
            servers, _ = await find_matching_servers(app_requirements)
            if not servers:
                self.console.print("[red]No matching servers found![/red]")
                results['success'] = False
                return results
            
            # Generate system prompt
            system_prompt = await generate_system_prompt(app_requirements, servers)
            
            # Create the app
            app = MinimalAIApp(
                app_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_prompt=system_prompt,
                mcp_servers=servers,
                verbose=False,
                auto_mode=False  # Non-auto mode for interactive conversation
            )
            
            # Start the app
            await app.start()
            self.console.print("[green]✓ App created and started[/green]\n")
            
            # Step 2: Run conversation turns
            start_time = datetime.now()
            
            for i, user_message in enumerate(conversation_turns, 1):
                self.console.print(f"\n[yellow]Turn {i}/{len(conversation_turns)}[/yellow]")
                
                # Execute query
                turn_start = datetime.now()
                result = await self.executor.execute_query(
                    app=app,
                    query=user_message,
                    show_chat_ui=True
                )
                turn_end = datetime.now()
                
                # Record results
                turn_data = {
                    'turn': i,
                    'user_message': user_message,
                    'response': result.get('response', ''),
                    'elapsed_time': (turn_end - turn_start).total_seconds(),
                    'tool_calls': result.get('tool_calls', []),
                    'success': result.get('success', False)
                }
                results['turns'].append(turn_data)
                
                # Track tools used
                for tool in result.get('tool_calls', []):
                    results['tools_used'].add(tool)
                
                # Small delay between turns
                await asyncio.sleep(0.5)
            
            # Calculate total time
            end_time = datetime.now()
            results['total_time'] = (end_time - start_time).total_seconds()
            
            # Step 3: Cleanup
            await app.stop()
            
        except Exception as e:
            self.console.print(f"\n[red]Test failed: {e}[/red]")
            results['success'] = False
            results['error'] = str(e)
            
        return results
    
    async def run_all_tests(self):
        """Run all conversation test scenarios."""
        test_scenarios = [
            # Test 1: Time-based conversation with follow-ups
            {
                'name': 'Time Conversation with Context',
                'requirements': 'I need an assistant that can tell me times in different timezones',
                'turns': [
                    "What time is it in UTC?",
                    "What about in New York?",
                    "And Tokyo?",
                    "What's the time difference between New York and Tokyo?"
                ]
            },
            
            # Test 2: Mixed tool usage
            {
                'name': 'Mixed Tool Usage',
                'requirements': 'I want an assistant that can help me with time, calculations, and web searches',
                'turns': [
                    "What's the current time?",
                    "Calculate 47 * 23 + 156",
                    "Search for the latest news about AI developments",
                    "What time was it 3 hours ago?"
                ]
            },
            
            # Test 3: Context retention test
            {
                'name': 'Context Retention',
                'requirements': 'I need a helpful assistant with time and calculation abilities',
                'turns': [
                    "My name is Alice and I'm in London. What time is it here?",
                    "I need to call someone in Los Angeles. What time is it there?",
                    "How many hours behind am I?",
                    "If I schedule a call at 3 PM my time, what time would that be for them?"
                ]
            },
            
            # Test 4: Rapid queries
            {
                'name': 'Rapid Sequential Queries',
                'requirements': 'I need a fast assistant for quick calculations and time checks',
                'turns': [
                    "What's 15 + 27?",
                    "Multiply that by 3",
                    "What time is it?",
                    "Add 100 to the first calculation"
                ]
            }
        ]
        
        all_results = []
        
        self.console.print("\n[bold cyan]🧪 Running Multi-Turn Conversation Tests[/bold cyan]")
        self.console.print("=" * 60)
        
        for scenario in test_scenarios:
            result = await self.run_conversation_test(
                app_requirements=scenario['requirements'],
                conversation_turns=scenario['turns'],
                test_name=scenario['name']
            )
            all_results.append(result)
            
            # Print summary
            self.console.print(f"\n[bold]Test Summary:[/bold]")
            self.console.print(f"  Success: {'✅' if result['success'] else '❌'}")
            self.console.print(f"  Total time: {result['total_time']:.2f}s")
            self.console.print(f"  Tools used: {', '.join(result['tools_used']) if result['tools_used'] else 'None'}")
            
            # Show per-turn stats
            if result.get('turns'):
                self.console.print(f"\n  Turn Statistics:")
                for turn in result['turns']:
                    status = '✅' if turn['success'] else '❌'
                    tools = f" (tools: {', '.join(turn['tool_calls'])})" if turn['tool_calls'] else ""
                    self.console.print(f"    Turn {turn['turn']}: {turn['elapsed_time']:.2f}s {status}{tools}")
            
            await asyncio.sleep(1)  # Pause between test scenarios
        
        # Final summary
        self.console.print("\n" + "=" * 60)
        self.console.print("[bold]FINAL TEST RESULTS[/bold]")
        
        passed = sum(1 for r in all_results if r['success'])
        total = len(all_results)
        
        self.console.print(f"\nTests passed: {passed}/{total}")
        
        for result in all_results:
            status = '✅ PASS' if result['success'] else '❌ FAIL'
            self.console.print(f"  {result['test_name']}: {status}")
        
        return all_results


async def main():
    """Main test runner."""
    # Check environment
    env_results = validate_environment_variables(verbose=True)
    
    if not env_results['anthropic_api_key']:
        print("\n❌ ANTHROPIC_API_KEY not set. Please set it to run tests.")
        print("   export ANTHROPIC_API_KEY=your-key-here")
        return
    
    # Validate v1.3 is ready
    validation_ok = await validate_environment(verbose=False)
    if not validation_ok:
        print("\n❌ Environment validation failed. Please check services.")
        return
    
    # Run tests
    runner = ConversationTestRunner()
    results = await runner.run_all_tests()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())