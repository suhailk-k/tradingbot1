# 🤖 Enterprise-Level Crypto Trading Bot

A sophisticated Bitcoin/USD futures trading bot powered by Google Gemini AI and integrated with Binance. This enterprise-grade solution features advanced technical analysis, AI-driven market insights, comprehensive backtesting, and multiple trading modes.

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/suhailk-k/tradingbot1)

**One-Click Deployment:** Click the button above to deploy instantly to Railway.app

## ✨ Features

### 🎯 Core Trading Features
- **Multi-Currency Support**: Trade BTC/USD, ETH/USD, and other major crypto pairs
- **Advanced Strategy**: EMA + ADX + RSI with AI-powered signal validation
- **Multiple Trading Modes**: Paper trading, live trading, and comprehensive backtesting
- **AI Integration**: Google Gemini API for market sentiment analysis and signal validation
- **Risk Management**: Sophisticated position sizing, stop-loss, and take-profit mechanisms

### 📊 Analytics & Monitoring
- **Real-time Dashboard**: Streamlit-based web interface for monitoring and control
- **Performance Analytics**: Detailed trade analysis, win rates, and risk metrics
- **Backtesting Engine**: Historical strategy validation with multiple timeframes
- **Portfolio Tracking**: Real-time balance, P&L, and position monitoring

### 🛡️ Enterprise-Level Security
- **Paper Trading Mode**: Safe testing environment with virtual funds
- **Multi-layer Confirmations**: Safety checks for live trading activation
- **Comprehensive Logging**: Structured logging for audit trails
- **Error Handling**: Robust error recovery and graceful shutdowns

### 🔧 Technical Excellence
- **Clean Architecture**: Modular, maintainable, and scalable codebase
- **Database Integration**: SQLAlchemy ORM with comprehensive trade tracking
- **Async Operations**: High-performance asynchronous trading operations
- **Configuration Management**: Environment-based configuration system

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd newTrading

# Run the setup script
python setup.py
```

### 2. Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET=True  # Set to False for live trading

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Trading Configuration
DEFAULT_SYMBOL=BTCUSDT
POSITION_SIZE_USD=100
RISK_PER_TRADE_PERCENT=1.5
MAX_TRADES_PER_DAY=3
```

### 3. Testing & Validation

**Always start with backtesting and paper trading:**

```bash
# Run backtesting
python run_backtest.py

# Run paper trading
python run_paper_trading.py

# Launch web dashboard
python run_dashboard.py
```

### 4. Live Trading (Only After Thorough Testing)

```bash
# Live trading requires explicit confirmation
python run_live_trading.py --confirmed
```

## 📊 Strategy Overview

### EMA + ADX + RSI Strategy

The bot uses a sophisticated multi-indicator strategy:

- **EMA (Exponential Moving Average)**: Trend direction identification
  - Fast EMA: 12 periods
  - Slow EMA: 26 periods
  - Signal confirmation with MACD

- **ADX (Average Directional Index)**: Trend strength validation
  - Period: 14
  - Threshold: 25 (strong trend requirement)

- **RSI (Relative Strength Index)**: Momentum analysis
  - Period: 14
  - Overbought: 70, Oversold: 30

- **Volume Confirmation**: Trade validation with volume analysis
- **AI Enhancement**: Google Gemini AI provides additional market sentiment analysis

### Entry Conditions
- **Long Entry**: EMA fast > slow, ADX > 25, RSI not overbought, high volume, AI confirmation
- **Short Entry**: EMA fast < slow, ADX > 25, RSI not oversold, high volume, AI confirmation

### Risk Management
- **Stop Loss**: 2% or 2x ATR (whichever is more conservative)
- **Take Profit**: 3% or 3x ATR (whichever is more conservative)
- **Position Sizing**: Risk-based position calculation
- **Daily Limits**: Maximum 3 trades per day

## 🖥️ Web Dashboard

Launch the comprehensive web dashboard:

```bash
streamlit run run_dashboard.py
```

