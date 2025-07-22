"""
Railway-specific configuration for trading bot
"""
import os

# Railway environment detection
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'

if IS_RAILWAY:
    print("🚂 Railway environment detected - applying safety configurations")
    
    # Force paper trading on Railway for safety
    os.environ['BINANCE_TESTNET'] = 'True'
    os.environ['PAPER_TRADING'] = 'True'
    
    # Optimize for Railway's resources
    os.environ['MAX_TRADES_PER_DAY'] = '2'
    os.environ['POSITION_SIZE_USD'] = '3'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    # Railway-specific settings
    os.environ['RAILWAY_SAFE_MODE'] = 'True'
    
    print("✅ Railway safety configurations applied:")
    print("   - Paper trading: ENFORCED")
    print("   - Max trades: 2/day") 
    print("   - Position size: $3")
    print("   - Testnet only: TRUE")

# Railway deployment constants
RAILWAY_CONFIG = {
    'PAPER_TRADING_ONLY': True,
    'MAX_POSITION_SIZE': 3.0,
    'MAX_DAILY_TRADES': 2,
    'RESTART_ON_ERROR': True,
    'HEARTBEAT_INTERVAL': 60,
    'STATUS_REPORT_INTERVAL': 600,  # 10 minutes
}
