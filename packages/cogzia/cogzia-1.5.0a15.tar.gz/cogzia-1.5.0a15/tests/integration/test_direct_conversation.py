#!/usr/bin/env python3
"""
Direct conversation test for Cogzia Alpha v1.3.

This script tests multi-turn conversations by directly using the MinimalAIApp
class, simulating real user interactions without any mocking.
"""
import asyncio
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tools.demos.cogzia_alpha_v1_3.app_executor import MinimalAIApp
from tools.demos.cogzia_alpha_v1_3.services import ServiceDiscovery
from tools.demos.cogzia_alpha_v1_3.ui import EnhancedConsole
from tools.demos.cogzia_alpha_v1_3.utils import PromptGenerator


class DirectConversationTester:
    """Tests conversations directly with MinimalAIApp."""
    
    def __init__(self, verbose: bool = False):
        self.console = EnhancedConsole()
        self.verbose = verbose
        self.service_discovery = ServiceDiscovery()
        self.prompt_generator = PromptGenerator()
        
    async def create_app_for_test(self, requirements: str) -> MinimalAIApp:
        """Create an app instance for testing."""
        # Discover servers
        servers, server_details = await self.service_discovery.discover_servers(
            requirements=requirements,
            auto_start=True
        )
        
        if not servers:
            raise ValueError("No servers found for requirements")
        
        # Generate system prompt
        system_prompt_parts = []
        async for chunk in self.prompt_generator.generate_system_prompt_stream(
            requirements=requirements,
            servers=servers,
            server_capabilities=server_details
        ):
            system_prompt_parts.append(chunk)
        
        system_prompt = ''.join(system_prompt_parts)
        
        # Create app
        app = MinimalAIApp(
            app_id=f"test_{int(time.time())}",
            system_prompt=system_prompt,
            mcp_servers=servers[:3],  # Limit to 3 servers
            verbose=self.verbose,
            auto_mode=False  # Interactive mode
        )
        
        return app
    
    async def run_conversation(self, 
                             app: MinimalAIApp,
                             messages: List[str],
                             test_name: str) -> Dict[str, Any]:
        """Run a conversation with multiple turns."""
        self.console.print(f"\n[bold cyan]🗣️ {test_name}[/bold cyan]")
        self.console.print("─" * 50)
        
        results = {
            'test_name': test_name,
            'turns': [],
            'total_duration': 0,
            'tool_calls_total': 0,
            'success': True
        }
        
        start_time = datetime.now()
        
        try:
            # Start the app
            await app.start()
            
            # Process each message
            for i, message in enumerate(messages, 1):
                self.console.print(f"\n[yellow]Turn {i}:[/yellow] {message}")
                
                turn_results = {
                    'turn': i,
                    'message': message,
                    'response_chunks': [],
                    'tool_calls': [],
                    'duration': 0,
                    'success': False
                }
                
                turn_start = time.time()
                
                # Collect response
                response_text = []
                tool_calls = []
                
                async def on_chunk(chunk: Dict[str, Any]):
                    """Handle streaming chunks."""
                    chunk_type = chunk.get('type', '')
                    
                    if chunk_type == 'text':
                        content = chunk.get('content', '')
                        response_text.append(content)
                        print(content, end='', flush=True)
                    
                    elif chunk_type == 'tool_call_detected':
                        tool_name = chunk.get('tool_name', 'unknown')
                        print(f"\n{chunk.get('message', '')}", flush=True)
                        tool_calls.append(tool_name)
                    
                    elif chunk_type == 'tool_call_json':
                        # Tool is being called
                        pass
                    
                    elif chunk_type == 'error':
                        print(f"\n❌ Error: {chunk.get('error', 'Unknown error')}")
                
                # Execute query
                try:
                    await app.query(
                        message=message,
                        stream=True,
                        on_chunk=on_chunk
                    )
                    turn_results['success'] = True
                except Exception as e:
                    self.console.print(f"[red]Error in turn {i}: {e}[/red]")
                    turn_results['error'] = str(e)
                
                # Record results
                turn_duration = time.time() - turn_start
                turn_results['duration'] = turn_duration
                turn_results['response'] = ''.join(response_text)
                turn_results['tool_calls'] = tool_calls
                
                results['turns'].append(turn_results)
                results['tool_calls_total'] += len(tool_calls)
                
                # Show summary
                self.console.print(f"\n[dim]Turn {i} completed in {turn_duration:.2f}s")
                if tool_calls:
                    self.console.print(f"[dim]Tools used: {', '.join(tool_calls)}[/dim]")
                
                # Small delay between turns
                await asyncio.sleep(0.5)
            
            # Calculate total duration
            results['total_duration'] = (datetime.now() - start_time).total_seconds()
            
        except Exception as e:
            self.console.print(f"[red]Conversation failed: {e}[/red]")
            results['success'] = False
            results['error'] = str(e)
        
        finally:
            # Always cleanup
            try:
                await app.stop()
            except:
                pass
        
        return results
    
    async def run_test_suite(self):
        """Run complete test suite."""
        test_scenarios = [
            {
                'name': 'Time Zone Conversation',
                'requirements': 'I need an AI that can tell me time in different timezones',
                'messages': [
                    "Hello! Can you help me with time zones?",
                    "What time is it right now in UTC?",
                    "What about Pacific Time?",
                    "Is Tokyo ahead or behind UTC?",
                    "If it's 3 PM in New York, what time is it in London?"
                ]
            },
            {
                'name': 'Calculator Context Test',
                'requirements': 'I want an AI assistant that can do calculations and remember previous results',
                'messages': [
                    "Let's do some math. What's 156 + 89?",
                    "Now multiply that result by 3",
                    "Divide the original sum by 5",
                    "What was our first calculation again?"
                ]
            },
            {
                'name': 'Mixed Tools Conversation',
                'requirements': 'I need a versatile assistant with time, math, and search capabilities',
                'messages': [
                    "Hi! I need help planning my day",
                    "What's the current time?",
                    "I have a meeting in 3.5 hours. What time will that be?",
                    "Calculate how many minutes that is",
                    "Search for tips on effective virtual meetings"
                ]
            },
            {
                'name': 'Conversation Memory Test',
                'requirements': 'I want an AI that remembers our conversation context',
                'messages': [
                    "My name is Sarah and I work in tech",
                    "What time is it in Silicon Valley?",
                    "I need to schedule a call with my team in Berlin",
                    "What's the time difference?",
                    "Do you remember what field I work in?"
                ]
            }
        ]
        
        all_results = []
        
        self.console.print("\n[bold cyan]🧪 Cogzia Alpha v1.3 Direct Conversation Tests[/bold cyan]")
        self.console.print("=" * 60)
        self.console.print("Testing multi-turn conversations with real services...")
        
        for scenario in test_scenarios:
            try:
                # Create app for this scenario
                self.console.print(f"\n[dim]Setting up: {scenario['name']}...[/dim]")
                app = await self.create_app_for_test(scenario['requirements'])
                
                # Run conversation
                results = await self.run_conversation(
                    app=app,
                    messages=scenario['messages'],
                    test_name=scenario['name']
                )
                
                all_results.append(results)
                
                # Print summary
                self.console.print(f"\n[bold]Summary for {scenario['name']}:[/bold]")
                self.console.print(f"  Status: {'✅ PASS' if results['success'] else '❌ FAIL'}")
                self.console.print(f"  Duration: {results['total_duration']:.2f}s")
                self.console.print(f"  Tool calls: {results['tool_calls_total']}")
                self.console.print(f"  Turns completed: {len([t for t in results['turns'] if t['success']])}/{len(scenario['messages'])}")
                
            except Exception as e:
                self.console.print(f"[red]Failed to run {scenario['name']}: {e}[/red]")
                all_results.append({
                    'test_name': scenario['name'],
                    'success': False,
                    'error': str(e)
                })
            
            # Pause between scenarios
            await asyncio.sleep(2)
        
        # Final report
        self.console.print("\n" + "=" * 60)
        self.console.print("[bold]FINAL TEST REPORT[/bold]")
        
        passed = sum(1 for r in all_results if r.get('success', False))
        total = len(all_results)
        
        self.console.print(f"\nTests Passed: {passed}/{total}")
        
        for result in all_results:
            status = '✅' if result.get('success', False) else '❌'
            name = result.get('test_name', 'Unknown')
            
            if result.get('success'):
                tool_info = f" ({result['tool_calls_total']} tools, {result['total_duration']:.1f}s)"
            else:
                tool_info = f" - {result.get('error', 'Unknown error')}"
            
            self.console.print(f"  {status} {name}{tool_info}")
        
        return all_results


async def main():
    """Main entry point."""
    # Check environment
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set.")
        print("   export ANTHROPIC_API_KEY=your-key-here")
        return
    
    print("✓ Environment ready")
    
    # Run tests
    tester = DirectConversationTester(verbose=False)
    results = await tester.run_test_suite()
    
    # Check if all passed
    all_passed = all(r.get('success', False) for r in results)
    
    if all_passed:
        print("\n✅ All conversation tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)