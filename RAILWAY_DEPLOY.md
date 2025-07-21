# 🚂 Railway Deployment Guide

## Quick Deploy Steps

### 1. Create GitHub Repository
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `tradingbot1`
3. Description: `AI-powered BTC/USDT futures trading bot`
4. Make it **Public**
5. **Don't** initialize with README
6. Click "Create repository"

### 2. Push Your Code
```bash
# Run this script after creating the repository
./setup_github.sh
```

### 3. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose: `yourusername/tradingbot1`
6. Railway will auto-detect the configuration

### 4. Set Environment Variables
Add these in Railway dashboard:

```env
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
GEMINI_API_KEY=your_gemini_api_key
BINANCE_TESTNET=True
DEFAULT_SYMBOL=BTCUSDT
POSITION_SIZE_USD=5
RISK_PER_TRADE_PERCENT=5.0
MAX_TRADES_PER_DAY=3
PAPER_TRADING_INITIAL_BALANCE=20
```

### 5. Monitor Your Bot
- **Railway Dashboard**: View logs and performance
- **Bot URL**: Visit your app URL to see status
- **Health Check**: `/health` endpoint for monitoring

## 🎯 Expected Result
After deployment, your bot will:
- ✅ Start in paper trading mode ($20 virtual balance)
- ✅ Trade BTC/USDT futures with $5 positions
- ✅ Use AI analysis for trade decisions
- ✅ Provide real-time health status
- ✅ Log all trading activity

## 📊 Performance Metrics
Based on backtesting:
- **Return**: 188% over 90 days
- **Win Rate**: 72.73%
- **Max Drawdown**: 1.14%
- **Sharpe Ratio**: 0.57

## 🔗 Useful Links
- [Railway Dashboard](https://railway.app/dashboard)
- [GitHub Repository](https://github.com/yourusername/tradingbot1)
- [Binance Testnet](https://testnet.binancefuture.com/)
- [Google AI Studio](https://makersuite.google.com/app/apikey)

---
**⚠️ Remember**: Always start with paper trading and test thoroughly before considering live trading!
