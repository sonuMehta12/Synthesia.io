#!/usr/bin/env python3
"""
Setup script for the Learning Agent project.

This script helps users set up the environment, install dependencies,
and configure the project for development.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print the setup banner."""
    print("🎓 Learning Agent - Setup Script")
    print("=" * 40)
    print("Setting up your learning agent development environment...")
    print()


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    print("\n🔧 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install project dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Determine the pip command based on the OS
    if os.name == 'nt':  # Windows
        pip_cmd = ["venv\\Scripts\\pip"]
    else:  # Unix/Linux/macOS
        pip_cmd = ["venv/bin/pip"]
    
    try:
        # Upgrade pip first
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
        
        # Install requirements
        subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create a .env file template if it doesn't exist."""
    print("\n🔐 Setting up environment variables...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# Learning Agent Environment Variables

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
SESSION_TIMEOUT=3600

# Optional: Database Configuration (for future use)
# DATABASE_URL=postgresql://user:password@localhost:5432/learning_agent
# REDIS_URL=redis://localhost:6379
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_template)
        print("✅ .env file created successfully")
        print("⚠️  Please update the .env file with your API keys!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def run_tests():
    """Run the test suite to verify installation."""
    print("\n🧪 Running tests...")
    
    # Determine the python command based on the OS
    if os.name == 'nt':  # Windows
        python_cmd = ["venv\\Scripts\\python"]
    else:  # Unix/Linux/macOS
        python_cmd = ["venv/bin/python"]
    
    try:
        # Run tests
        result = subprocess.run(
            python_cmd + ["-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Tests passed successfully")
            return True
        else:
            print("⚠️  Some tests failed, but installation is complete")
            print("You can run tests later with: python -m pytest tests/ -v")
            return True
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        print("You can run tests later with: python -m pytest tests/ -v")
        return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("Your Learning Agent environment is ready!")
    print()
    print("📋 Next Steps:")
    print("1. Update your .env file with API keys")
    print("2. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    print("3. Run the demo:")
    print("   python demo.py")
    print("4. Run tests:")
    print("   python -m pytest tests/ -v")
    print("5. Start development:")
    print("   python src/main.py")
    print()
    print("📚 Documentation:")
    print("- README.md: Project overview and setup")
    print("- docs/first_node_implementation.md: Detailed implementation guide")
    print("- docs/development_roadmap.md: Project roadmap")
    print()
    print("🚀 Happy coding!")


def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main() 