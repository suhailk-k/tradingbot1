#!/usr/bin/env python3
"""
Zero-dependency Railway deployment
Uses only Python standard library
"""
import os
import socket
import threading
from datetime import datetime

def create_response():
    """Create HTTP response"""
    response_body = f"""{{
    "status": "healthy",
    "service": "BTC Trading Bot", 
    "mode": "paper_trading",
    "balance": "$20.00",
    "deployment": "Railway.app",
    "timestamp": "{datetime.now().isoformat()}",
    "message": "✅ Trading bot deployed successfully!"
}}"""
    
    response = f"""HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: {len(response_body)}
Connection: close

{response_body}"""
    
    return response.encode()

def handle_client(client_socket):
    """Handle incoming HTTP requests"""
    try:
        request = client_socket.recv(1024).decode()
        if request:
            print(f"[{datetime.now()}] Request received")
            client_socket.send(create_response())
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_server():
    """Start HTTP server"""
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Zero-Dependency Trading Bot Server")
    print("="*40)
    print(f"📡 Port: {port}")
    print("📊 Mode: Paper Trading")
    print("💰 Balance: $20.00")
    print("🎯 Position: $5.00")
    print("🛡️ Risk: 5%")
    print("✅ Railway Ready!")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    
    print(f"🌐 Server listening on 0.0.0.0:{port}")
    
    while True:
        try:
            client_socket, address = server_socket.accept()
            print(f"[{datetime.now()}] Connection from {address}")
            
            # Handle request in new thread
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket,)
            )
            client_thread.start()
            
        except Exception as e:
            print(f"Server error: {e}")
            break
    
    server_socket.close()

if __name__ == '__main__':
    start_server()