Features:
- **Portfolio Overview**: Real-time balance, P&L, and performance metrics
- **Live Trading Control**: Start/stop bot, emergency controls, position management
- **Backtesting Interface**: Run and analyze historical performance
- **Analytics Dashboard**: Detailed trade analysis and risk metrics
- **Settings Management**: Configure trading parameters and risk settings

## 📈 Backtesting

Run comprehensive backtests to validate strategy performance:

```bash
python run_backtest.py
```

The backtesting engine provides:
- **Multiple Timeframes**: 15m, 1h, 4h, 1d
- **Historical Data**: Up to several years of data
- **Performance Metrics**: Win rate, profit factor, Sharpe ratio, max drawdown
- **Detailed Reports**: Trade-by-trade analysis with exportable results

Example backtest report:
```
╔══════════════════════════════════════════════════════════╗
║                    BACKTEST REPORT                      ║
╠══════════════════════════════════════════════════════════╣
║ Symbol: BTCUSDT                                         ║
║ Period: 2023-01-01 to 2024-01-01                       ║
║ Timeframe: 15m                                          ║
╠══════════════════════════════════════════════════════════╣
║                    PERFORMANCE                           ║
╠══════════════════════════════════════════════════════════╣
║ Initial Balance:     $10,000.00                        ║
║ Final Balance:       $12,150.00                        ║
║ Total Return:         21.50%                           ║
║ Total P&L:           $2,150.00                         ║
╠══════════════════════════════════════════════════════════╣
║                    TRADE STATISTICS                     ║
╠══════════════════════════════════════════════════════════╣
║ Total Trades:            156                           ║
║ Winning Trades:           97                           ║
║ Losing Trades:            59                           ║
║ Win Rate:              62.18%                          ║
║ Profit Factor:          1.85                           ║
║ Sharpe Ratio:           1.25                           ║
║ Max Drawdown:           8.50%                          ║
╚══════════════════════════════════════════════════════════╝
```

## 🔄 Trading Modes

### 1. Paper Trading (Recommended for beginners)
- **Virtual funds**: No real money at risk
- **Real market data**: Live price feeds and realistic execution
- **Full feature testing**: Test all bot functionality safely
- **Performance tracking**: Complete analytics and reporting

```bash
python run_paper_trading.py
```

### 2. Live Trading (For experienced traders only)
- **Real money**: Actual trades on Binance
- **Safety confirmations**: Multiple confirmation steps
- **Risk controls**: Built-in safeguards and limits
- **Real-time monitoring**: Live performance tracking

```bash
python run_live_trading.py --confirmed
```

### 3. Backtesting (Strategy validation)
- **Historical analysis**: Test on past market data
- **Performance metrics**: Comprehensive strategy evaluation
- **Parameter optimization**: Fine-tune strategy settings
- **Risk assessment**: Understand potential drawdowns

## 🔧 Configuration

### Trading Parameters

Customize the bot's behavior through environment variables:

```bash
# Position and Risk Management
POSITION_SIZE_USD=100              # Base position size
MAX_POSITION_SIZE_USD=500          # Maximum position size
RISK_PER_TRADE_PERCENT=1.5         # Risk per trade as % of balance
MAX_TRADES_PER_DAY=3               # Daily trade limit
STOP_LOSS_PERCENT=2.0              # Stop loss percentage
TAKE_PROFIT_PERCENT=3.0            # Take profit percentage

# Strategy Parameters
DEFAULT_SYMBOL=BTCUSDT             # Primary trading pair
DEFAULT_TIMEFRAME=15m              # Analysis timeframe

# API Configuration
BINANCE_TESTNET=True               # Use testnet for safety
```

### Strategy Customization

Modify strategy parameters in `src/config.py`:

```python
class StrategyConfig:
    # EMA Parameters
    EMA_FAST = 12
    EMA_SLOW = 26
    EMA_SIGNAL = 9
    
    # ADX Parameters
    ADX_PERIOD = 14
    ADX_THRESHOLD = 25
    
    # RSI Parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
```

## 📁 Project Structure

