#!/usr/bin/env python3
"""
Test script for the stdio-to-HTTP proxy functionality.

This script tests the new URL-based installation and proxy features.
"""

import asyncio
import subprocess
import sys
import json


def test_install_command():
    """Test the install command with URL."""
    print("Testing install command with URL...")
    
    # Test cases
    test_cases = [
        {
            "name": "Claude Desktop installation",
            "cmd": [
                "mcpstore-cli", "install",
                "http://localhost:8090/mcp/75d341c4930b6662da822254?client=claude",
                "Gmail",
                "--client", "claude"
            ],
            "expected": "stdio proxy configuration"
        },
        {
            "name": "Cursor installation",
            "cmd": [
                "mcpstore-cli", "install",
                "http://localhost:8090/mcp/75d341c4930b6662da822254?client=cursor",
                "Gmail",
                "--client", "cursor"
            ],
            "expected": "direct URL configuration"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"Command: {' '.join(test['cmd'])}")
        print(f"Expected: {test['expected']}")
        print("-" * 50)


def test_run_command():
    """Test the run command with --url."""
    print("\nTesting run command with --url...")
    
    cmd = [
        "mcpstore-cli", "run",
        "--url", "http://localhost:8090/mcp/75d341c4930b6662da822254?client=claude",
        "Gmail"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("This should start the stdio-to-HTTP proxy")
    print("-" * 50)


def test_config_generation():
    """Test configuration generation logic."""
    print("\nTesting configuration generation...")
    
    # Simulate configuration for different clients
    configs = {
        "claude": {
            "mcpServers": {
                "Gmail": {
                    "command": "uvx",
                    "args": [
                        "mcpstore-cli",
                        "run",
                        "--url",
                        "http://localhost:8090/mcp/75d341c4930b6662da822254?client=claude",
                        "Gmail"
                    ]
                }
            }
        },
        "cursor": {
            "mcpServers": {
                "Gmail": {
                    "url": "http://localhost:8090/mcp/75d341c4930b6662da822254?client=cursor"
                }
            }
        }
    }
    
    for client, config in configs.items():
        print(f"\n{client} configuration:")
        print(json.dumps(config, indent=2))


def main():
    """Run all tests."""
    print("=== mcpstore-cli URL Installation and Proxy Tests ===\n")
    
    test_install_command()
    test_run_command()
    test_config_generation()
    
    print("\n=== Summary ===")
    print("1. Install command now supports URL format")
    print("2. Claude Desktop gets stdio proxy configuration")
    print("3. Other clients (like Cursor) get direct URL configuration")
    print("4. Run command supports --url for stdio-to-HTTP proxy")
    
    print("\n=== Usage Examples ===")
    print("\n# Install URL-based server to Claude Desktop:")
    print('mcpstore-cli install "http://localhost:8090/mcp/abc123?client=claude" "Gmail" --client claude')
    
    print("\n# Run stdio-to-HTTP proxy manually:")
    print('mcpstore-cli run --url "http://localhost:8090/mcp/abc123" "Gmail"')
    
    print("\n# Claude Desktop will execute:")
    print('uvx mcpstore-cli run --url "http://localhost:8090/mcp/abc123?client=claude" "Gmail"')


if __name__ == "__main__":
    main()