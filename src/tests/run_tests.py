#!/usr/bin/env python3
'''
Test runner script for ticker-cal-tracker.

Provides options to run unit tests, integration tests, or both.
Handles API key checking and provides helpful error messages.
'''

# Disclaimer: Created by GitHub Copilot

import sys
import os
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path('.env'))


def check_env_var(var_name):
    '''Check if environment variable is set.'''
    value = os.getenv(var_name)
    if value:
        print(f"  ✓ {var_name} is set")
        return True
    else:
        print(f"  ✗ {var_name} is NOT set")
        return False


def run_unit_tests(verbose=True):
    '''Run unit tests (no API calls).'''
    print("\n" + "="*70)
    print("Running Unit Tests")
    print("="*70)
    print("These tests use mocks and make NO real API calls.\n")
    
    tests = [
        'tests.test_alpha_vantage',
        'tests.test_finnhub',
        'tests.test_external_api_facade'
    ]
    
    # Skip integration tests
    os.environ['SKIP_INTEGRATION_TESTS'] = '1'
    
    for test in tests:
        print(f"\nRunning {test}...")
        cmd = ['python', '-m', 'unittest', test]
        if verbose:
            cmd.append('-v')
        
        result = subprocess.run(cmd, cwd='src')
        if result.returncode != 0:
            print(f"\n✗ {test} failed!")
            return False
    
    print("\n" + "="*70)
    print("✓ All unit tests passed!")
    print("="*70)
    return True


def run_integration_tests(verbose=True):
    '''Run integration tests (makes real API calls).'''
    print("\n" + "="*70)
    print("Running Integration Tests")
    print("="*70)
    print("⚠️  These tests make REAL API calls and count against rate limits!\n")
    
    # Check for API keys
    print("Checking for API keys...")
    has_alpha_vantage = check_env_var('API_KEY_ALPHA_VANTAGE')
    has_finnhub = check_env_var('API_KEY_FINNHUB')
    
    if not has_alpha_vantage and not has_finnhub:
        print("\n✗ No API keys found!")
        print("\nPlease set at least one of:")
        print("  export API_KEY_ALPHA_VANTAGE='your_key'")
        print("  export API_KEY_FINNHUB='your_key'")
        return False
    
    print("\nAPI Rate Limits:")
    if has_alpha_vantage:
        print("  Alpha Vantage: 25 requests/day, 5 requests/minute")
    if has_finnhub:
        print("  Finnhub: 60 requests/minute")
    
    # Ask for confirmation
    response = input("\nProceed with integration tests? (y/N): ")
    if response.lower() != 'y':
        print("Integration tests cancelled.")
        return False
    
    # Remove skip flag
    os.environ.pop('SKIP_INTEGRATION_TESTS', None)
    
    tests = []
    if has_alpha_vantage:
        tests.append('tests.test_alpha_vantage_integration')
    if has_finnhub:
        tests.append('tests.test_finnhub_integration')
    
    success = True
    for test in tests:
        print(f"\nRunning {test}...")
        cmd = ['python', '-m', 'unittest', test]
        if verbose:
            cmd.append('-v')
        
        result = subprocess.run(cmd, cwd='src')
        if result.returncode != 0:
            print(f"\n⚠️  {test} had failures (may be due to rate limits)")
            success = False
    
    if success:
        print("\n" + "="*70)
        print("✓ All integration tests completed!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠️  Some integration tests failed - check output above")
        print("="*70)
    
    return success


def run_all_tests(verbose=True):
    '''Run both unit and integration tests.'''
    print("\n" + "="*70)
    print("Running ALL Tests")
    print("="*70)
    
    # Run unit tests first
    if not run_unit_tests(verbose):
        print("\n✗ Unit tests failed, skipping integration tests")
        return False
    
    # Then integration tests
    return run_integration_tests(verbose)


def main():
    '''Main entry point.'''
    parser = argparse.ArgumentParser(
        description='Run tests for ticker-cal-tracker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --unit              # Run unit tests only (no API calls)
  %(prog)s --integration       # Run integration tests only (real API calls)
  %(prog)s --all              # Run all tests
  %(prog)s --unit -q          # Run unit tests quietly
        '''
    )
    
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run unit tests only (no real API calls)'
    )
    
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run integration tests only (makes real API calls)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run both unit and integration tests'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Less verbose output'
    )
    
    args = parser.parse_args()
    
    # Default to unit tests if nothing specified
    if not (args.unit or args.integration or args.all):
        print("No test type specified, defaulting to --unit")
        print("Use --help for more options\n")
        args.unit = True
    
    verbose = not args.quiet
    
    try:
        if args.all:
            success = run_all_tests(verbose)
        elif args.integration:
            success = run_integration_tests(verbose)
        else:  # unit tests
            success = run_unit_tests(verbose)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
