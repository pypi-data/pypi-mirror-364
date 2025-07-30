#!/usr/bin/env python3
import sys
import os
import click
import uvicorn
import subprocess
import time
import signal
import requests

# Add the parent directory to the path so we can import ze_prompter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ze_prompter.models import init_db, SessionLocal, User
    from ze_prompter.api.main import app
    from ze_prompter.core.auth import AuthManager
except ImportError:
    # If we're running from within the package directory
    from models import init_db, SessionLocal, User
    from api.main import app
    from core.auth import AuthManager

@click.group()
def cli():
    """Ze Prompter CLI"""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host, port, reload):
    """Start the FastAPI server"""
    click.echo(f"Starting Ze Prompter server on {host}:{port}")
    init_db()
    if reload:
        uvicorn.run("ze_prompter.api.main:app", host=host, port=port, reload=reload)
    else:
        uvicorn.run(app, host=host, port=port)

@cli.command()
def init():
    """Initialize the database"""
    click.echo("Initializing database...")
    init_db()
    click.echo("Database initialized successfully!")

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_ngrok(port):
    """Start ngrok tunnel and return the public URL"""
    click.echo("Starting ngrok tunnel...")
    
    # Start ngrok in the background
    process = subprocess.Popen(
        ['ngrok', 'http', str(port), '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for ngrok to start and get the public URL
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        public_url = tunnel.get('public_url')
                        if public_url:
                            return process, public_url
        except requests.exceptions.ConnectionError:
            pass
        
        time.sleep(1)
    
    # If we get here, ngrok failed to start
    process.terminate()
    raise click.ClickException("❌ Failed to start ngrok tunnel")

def update_env_file(ngrok_url):
    """Update .env file with ngrok URL"""
    env_path = '.env'
    env_lines = []
    
    # Read existing .env file if it exists
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    
    # Remove any existing ZE_PROMPTER_URL entries
    env_lines = [line for line in env_lines if not line.startswith('ZE_PROMPTER_URL=')]
    
    # Add the new ngrok URL
    env_lines.append(f'ZE_PROMPTER_URL={ngrok_url}\n')
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    click.echo(f"✅ Updated .env file with ZE_PROMPTER_URL={ngrok_url}")

def validate_database_config():
    """Validate database configuration for deployment"""
    db_url = os.getenv('ZE_PROMPTER_DB', 'sqlite:///./prompt_library.db')
    ngrok_url = os.getenv('ZE_PROMPTER_URL', '')
    
    # If ngrok URL is set but database is still SQLite, show warning
    if ngrok_url and db_url.startswith('sqlite:'):
        click.echo("⚠️  WARNING: You're using SQLite database with a public URL.")
        click.echo("   This might cause issues if multiple users access the application simultaneously.")
        click.echo("   Consider using PostgreSQL or MySQL for production deployments.")
        click.echo()

@cli.command()
def create_account():
    """Create a new user account interactively"""
    click.echo("🔧 Creating a new user account...")
    
    # Initialize database first
    init_db()
    
    # Get user input
    username = click.prompt("Username", type=str)
    email = click.prompt("Email", type=str)
    password = click.prompt("Password", type=str, hide_input=True, confirmation_prompt=True)
    is_superuser = click.confirm("Make this user a superuser (admin)?", default=False)
    
    # Create the user
    db = SessionLocal()
    try:
        auth_manager = AuthManager(db)
        
        # Check if user already exists
        if auth_manager.get_user_by_username(username):
            click.echo(f"❌ User '{username}' already exists!")
            return
        
        # Create the user
        user = auth_manager.create_user(
            username=username,
            email=email,
            password=password,
            is_superuser=is_superuser
        )
        
        user_type = "superuser" if is_superuser else "regular user"
        click.echo(f"✅ Successfully created {user_type}: {username}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create user: {e}")
    finally:
        db.close()

@cli.command()
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--no-ngrok', is_flag=True, help='Skip ngrok tunnel creation')
def deploy(port, no_ngrok):
    """Deploy Ze Prompter with ngrok tunnel for easy sharing"""
    click.echo("🚀 Deploying Ze Prompter...")
    
    # Initialize database
    click.echo("Initializing database...")
    init_db()
    
    ngrok_process = None
    public_url = None
    
    if not no_ngrok:
        # Check if ngrok is installed
        if not check_ngrok_installed():
            click.echo("❌ ngrok is not installed!")
            click.echo("📦 Please install ngrok from: https://ngrok.com/download")
            click.echo("   Or run with --no-ngrok to deploy without tunnel")
            return
        
        try:
            # Start ngrok tunnel
            ngrok_process, public_url = start_ngrok(port)
            click.echo(f"✅ ngrok tunnel created: {public_url}")
            
            # Update .env file
            update_env_file(public_url)
            
            # Validate database configuration
            validate_database_config()
            
        except Exception as e:
            click.echo(f"❌ Failed to start ngrok: {e}")
            return
    
    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully"""
        click.echo("\n🛑 Shutting down...")
        if ngrok_process:
            click.echo("Stopping ngrok tunnel...")
            ngrok_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        click.echo(f"🌟 Ze Prompter is now running!")
        click.echo(f"📍 Local URL: http://localhost:{port}")
        if public_url:
            click.echo(f"🌍 Public URL: {public_url}")
        click.echo("🔐 Create an account with: python -m ze_prompter.cli create-account")
        click.echo("📖 Press Ctrl+C to stop the server")
        click.echo()
        
        # Start the FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except KeyboardInterrupt:
        pass
    finally:
        if ngrok_process:
            click.echo("Stopping ngrok tunnel...")
            ngrok_process.terminate()

if __name__ == "__main__":
    cli()