#!/usr/bin/env python3
"""
Quick start script for the trading bot
Sets up everything and launches the dashboard
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Print welcome banner"""
    print("""
🤖 CRYPTO TRADING BOT - QUICK START
═══════════════════════════════════════════════════════════════
Enterprise-level Bitcoin/USD futures trading bot with AI
Powered by Google Gemini AI + Binance + Advanced Technical Analysis
═══════════════════════════════════════════════════════════════
    """)

def run_setup():
    """Run the setup process"""
    print("🚀 Running setup...")
    try:
        subprocess.run([sys.executable, "setup.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Setup failed")
        return False

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    try:
        subprocess.run([sys.executable, "test_bot.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        return False

def check_env_file():
    """Check if .env file is configured"""
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found!")
        print("Please copy .env.example to .env and configure your API keys:")
        print("cp .env.example .env")
        return False
    
    # Basic check for API keys
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_binance_api_key_here' in content or 'your_gemini_api_key_here' in content:
            print("\n⚠️  Please configure your API keys in the .env file!")
            print("Edit .env and replace the placeholder values with your real API keys.")
            return False
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n🖥️  Launching web dashboard...")
    print("Dashboard will open in your browser at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "run_dashboard.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thank you for using the trading bot!")

def show_menu():
    """Show main menu"""
    print("\n📋 What would you like to do?")
    print("1. 🖥️  Launch Web Dashboard")
    print("2. 📝 Run Paper Trading")
    print("3. 🔄 Run Backtesting")
    print("4. 🧪 Run Tests")
    print("5. 📚 View Documentation")
    print("6. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            launch_dashboard()
            break
        elif choice == '2':
            print("\n📝 Starting paper trading...")
            subprocess.run([sys.executable, "run_paper_trading.py"])
            break
        elif choice == '3':
            print("\n🔄 Starting backtesting...")
            subprocess.run([sys.executable, "run_backtest.py"])
            break
        elif choice == '4':
            run_tests()
            break
        elif choice == '5':
            print("\n📚 Opening README.md...")
            if os.name == 'nt':  # Windows
                os.startfile('README.md')
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', 'README.md'] if sys.platform == 'darwin' else ['xdg-open', 'README.md'])
            break
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def main():
    """Main quick start function"""
    print_banner()
    
    # Check if setup has been run
    if not os.path.exists('logs') or not os.path.exists('.env.example'):
        print("🔧 First time setup required...")
        if not run_setup():
            print("❌ Setup failed. Please run 'python setup.py' manually.")
            return
    
    # Check environment configuration
    if not check_env_file():
        print("\n📝 Please configure your .env file before proceeding.")
        print("You can still run the setup and tests without API keys.")
        
        proceed = input("\nProceed anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            print("👋 Come back after configuring your API keys!")
            return
    
    # Run tests to verify everything works
    print("\n🧪 Verifying installation...")
    if not run_tests():
        print("⚠️  Some tests failed, but you can still proceed.")
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            return
    
    print("\n✅ Everything looks good!")
    
    # Show main menu
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please run 'python setup.py' first or check the README.md for help.")