```
newTrading/
├── src/                          # Core source code
│   ├── trading_bot.py           # Main trading bot logic
│   ├── strategy.py              # EMA + ADX + RSI strategy
│   ├── ai_analysis.py           # Google Gemini AI integration
│   ├── binance_interface.py     # Binance API wrapper
│   ├── backtest.py              # Backtesting engine
│   ├── database.py              # Database operations
│   ├── models.py                # Data models and schemas
│   ├── config.py                # Configuration management
│   └── dashboard.py             # Streamlit web interface
├── run_live_trading.py          # Live trading launcher
├── run_paper_trading.py         # Paper trading launcher
├── run_backtest.py              # Backtesting launcher
├── run_dashboard.py             # Web dashboard launcher
├── setup.py                     # Setup and installation script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # This documentation
```

## 🛡️ Risk Management

### Built-in Safety Features

1. **Paper Trading Default**: Bot starts in paper trading mode
2. **Multi-layer Confirmations**: Explicit confirmations required for live trading
3. **Position Limits**: Maximum position sizes and daily trade limits
4. **Stop Losses**: Automatic loss protection
5. **Emergency Stop**: Immediate position closure and bot shutdown

### Best Practices

1. **Always Test First**: Use paper trading and backtesting extensively
2. **Start Small**: Begin with minimal position sizes
3. **Monitor Actively**: Keep an eye on bot performance
4. **Set Limits**: Configure appropriate risk parameters
5. **Understand the Strategy**: Know how the EMA + ADX + RSI strategy works

## 🔑 API Setup

### Binance API
1. Create a Binance account and enable 2FA
2. Generate API keys in your account settings
3. Enable futures trading permissions
4. For testing, use Binance Testnet
5. Never share your API keys

### Google Gemini API
1. Visit Google AI Studio
2. Create a new API key
3. Add the key to your `.env` file
4. The AI analysis enhances trading signals

## 📊 Performance Monitoring

### Key Metrics to Track

- **Win Rate**: Percentage of profitable trades (target: >60%)
- **Profit Factor**: Gross profit / Gross loss (target: >1.5)
- **Sharpe Ratio**: Risk-adjusted returns (target: >1.0)
- **Maximum Drawdown**: Largest peak-to-trough decline (target: <15%)
- **Average Trade Duration**: How long positions are held

### Dashboard Monitoring

The web dashboard provides real-time monitoring:
- Portfolio balance and P&L
- Open positions and recent trades
- Performance charts and analytics
- Risk metrics and warnings
- Bot status and controls

## 🚨 Important Warnings

### ⚠️ Live Trading Risks
- **Real Money**: Live trading uses actual funds
- **Market Volatility**: Crypto markets are highly volatile
- **Technical Risks**: Software bugs or connectivity issues
- **No Guarantees**: Past performance doesn't guarantee future results

### 🛡️ Safety Recommendations
1. **Never risk more than you can afford to lose**
2. **Always test strategies thoroughly before live trading**
3. **Start with small position sizes**
4. **Keep API keys secure and never share them**
5. **Monitor bot performance regularly**
6. **Have emergency stop procedures ready**

## 📞 Support & Troubleshooting

### Common Issues

**Bot won't start:**
- Check API keys in `.env` file
- Verify internet connection
- Ensure all dependencies are installed

**Trades not executing:**
- Check account balance
- Verify trading permissions
- Review daily trade limits

**Backtest errors:**
- Ensure sufficient historical data
- Check date format (YYYY-MM-DD)
- Verify symbol is supported

### Logs and Debugging

Logs are stored in `logs/trading_bot.log` and include:
- Trade executions and reasons
- Strategy signals and analysis
- Error messages and warnings
- Performance metrics

## 📝 License

This project is for educational and research purposes. Use at your own risk. The authors are not responsible for any financial losses.

## 🤝 Contributing

We welcome contributions! Please read the contributing guidelines and submit pull requests for any improvements.

---

**⚠️ DISCLAIMER: This trading bot is for educational purposes. Cryptocurrency trading involves substantial risk of loss. Never trade with money you cannot afford to lose. Past performance is not indicative of future results.**
