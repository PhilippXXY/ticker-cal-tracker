#!/usr/bin/env python3
'''
Database Management Script for Ticker Calendar Tracker
Usage: python database/manage_db.py [command]

Commands:
    setup   - Create and start the database (first time setup)
    start   - Start the existing database container
    stop    - Stop the database container
    reset   - Drop all data and recreate database with fresh seed data
    status  - Check database container status
    logs    - Show database container logs
    shell   - Open PostgreSQL shell (psql)
'''

# Disclaimer: Created by GitHub Copilot

import subprocess
import sys
import time


# Database configuration (matches docker-compose.yml)
DB_CONTAINER_NAME = "ticker_calendar_local_dev_db"
DB_USER = "ticker_dev"
DB_PASSWORD = "dev_password_123"
DB_NAME = "ticker_calendar_local_dev_db"
DB_PORT = "5432"


class Colors:
    '''ANSI color codes for terminal output'''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message):
    '''Print a styled header message'''
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(message):
    '''Print a success message'''
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    '''Print an error message'''
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message):
    '''Print an info message'''
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message):
    '''Print a warning message'''
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(command, capture_output=False, check=True):
    '''
    Execute a shell command
    
    Args:
        command: Command to execute (list or string)
        capture_output: Whether to capture and return output
        check: Whether to raise exception on non-zero exit code
    
    Returns:
        CompletedProcess object if capture_output=True, None otherwise
    '''
    try:
        if capture_output:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
                shell=isinstance(command, str)
            )
            return result
        else:
            subprocess.run(
                command,
                check=check,
                shell=isinstance(command, str)
            )
            return None
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {e}")
            if capture_output and e.stderr:
                print(e.stderr)
        raise
    except FileNotFoundError:
        print_error(f"Command not found: {command[0] if isinstance(command, list) else command}")
        raise


