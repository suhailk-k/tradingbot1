#!/usr/bin/env python3
"""
Render.com optimized trading bot runner
Handles Render-specific environment and configurations
"""

import os
import sys
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_render_environment():
    """Configure environment variables for Render deployment"""
    os.environ['IS_RENDER'] = 'true'
    os.environ['TRADING_MODE'] = 'paper'
    os.environ['MAX_POSITION_SIZE'] = '3'
    os.environ['MAX_TRADES_PER_DAY'] = '2'
    
    logger.info("🎨 Render environment configured")
    logger.info(f"Trading Mode: {os.environ.get('TRADING_MODE', 'unknown')}")
    logger.info(f"Max Position Size: ${os.environ.get('MAX_POSITION_SIZE', 'unknown')}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['ccxt', 'pandas', 'numpy', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} - Missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.info("Installing missing packages...")
        os.system(f"pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def start_trading_bot():
    """Start the main trading bot"""
    try:
        # Import the main bot module
        logger.info("🤖 Starting trading bot...")
        
        # Try to import and run the main bot
        try:
            from run_trading_bot import main
            logger.info("✅ Main bot module imported successfully")
            main()
        except ImportError as e:
            logger.error(f"❌ Could not import main bot: {e}")
            # Fallback to simple heartbeat
            run_simple_heartbeat()
            
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        # Keep the service alive with heartbeat
        run_simple_heartbeat()

def run_simple_heartbeat():
    """Run a simple heartbeat to keep Render service alive"""
    logger.info("💓 Starting heartbeat mode...")
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"💓 Heartbeat - {current_time} - Render service alive")
            
            # Add some basic system info
            logger.info(f"📊 Python: {sys.version}")
            logger.info(f"📁 Working Dir: {os.getcwd()}")
            
            time.sleep(300)  # 5 minutes between heartbeats
            
        except KeyboardInterrupt:
            logger.info("🛑 Heartbeat stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Heartbeat error: {e}")
            time.sleep(60)  # Wait 1 minute before retry

def main():
    """Main entry point for Render deployment"""
    logger.info("🚀 Starting Render trading bot deployment...")
    logger.info(f"📅 Deployment time: {datetime.now()}")
    
    # Setup environment
    setup_render_environment()
    
    # Check dependencies
    if not check_dependencies():
        logger.warning("⚠️ Some dependencies missing, but continuing...")
    
    # Start the bot
    start_trading_bot()

if __name__ == "__main__":
    main()
