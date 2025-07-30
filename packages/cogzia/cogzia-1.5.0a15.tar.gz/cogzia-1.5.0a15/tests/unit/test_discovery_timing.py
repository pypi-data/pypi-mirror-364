#!/usr/bin/env python3
"""
Test script to measure discovery timing with different models.

This script runs the cogzia demo workflow and measures the time taken
for the tool discovery step with different Anthropic models.
"""
import os
import sys
import asyncio
import time
from typing import List, Dict, Any
from datetime import datetime

# Models to test
MODELS_TO_TEST = [
    "claude-3-5-sonnet-20241022",  # Current default (baseline)
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514", 
    "claude-3-5-haiku-20241022",
    "claude-3-7-sonnet-20250219"
]

# Test requirements
TEST_REQUIREMENTS = "I need an app that can search the web for information"


async def run_single_test(model: str) -> Dict[str, Any]:
    """Run a single test with the specified model."""
    print(f"\n{'='*60}")
    print(f"Testing model: {model}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Set the model
    os.environ['ANTHROPIC_MODEL'] = model
    
    # Import here to ensure fresh import with new env var
    from demo_workflow import AIAppCreateDemo
    
    try:
        # Create demo instance
        demo = AIAppCreateDemo(
            auto_mode=True,
            auto_step=5,  # Stop after discovery step
            auto_requirements=TEST_REQUIREMENTS,
            verbose=False,
            enable_auth=False
        )
        
        # Run the demo
        start_time = time.time()
        await demo.run()
        total_time = time.time() - start_time
        
        # Extract discovery time from output (if available)
        # For now, we'll use the total time as a proxy
        result = {
            "model": model,
            "success": True,
            "total_time": total_time,
            "error": None
        }
        
    except Exception as e:
        result = {
            "model": model,
            "success": False,
            "total_time": None,
            "error": str(e)
        }
    
    return result


async def run_baseline_test():
    """Run baseline test with current default model."""
    print("Starting baseline discovery timing test...")
    print(f"Requirements: {TEST_REQUIREMENTS}")
    
    # Get current model or use default
    current_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
    
    # Run baseline test
    result = await run_single_test(current_model)
    
    # Print results
    print(f"\n{'='*60}")
    print("BASELINE TEST RESULTS")
    print(f"{'='*60}")
    print(f"Model: {result['model']}")
    if result['success']:
        print(f"Status: SUCCESS")
        print(f"Total Time: {result['total_time']:.2f} seconds")
    else:
        print(f"Status: FAILED")
        print(f"Error: {result['error']}")
    print(f"{'='*60}\n")
    
    return result


async def run_all_tests():
    """Run tests for all models."""
    print("Starting discovery timing tests for all models...")
    print(f"Requirements: {TEST_REQUIREMENTS}")
    print(f"Models to test: {', '.join(MODELS_TO_TEST)}")
    
    results = []
    
    for model in MODELS_TO_TEST:
        result = await run_single_test(model)
        results.append(result)
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY OF ALL TESTS")
    print(f"{'='*60}")
    print(f"{'Model':<35} {'Status':<10} {'Time (s)':<10}")
    print(f"{'-'*55}")
    
    for result in results:
        model = result['model']
        status = "SUCCESS" if result['success'] else "FAILED"
        time_str = f"{result['total_time']:.2f}" if result['total_time'] else "N/A"
        print(f"{model:<35} {status:<10} {time_str:<10}")
    
    print(f"{'='*60}\n")
    
    return results


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        asyncio.run(run_all_tests())
    else:
        asyncio.run(run_baseline_test())


if __name__ == "__main__":
    main()