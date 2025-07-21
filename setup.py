#!/usr/bin/env python3
"""
Setup script for the trading bot
Installs dependencies and configures the environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🤖 Crypto Trading Bot Setup")
    print("="*50)
    print("This script will set up your trading bot environment")
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Set up environment configuration"""
    print("\n⚙️ Setting up environment...")
    
    # Copy example env file if .env doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from example")
            print("⚠️  Please edit .env file with your API keys before running the bot")
        else:
            print("❌ .env.example file not found")
            sys.exit(1)
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'logs',
        'data',
        'backtest_results'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def setup_database():
    """Initialize the database"""
    try:
        import sys
        import os
        
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from src.database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database setup completed")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    return True

def display_next_steps():
    """Display next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next Steps:")
    print("1. Edit the .env file with your API keys:")
    print("   - BINANCE_API_KEY=your_binance_api_key")
    print("   - BINANCE_SECRET_KEY=your_binance_secret_key")
    print("   - GEMINI_API_KEY=your_gemini_api_key")
    print()
    print("2. Choose how to run the bot:")
    print("   📊 Web Dashboard:    python run_dashboard.py")
    print("   📝 Paper Trading:    python run_paper_trading.py")
    print("   🔄 Backtesting:      python run_backtest.py")
    print("   💰 Live Trading:     python run_live_trading.py --confirmed")
    print()
    print("⚠️  IMPORTANT: Always test with paper trading first!")
    print("⚠️  Never run live trading without thorough testing!")
    print()
    print("📚 Documentation and examples are in the README.md file")

def main():
    """Main setup function"""
    print_header()
    
    try:
        check_python_version()
        install_dependencies()
        setup_environment()
        create_directories()
        setup_database()
        display_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
