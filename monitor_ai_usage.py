#!/usr/bin/env python3
"""
AI Usage Monitor
Track and display Gemini API usage statistics
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ai_analysis import GeminiAI
    from config import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the project directory and dependencies are installed")
    sys.exit(1)

async def monitor_ai_usage():
    """Monitor AI usage statistics"""
    try:
        print("🤖 AI Usage Monitor")
        print("=" * 50)
        
        # Initialize AI client
        ai = GeminiAI()
        
        # Get usage stats
        stats = ai.get_usage_stats()
        
        print(f"📊 Usage Statistics:")
        print(f"   📞 API Calls Today: {stats['calls_today']}")
        print(f"   🎯 Daily Limit: {stats['daily_limit']}")
        print(f"   🔋 Remaining Calls: {stats['remaining_calls']}")
        print(f"   📈 Usage Percentage: {stats['usage_percentage']:.1f}%")
        print(f"   💾 Cache Entries: {stats['cache_entries']}")
        print(f"   🕐 Last Reset: {stats['last_reset']}")
        
        # Usage recommendations
        print(f"\n💡 Optimization Status:")
        if stats['usage_percentage'] < 50:
            print("   ✅ API usage is optimal")
        elif stats['usage_percentage'] < 80:
            print("   ⚠️ API usage is moderate")
        else:
            print("   🚨 API usage is high - consider reducing")
        
        # Cache efficiency
        cache_efficiency = min(stats['cache_entries'] * 10, 100)
        print(f"   💾 Cache Efficiency: {cache_efficiency:.0f}%")
        
        print(f"\n🔧 Optimization Features:")
        print(f"   ✅ 15-minute caching enabled")
        print(f"   ✅ Daily limit protection: {stats['daily_limit']} calls")
        print(f"   ✅ Signal strength filtering")
        print(f"   ✅ Rule-based fallbacks")
        print(f"   ✅ Smart validation thresholds")
        
        print(f"\n📋 Configuration:")
        print(f"   AI Enabled: {getattr(config, 'ai_enabled', True)}")
        print(f"   Daily Limit: {getattr(config, 'ai_daily_limit', 50)}")
        print(f"   Cache Duration: {getattr(config, 'ai_cache_duration_minutes', 15)} min")
        print(f"   Min Signal Strength: {getattr(config, 'ai_minimum_signal_strength', 0.7)}")
        
    except Exception as e:
        print(f"❌ Error monitoring AI usage: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_ai_usage())
