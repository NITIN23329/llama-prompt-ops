#!/usr/bin/env python3
"""
Debug script for running the migrate command with enhanced debugging capabilities.

This script provides several ways to debug the migration process:
1. Standard execution with enhanced logging
2. Python debugger (pdb) integration
3. Visual Studio Code debugger support
4. Exception handling with detailed tracebacks

Usage:
    python debug_migrate.py                    # Normal execution with debug logging
    python debug_migrate.py --pdb             # Run with Python debugger
    python debug_migrate.py --break-on-error  # Break into debugger on exceptions
    python debug_migrate.py --verbose         # Extra verbose output
"""

import argparse
import logging
import os
import sys
import traceback
from pathlib import Path
from contextlib import contextmanager

# Add the src directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

@contextmanager
def redirect_stdout_stderr(log_file):
    """Context manager to redirect stdout and stderr to a file."""
    # Open the log file for writing
    with open(log_file, 'a') as f:
        # Save original stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # Redirect stdout and stderr to the file
            sys.stdout = f
            sys.stderr = f
            yield f
        finally:
            # Restore original stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

def setup_debug_logging(verbose=False, redirect_all=False, log_file='debug_migrate.log'):
    """Set up enhanced logging for debugging."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Set up handlers
    handlers = []
    
    if redirect_all:
        # Only file handler when redirecting all output
        handlers.append(logging.FileHandler(log_file, mode='w'))
        print(f"All output will be redirected to: {log_file}")
    else:
        # Both console and file handlers
        handlers.extend([
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, mode='w')
        ])
        print(f"Debug logging enabled. Log file: {log_file}")
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Force reconfiguration
    )
    
    # Set specific loggers to debug level
    loggers_to_debug = [
        'llama_prompt_ops',
        'llama_prompt_ops.core.model',
        'llama_prompt_ops.core.metrics',
        'llama_prompt_ops.core.evaluation',
        'llama_prompt_ops.interfaces.cli'
    ]
    
    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    if not redirect_all:
        print(f"Log level: {logging.getLevelName(log_level)}")
    
    return log_file

def debug_environment():
    """Print debug information about the environment."""
    print("=== Debug Environment Information ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    # Check if we can import our modules
    try:
        from llama_prompt_ops.interfaces.cli import main
        print("✓ Successfully imported llama_prompt_ops.interfaces.cli")
    except ImportError as e:
        print(f"✗ Failed to import CLI module: {e}")
        return False
    
    # Check for required dependencies
    required_packages = ['dspy', 'sentence_transformers', 'sklearn', 'pandas', 'pyyaml']
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is missing")
    
    print("=====================================\n")
    return True

def run_with_debugger():
    """Run the migrate command with Python debugger (pdb)."""
    print("Starting migration with Python debugger (pdb)")
    print("Debugger commands:")
    print("  n(ext)     - Execute next line")
    print("  s(tep)     - Step into functions")
    print("  c(ontinue) - Continue execution")
    print("  l(ist)     - Show current code")
    print("  p <var>    - Print variable value")
    print("  q(uit)     - Quit debugger")
    print("  h(elp)     - Show help")
    print("-" * 50)
    
    import pdb
    pdb.set_trace()
    
    # Import and run the CLI
    from llama_prompt_ops.interfaces.cli import main
    main(['migrate'])

def run_with_exception_handler(break_on_error=False):
    """Run the migrate command with enhanced exception handling."""
    try:
        from llama_prompt_ops.interfaces.cli import main
        main(['migrate'])
    except Exception as e:
        print(f"\n{'='*60}")
        print("ERROR ENCOUNTERED DURING MIGRATION")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        
        if break_on_error:
            print(f"\n{'='*60}")
            print("ENTERING DEBUGGER DUE TO ERROR")
            print(f"{'='*60}")
            import pdb
            pdb.post_mortem()
        else:
            print(f"\nTo debug this error, run with --break-on-error flag")
        
        return False
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Debug script for llama-prompt-ops migrate command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--pdb', action='store_true',
                        help='Run with Python debugger (pdb)')
    parser.add_argument('--break-on-error', action='store_true',
                        help='Break into debugger when an exception occurs')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose debug output')
    parser.add_argument('--env-check', action='store_true',
                        help='Only check environment and exit')
    
    args = parser.parse_args()
    
    # Set up debug logging
    setup_debug_logging(verbose=args.verbose)
    
    # Check environment
    if not debug_environment():
        print("Environment check failed. Please fix the issues above.")
        return 1
    
    if args.env_check:
        print("Environment check completed successfully.")
        return 0
    
    print("Starting migration process...")
    print(f"Debug options: pdb={args.pdb}, break_on_error={args.break_on_error}, verbose={args.verbose}")
    print("-" * 60)
    
    if args.pdb:
        run_with_debugger()
    else:
        success = run_with_exception_handler(break_on_error=args.break_on_error)
        if not success:
            return 1
    
    print("\nMigration process completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
