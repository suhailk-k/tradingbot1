"""
Ultra-simple Railway deployment
"""
import os
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 BTC Trading Bot - Railway Deployment",
        "status": "healthy",
        "mode": "paper_trading",
        "balance": "$20.00",
        "features": [
            "AI-powered BTC/USDT trading",
            "Paper trading mode",
            "Risk management",
            "Real-time monitoring"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "trading-bot"
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        "bot_running": True,
        "trading_pair": "BTCUSDT",
        "position_size": "$5",
        "risk_per_trade": "5%",
        "max_daily_trades": 3,
        "current_balance": "$20.00"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting Trading Bot Web Service on port {port}")
    print("📊 Paper Trading Mode Active")
    print("💰 Virtual Balance: $20.00")
    app.run(host='0.0.0.0', port=port, debug=False)