def check_docker_installed():
    '''Check if Docker is installed'''
    try:
        result = run_command(["docker", "--version"], capture_output=True)
        if result:
            print_success(f"Docker is installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Docker is not installed or not in PATH")
        print_info("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False


def check_docker_running():
    '''Check if Docker daemon is running'''
    try:
        run_command(["docker", "ps"], capture_output=True)
        print_success("Docker daemon is running")
        return True
    except subprocess.CalledProcessError:
        print_error("Docker daemon is not running")
        print_info("Please start Docker Desktop")
        return False


def check_docker_compose_installed():
    '''Check if Docker Compose is installed'''
    try:
        # Try docker compose (newer plugin version)
        result = run_command(["docker", "compose", "version"], capture_output=True)
        if result:
            print_success(f"Docker Compose is installed: {result.stdout.strip()}")
        return "docker compose"
    except subprocess.CalledProcessError:
        # Try docker-compose (standalone version)
        try:
            result = run_command(["docker-compose", "--version"], capture_output=True)
            if result:
                print_success(f"Docker Compose is installed: {result.stdout.strip()}")
            return "docker-compose"
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("Docker Compose is not installed")
            print_info("Docker Compose should come with Docker Desktop")
            return None


def get_container_status():
    '''Get the status of the database container'''
    try:
        result = run_command(
            ["docker", "ps", "-a", "--filter", f"name={DB_CONTAINER_NAME}", "--format", "{{.Status}}"],
            capture_output=True
        )
        if result:
            status = result.stdout.strip()
            return status if status else None
        return None
    except subprocess.CalledProcessError:
        return None


def wait_for_database(max_attempts=30):
    '''Wait for database to be ready'''
    print_info("Waiting for database to be ready...")
    
    for attempt in range(max_attempts):
        try:
            result = run_command(
                ["docker", "exec", DB_CONTAINER_NAME, "pg_isready", "-U", DB_USER, "-d", DB_NAME],
                capture_output=True,
                check=False
            )
            if result and result.returncode == 0:
                print_success("Database is ready!")
                return True
            
            time.sleep(1)
            print(".", end="", flush=True)
        except Exception:
            time.sleep(1)
            print(".", end="", flush=True)
    
    print()
    print_error("Database failed to start within expected time")
    return False


def setup_database(compose_cmd):
    '''Setup the database (first time)'''
    print_header("Setting Up Database")
    
    # Check if container already exists
    status = get_container_status()
    if status:
        print_warning(f"Database container already exists (Status: {status})")
        response = input("Do you want to reset it? This will delete all data. (y/N): ")
        if response.lower() == 'y':
            reset_database(compose_cmd)
            return
        else:
            print_info("Setup cancelled")
            return
    
    # Start the database
    print_info("Creating and starting database container...")
    run_command(f"{compose_cmd} up -d".split())
    
    # Wait for database to be ready
    if wait_for_database():
        print_success("Database setup complete!")
        print_connection_info()
    else:
        print_error("Database setup failed")
        sys.exit(1)


def start_database(compose_cmd):
    '''Start the existing database'''
    print_header("Starting Database")
    
    status = get_container_status()
    if not status:
        print_error("Database container does not exist")
        print_info("Run 'python database/manage_db.py setup' first")
        sys.exit(1)
    
    if "Up" in status:
        print_warning("Database is already running")
        print_connection_info()
        return
    
    print_info("Starting database container...")
    run_command(f"{compose_cmd} start".split())
    
    if wait_for_database():
        print_success("Database started successfully!")
        print_connection_info()


def stop_database(compose_cmd):
    '''Stop the database'''
    print_header("Stopping Database")
    
    status = get_container_status()
    if not status:
        print_error("Database container does not exist")
        return
    
    if "Exited" in status:
        print_warning("Database is already stopped")
        return
    
    print_info("Stopping database container...")
    run_command(f"{compose_cmd} stop".split())
    print_success("Database stopped successfully!")


def reset_database(compose_cmd):
    '''Reset the database (delete and recreate)'''
    print_header("Resetting Database")
    
    print_warning("This will delete ALL data in the database!")
    response = input("Are you sure you want to continue? (y/N): ")
    
    if response.lower() != 'y':
        print_info("Reset cancelled")
        return
    
    print_info("Stopping and removing database container...")
    run_command(f"{compose_cmd} down -v".split())
    
    print_info("Creating fresh database...")
    run_command(f"{compose_cmd} up -d".split())
    
    if wait_for_database():
        print_success("Database reset complete!")
        print_connection_info()
    else:
        print_error("Database reset failed")
        sys.exit(1)


def show_status():
    '''Show database status'''
    print_header("Database Status")
    
    status = get_container_status()
    if not status:
        print_error("Database container does not exist")
        print_info("Run 'python database/manage_db.py setup' to create it")
        return
    
    print_info(f"Container: {DB_CONTAINER_NAME}")
    print_info(f"Status: {status}")
    
    if "Up" in status:
        print_success("Database is running")
        print_connection_info()
        
        # Show container stats
        try:
            result = run_command(
                ["docker", "stats", DB_CONTAINER_NAME, "--no-stream", "--format",
                 "table {{.CPUPerc}}\t{{.MemUsage}}"],
                capture_output=True
            )
            if result:
                print(f"\n{result.stdout}")
        except subprocess.CalledProcessError:
            pass
    else:
        print_warning("Database is not running")
        print_info("Run 'python database/manage_db.py start' to start it")


def show_logs():
    '''Show database logs'''
    print_header("Database Logs")
    
    status = get_container_status()
    if not status:
        print_error("Database container does not exist")
        return
    
    print_info("Showing last 50 lines of logs (Ctrl+C to exit live mode)...")
    print()
    try:
        run_command(["docker", "logs", "-f", "--tail", "50", DB_CONTAINER_NAME])
    except KeyboardInterrupt:
        print("\n")
        print_info("Stopped following logs")


def open_shell():
    '''Open PostgreSQL shell'''
    print_header("PostgreSQL Shell")
    
    status = get_container_status()
    if not status or "Exited" in status:
        print_error("Database is not running")
        print_info("Run 'python database/manage_db.py start' first")
        sys.exit(1)
    
    print_info("Opening PostgreSQL shell (\\q to exit)...")
    print()
    try:
        run_command([
            "docker", "exec", "-it", DB_CONTAINER_NAME,
            "psql", "-U", DB_USER, "-d", DB_NAME
        ])
    except KeyboardInterrupt:
        print("\n")


def print_connection_info():
    '''Print database connection information'''
    print()
    print_info("Connection Details:")
    print("  Host:     localhost")
    print(f"  Port:     {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User:     {DB_USER}")
    print(f"  Password: {DB_PASSWORD}")
    print()
    print_info("Connection String:")
    print(f"  postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}")


def print_usage():
    '''Print usage information'''
    print(__doc__)


def main():
    '''Main entry point'''
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Initialize compose_cmd
    compose_cmd = None
    
    # Check Docker installation (except for help)
    if command not in ['help', '--help', '-h']:
        if not check_docker_installed():
            sys.exit(1)
        
        if not check_docker_running():
            sys.exit(1)
        
        compose_cmd = check_docker_compose_installed()
        if not compose_cmd:
            sys.exit(1)
    
    # Execute command
    try:
        if command == 'setup':
            if compose_cmd:
                setup_database(compose_cmd)
        elif command == 'start':
            if compose_cmd:
                start_database(compose_cmd)
        elif command == 'stop':
            if compose_cmd:
                stop_database(compose_cmd)
        elif command == 'reset':
            if compose_cmd:
                reset_database(compose_cmd)
        elif command == 'status':
            show_status()
        elif command == 'logs':
            show_logs()
        elif command == 'shell':
            open_shell()
        elif command in ['help', '--help', '-h']:
            print_usage()
        else:
            print_error(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n")
        print_info("Operation cancelled")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
