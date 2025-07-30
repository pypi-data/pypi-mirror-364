#!/usr/bin/env python3
"""
Entry point script to run the Ze Prompter server
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ze_prompter.cli import cli

if __name__ == "__main__":
    cli()