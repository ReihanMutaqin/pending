#!/usr/bin/env python3
"""
Run Script untuk WSA Fulfillment Pro
Script ini digunakan untuk menjalankan aplikasi dengan berbagai opsi
"""

import argparse
import sys
import os
import subprocess


def run_app():
    """Run aplikasi Streamlit"""
    print("🚀 Starting WSA Fulfillment Pro...")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Run streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port=8501",
        "--server.address=localhost"
    ]
    
    print("\n📱 Aplikasi akan dibuka di browser...")
    print("URL: http://localhost:8501\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Aplikasi dihentikan.")


def run_tests():
    """Run unit tests"""
    print("🧪 Running unit tests...")
    print("=" * 50)
    
    cmd = [sys.executable, "-m", "unittest", "discover", "tests/", "-v"]
    
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ Error running tests: {e}")


def run_linter():
    """Run code linter"""
    print("🔍 Running code linter...")
    print("=" * 50)
    
    # Check if flake8 is installed
    try:
        subprocess.run([sys.executable, "-m", "flake8", "src/", "--max-line-length=120"])
    except FileNotFoundError:
        print("❌ flake8 not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flake8"])
        subprocess.run([sys.executable, "-m", "flake8", "src/", "--max-line-length=120"])


def format_code():
    """Format code dengan black"""
    print("🎨 Formatting code...")
    print("=" * 50)
    
    # Check if black is installed
    try:
        subprocess.run([sys.executable, "-m", "black", "src/", "tests/", "app.py"])
    except FileNotFoundError:
        print("❌ black not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "black"])
        subprocess.run([sys.executable, "-m", "black", "src/", "tests/", "app.py"])


def setup():
    """Setup environment"""
    print("⚙️ Setting up environment...")
    print("=" * 50)
    
    # Create necessary directories
    directories = ["logs", "data", "output", "config"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    # Install requirements
    print("\n📦 Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\n✅ Setup completed!")
    print("\nNext steps:")
    print("1. Copy your Google Sheets credentials to config/credentials.json")
    print("2. Configure .streamlit/secrets.toml")
    print("3. Run: python run.py")


def main():
    parser = argparse.ArgumentParser(
        description="WSA Fulfillment Pro - Run Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py              # Run the application
  python run.py --test       # Run unit tests
  python run.py --setup      # Setup environment
  python run.py --lint       # Run code linter
  python run.py --format     # Format code
        """
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run unit tests"
    )
    
    parser.add_argument(
        "--lint", "-l",
        action="store_true",
        help="Run code linter"
    )
    
    parser.add_argument(
        "--format", "-f",
        action="store_true",
        help="Format code with black"
    )
    
    parser.add_argument(
        "--setup", "-s",
        action="store_true",
        help="Setup environment"
    )
    
    args = parser.parse_args()
    
    if args.test:
        run_tests()
    elif args.lint:
        run_linter()
    elif args.format:
        format_code()
    elif args.setup:
        setup()
    else:
        run_app()


if __name__ == "__main__":
    main()
