#!/usr/bin/env python3
"""
Test script for verifying tool call streaming in Cogzia Alpha v1.3.

This script tests that tool calls are displayed immediately when detected,
before the tool parameters are fully streamed and executed.
"""
import asyncio
import os
import sys
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tools.demos.cogzia_alpha_v1_3.app_executor import MinimalAIApp
from tools.demos.cogzia_alpha_v1_3.ui import EnhancedConsole


async def test_tool_streaming():
    """Test tool call streaming detection."""
    console = EnhancedConsole()
    
    console.print("\n[bold cyan]Testing Tool Call Streaming Detection[/bold cyan]")
    console.print("=" * 60)
    
    # Test queries that should trigger different tools
    test_queries = [
        "What time is it right now?",
        "Calculate 15 * 23 + 47",
        "Search for recent advances in quantum computing"
    ]
    
    # Create app with verbose mode to see debug output
    app = MinimalAIApp(
        app_id="tool_stream_test",
        system_prompt="You are a helpful assistant with access to various tools.",
        mcp_servers=["time", "calculator", "brave_search"],
        verbose=True
    )
    
    try:
        # Start the app
        await app.start()
        console.print("[green]✓ App started successfully[/green]\n")
        
        for query in test_queries:
            console.print(f"\n[yellow]Testing query:[/yellow] {query}")
            console.print("-" * 40)
            
            # Track events
            events_log = []
            tool_detected_time = None
            tool_executed_time = None
            
            async def event_logger(chunk):
                """Log streaming events with timestamps."""
                nonlocal tool_detected_time, tool_executed_time
                
                event_type = chunk.get('type', '')
                timestamp = datetime.now()
                events_log.append((timestamp, event_type, chunk))
                
                if event_type == 'tool_call_detected':
                    tool_detected_time = timestamp
                    console.print(f"[dim cyan]⚡ Tool detected at {timestamp.strftime('%H:%M:%S.%f')[:-3]}:[/dim cyan] {chunk.get('message', '')}")
                elif event_type == 'tool_call_json':
                    tool_executed_time = timestamp
                    console.print(f"[dim green]📞 Tool call prepared at {timestamp.strftime('%H:%M:%S.%f')[:-3]}[/dim green]")
                elif event_type == 'text':
                    # Don't print text chunks in test mode
                    pass
                elif event_type == 'error':
                    console.print(f"[red]❌ Error: {chunk.get('error', 'Unknown error')}[/red]")
            
            # Execute query with event logging
            result = await app.query(
                message=query,
                stream=True,
                on_chunk=event_logger
            )
            
            # Analyze timing
            if tool_detected_time and tool_executed_time:
                time_diff = (tool_executed_time - tool_detected_time).total_seconds() * 1000
                console.print(f"\n[green]✓ Tool detection worked![/green]")
                console.print(f"  Detection to execution: {time_diff:.1f}ms")
                
                # Check if detection happened before execution
                if time_diff > 0:
                    console.print(f"  [green]✓ Tool was detected BEFORE execution[/green]")
                else:
                    console.print(f"  [red]✗ Tool detection timing issue[/red]")
            else:
                if not tool_detected_time:
                    console.print(f"\n[yellow]⚠ No tool detection event received[/yellow]")
                if not tool_executed_time:
                    console.print(f"[yellow]⚠ No tool execution event received[/yellow]")
            
            # Show event summary
            console.print(f"\nEvent summary:")
            event_counts = {}
            for _, event_type, _ in events_log:
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            for event_type, count in event_counts.items():
                console.print(f"  {event_type}: {count}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
    except Exception as e:
        console.print(f"\n[red]Test failed with error: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await app.stop()
        console.print("\n[dim]App stopped[/dim]")


async def main():
    """Main test runner."""
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set. Please set it to run tests.")
        print("   export ANTHROPIC_API_KEY=your-key-here")
        return
    
    await test_tool_streaming()
    print("\n✅ Test completed")


if __name__ == "__main__":
    asyncio.run(main())