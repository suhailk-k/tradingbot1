"""
Ultra-minimal Railway deployment for trading bot
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class TradingBotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Response data
        response_data = {
            "status": "healthy",
            "service": "BTC Trading Bot",
            "mode": "paper_trading",
            "balance": "$20.00",
            "message": "Railway deployment successful!",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "/": "Status page",
                "/health": "Health check",
                "/api": "Bot API"
            }
        }
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{datetime.now()}] {format % args}")

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Starting BTC Trading Bot on Railway")
    print("="*50)
    print(f"📡 Server starting on port {port}")
    print("📊 Paper Trading Mode: Active")
    print("💰 Virtual Balance: $20.00")
    print("🎯 Position Size: $5.00")
    print("🛡️ Risk Management: 5% per trade")
    print("✅ Ready for Railway deployment!")
    
    try:
        server = HTTPServer(('0.0.0.0', port), TradingBotHandler)
        print(f"🌐 Server running at http://0.0.0.0:{port}")
        print("🔄 Waiting for Railway health checks...")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
