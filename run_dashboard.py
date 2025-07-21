#!/usr/bin/env python3
"""
Launch the Streamlit web dashboard for trading bot management
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dashboard import TradingDashboard

def main():
    """Main dashboard entry point"""
    try:
        dashboard = TradingDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

if __name__ == "__main__":
    main()
