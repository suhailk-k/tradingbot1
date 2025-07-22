"""
Google Gemini AI integration for enhanced market analysis.
OPTIMIZED VERSION - Reduced API calls for cost efficiency
"""

import asyncio
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime, timedelta
import json

from config import config

logger = logging.getLogger(__name__)

class GeminiAI:
    """Google Gemini AI integration for trading analysis - Optimized for reduced API usage"""
    
    def __init__(self):
        """Initialize Gemini AI client with caching"""
        try:
            genai.configure(api_key=config.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Cache for reducing API calls
            self.analysis_cache = {}
            self.cache_duration = timedelta(minutes=int(getattr(config, 'ai_cache_duration', 600)) // 60)
            self.call_count = 0
            self.daily_limit = int(getattr(config, 'ai_daily_limit', 50))
            self.analysis_interval = int(getattr(config, 'ai_analysis_interval', 300))
            self.last_reset = datetime.now().date()
            self.last_analysis_time = {}
            
            logger.info(f"✅ Gemini AI initialized - Daily limit: {self.daily_limit}, Cache: {self.cache_duration}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            raise
    
    def _check_daily_limit(self) -> bool:
        """Check if daily API limit is reached"""
        current_date = datetime.now().date()
        
        # Reset counter if new day
        if current_date > self.last_reset:
            self.call_count = 0
            self.last_reset = current_date
            
        return self.call_count < self.daily_limit
    
    def _get_cache_key(self, symbol: str, analysis_type: str) -> str:
        """Generate cache key for analysis"""
        timestamp = datetime.now().replace(minute=datetime.now().minute // 15 * 15, second=0, microsecond=0)
        return f"{symbol}_{analysis_type}_{timestamp}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached analysis is still valid"""
        if cache_key not in self.analysis_cache:
            return False
            
        cached_time = self.analysis_cache[cache_key]['timestamp']
        return datetime.now() - cached_time < self.cache_duration

    def _should_analyze_now(self, symbol: str) -> bool:
        """Check if enough time has passed since last analysis"""
        last_time = self.last_analysis_time.get(symbol, datetime.min)
        time_since_last = (datetime.now() - last_time).total_seconds()
        return time_since_last >= self.analysis_interval

    def _calculate_signal_strength(self, indicators: Dict) -> float:
        """Calculate signal strength to determine if AI analysis is needed"""
        try:
            rsi = indicators.get('rsi', 50)
            adx = indicators.get('adx', 0)
            ema_diff = abs(indicators.get('ema_fast', 0) - indicators.get('ema_slow', 0))
            
            # Normalize indicators to 0-1 scale
            rsi_strength = abs(rsi - 50) / 50  # Higher when RSI is extreme
            adx_strength = min(adx / 50, 1.0)  # Higher when trend is strong
            ema_strength = min(ema_diff / 100, 1.0)  # Simplified EMA strength
            
            return (rsi_strength + adx_strength + ema_strength) / 3
        except:
            return 0.5

    def _fallback_analysis(self, indicators: Dict) -> Dict:
        """Provide simple analysis without AI when limits are reached"""
        rsi = indicators.get('rsi', 50)
        adx = indicators.get('adx', 0)
        
        if rsi > 70 and adx > 25:
            sentiment = "bearish"
            confidence = 0.6
            reasoning = "Technical indicators suggest overbought conditions with strong trend"
        elif rsi < 30 and adx > 25:
            sentiment = "bullish"
            confidence = 0.6
            reasoning = "Technical indicators suggest oversold conditions with strong trend"
        else:
            sentiment = "neutral"
            confidence = 0.4
            reasoning = "Mixed technical signals, no clear direction"
            
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'reasoning': reasoning,
            'key_factors': ['Technical analysis only'],
            'ai_used': False
        }

    async def analyze_market_sentiment(self, symbol: str, price_data: Dict, 
                                     technical_indicators: Dict) -> Dict:
        """Analyze market sentiment using AI with optimization and limits"""
        
        # Check if enough time has passed since last analysis
        if not self._should_analyze_now(symbol):
            logger.debug(f"Skipping AI analysis for {symbol} - interval not reached")
            return self._fallback_analysis(technical_indicators)
        
        # Check cache first
        cache_key = self._get_cache_key(symbol, "sentiment")
        if self._is_cache_valid(cache_key):
            logger.info(f"📋 Using cached AI analysis for {symbol}")
            return self.analysis_cache[cache_key]['data']
        
        # Check daily limit
        if not self._check_daily_limit():
            logger.warning(f"⚠️ Daily AI limit reached ({self.daily_limit}), using fallback")
            return self._fallback_analysis(technical_indicators)
        
        # Only call AI for strong signals (save API calls)
        signal_strength = self._calculate_signal_strength(technical_indicators)
        if signal_strength < 0.6:  # Only use AI for moderate+ signals
            logger.debug(f"Signal strength {signal_strength:.2f} too low, using fallback")
            return self._fallback_analysis(technical_indicators)
        
        try:
            prompt = self._create_optimized_prompt(symbol, price_data, technical_indicators)
            
            logger.info(f"🤖 Calling Gemini AI for {symbol} (call #{self.call_count + 1}/{self.daily_limit})")
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            analysis = self._parse_ai_response(response.text)
            analysis['ai_used'] = True
            
            # Cache the result
            self.analysis_cache[cache_key] = {
                'data': analysis,
                'timestamp': datetime.now()
            }
            
            self.call_count += 1
            self.last_analysis_time[symbol] = datetime.now()
            
            logger.info(f"✅ AI analysis completed for {symbol} - {analysis['sentiment']} ({analysis['confidence']:.1f})")
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed for {symbol}: {e}")
            return self._fallback_analysis(technical_indicators)
            logger.info(f"AI analysis completed for {symbol} (API calls today: {self.call_count})")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI market analysis: {e}")
            return self._fallback_analysis(technical_indicators)
    
    def _calculate_signal_strength(self, indicators: Dict) -> float:
        """Calculate overall signal strength to determine if AI analysis is needed"""
        try:
            strength = 0.0
            
            # RSI contribution
            rsi = indicators.get('rsi', 50)
            if rsi < 30 or rsi > 70:
                strength += 0.3
            
            # ADX contribution  
            adx = indicators.get('adx', 20)
            if adx > 25:
                strength += 0.3
            
            # EMA alignment
            ema_fast = indicators.get('ema_fast', 0)
            ema_slow = indicators.get('ema_slow', 0)
            if abs(ema_fast - ema_slow) / ema_slow > 0.01:  # 1% difference
                strength += 0.4
                
            return min(strength, 1.0)
            
        except Exception:
            return 0.5  # Default moderate strength
    
    def _fallback_analysis(self, technical_indicators: Dict) -> Dict:
        """Provide fallback analysis when AI is not used"""
        try:
            rsi = technical_indicators.get('rsi', 50)
            adx = technical_indicators.get('adx', 20)
            ema_fast = technical_indicators.get('ema_fast', 0)
            ema_slow = technical_indicators.get('ema_slow', 0)
            
            # Simple rule-based analysis
            if rsi > 70:
                sentiment = 'bearish'
                confidence = min(70 + (rsi - 70), 85)
            elif rsi < 30:
                sentiment = 'bullish'  
                confidence = min(70 + (30 - rsi), 85)
            elif ema_fast > ema_slow and adx > 25:
                sentiment = 'bullish'
                confidence = 60
            elif ema_fast < ema_slow and adx > 25:
                sentiment = 'bearish'
                confidence = 60
            else:
                sentiment = 'neutral'
                confidence = 40
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'analysis': f'Technical analysis: RSI={rsi:.1f}, ADX={adx:.1f}',
                'recommendations': [f'Monitor {sentiment} trend'],
                'risk_factors': ['Limited AI analysis due to optimization'],
                'source': 'fallback_technical'
            }
            
        except Exception:
            return {
                'sentiment': 'neutral',
                'confidence': 30,
                'analysis': 'Basic fallback analysis',
                'recommendations': ['Use caution'],
                'risk_factors': ['Limited analysis available'],
                'source': 'fallback_basic'
            }
    
    async def validate_trading_signal(self, signal_data: Dict, market_context: Dict) -> Dict:
        """Validate trading signal - ONLY for high-confidence signals to save API calls"""
        
        # Only validate signals with high confidence to save API calls
        signal_confidence = signal_data.get('confidence', 0)
        if signal_confidence < 80:  # Only validate very confident signals
            return {
                'valid': True,
                'confidence': signal_confidence,
                'reasoning': 'Signal validation skipped for optimization',
                'adjustments': [],
                'source': 'skipped_validation'
            }
        
        # Check daily limit
        if not self._check_daily_limit():
            return {
                'valid': True,
                'confidence': 70,
                'reasoning': 'Daily API limit reached',
                'adjustments': [],
                'source': 'limit_reached'
            }
        
        try:
            prompt = self._create_signal_validation_prompt(signal_data, market_context)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            validation = self._parse_signal_validation(response.text)
            self.call_count += 1
            
            logger.info(f"AI signal validation completed (API calls today: {self.call_count})")
            return validation
            
        except Exception as e:
            logger.error(f"Error in AI signal validation: {e}")
            return {
                'valid': True,
                'confidence': 60,
                'reasoning': 'AI validation unavailable',
                'adjustments': [],
                'source': 'error_fallback'
            }
    
    async def analyze_risk_factors(self, position_data: Dict, market_data: Dict) -> Dict:
        """Analyze risk factors - DISABLED to save API calls, using rule-based analysis"""
        
        # Skip AI analysis for risk factors, use rule-based approach
        logger.info("Using rule-based risk analysis to save API calls")
        
        try:
            # Rule-based risk analysis
            risk_level = 'low'
            risk_factors = []
            recommendations = []
            
            # Check position size
            position_size = position_data.get('size', 0)
            account_balance = position_data.get('balance', 10000)
            
            if position_size > account_balance * 0.05:  # More than 5% of account
                risk_level = 'high'
                risk_factors.append('Large position size relative to account')
                recommendations.append('Consider reducing position size')
            
            # Check market volatility
            volatility = market_data.get('atr', 0)
            if volatility > 100:  # High volatility
                risk_level = 'medium' if risk_level == 'low' else 'high'
                risk_factors.append('High market volatility detected')
                recommendations.append('Use tighter stop losses')
            
            return {
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'position_adjustments': [],
                'source': 'rule_based_analysis'
            }
            
        except Exception as e:
            logger.error(f"Error in rule-based risk analysis: {e}")
            return {
                'risk_level': 'medium',
                'risk_factors': ['Analysis error'],
                'recommendations': ['Use standard risk management'],
                'position_adjustments': [],
                'source': 'error_fallback'
            }
    
    async def generate_trade_commentary(self, trade_data: Dict, performance: Dict) -> str:
        """Generate AI commentary - DISABLED to save API calls"""
        # Disable trade commentary to save API calls
        logger.info("Trade commentary disabled to save API calls")
        
        try:
            # Generate simple rule-based commentary
            pnl = performance.get('pnl', 0)
            if pnl > 0:
                return f"Profitable trade: +${pnl:.2f}. Strategy performed well."
            elif pnl < 0:
                return f"Loss trade: -${abs(pnl):.2f}. Review risk management."
            else:
                return "Neutral trade outcome. Monitor for improvements."
                
        except Exception:
            return "Trade completed. Analysis optimized for efficiency."
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'calls_today': self.call_count,
            'daily_limit': self.daily_limit,
            'remaining_calls': max(0, self.daily_limit - self.call_count),
            'usage_percentage': (self.call_count / self.daily_limit) * 100,
            'cache_entries': len(self.analysis_cache),
            'last_reset': self.last_reset.isoformat()
        }
    
    def _create_optimized_prompt(self, symbol: str, price_data: Dict, 
                               technical_indicators: Dict) -> str:
        """Create shorter, more efficient prompt for market analysis"""
        return f"""
        Quick crypto analysis for {symbol}:
        
        Price: ${price_data.get('price', 'N/A')}, Change: {price_data.get('change_24h', 'N/A')}%
        RSI: {technical_indicators.get('rsi', 'N/A')}, ADX: {technical_indicators.get('adx', 'N/A')}
        EMA: {technical_indicators.get('ema_fast', 'N/A')}/{technical_indicators.get('ema_slow', 'N/A')}
        
        JSON response only:
        {{
            "sentiment": "bullish/bearish/neutral",
            "confidence": 0-100,
            "analysis": "brief reason",
            "recommendations": ["max 2 items"]
        }}
        """
    
    def _create_signal_validation_prompt(self, signal_data: Dict, market_context: Dict) -> str:
        """Create prompt for signal validation"""
        return f"""
        As a professional trading analyst, validate this trading signal:
        
        Signal Details:
        - Direction: {signal_data.get('signal', 'N/A')}
        - Strength: {signal_data.get('strength', 'N/A')}
        - Confidence: {signal_data.get('confidence', 'N/A')}%
        - Reasons: {signal_data.get('reasons', [])}
        
        Market Context:
        - Market Trend: {market_context.get('trend', 'N/A')}
        - Volatility: {market_context.get('volatility', 'N/A')}
        - Volume Profile: {market_context.get('volume_profile', 'N/A')}
        
        Technical Indicators:
        {json.dumps(signal_data.get('indicators', {}), indent=2)}
        
        Please validate in this JSON format:
        {{
            "valid": true/false,
            "confidence": 0-100,
            "reasoning": "detailed validation reasoning",
            "strengths": ["signal strengths"],
            "weaknesses": ["signal weaknesses"],
            "adjustments": ["suggested adjustments"],
            "entry_timing": "immediate|wait|caution"
        }}
        
        Consider confluence of indicators, market structure, and risk/reward ratio.
        """
    
    def _create_risk_analysis_prompt(self, position_data: Dict, market_data: Dict) -> str:
        """Create prompt for risk analysis"""
        return f"""
        Analyze the risk factors for this trading position:
        
        Position Details:
        - Symbol: {position_data.get('symbol', 'N/A')}
        - Size: {position_data.get('size', 'N/A')}
        - Entry Price: {position_data.get('entry_price', 'N/A')}
        - Current Price: {position_data.get('current_price', 'N/A')}
        - P&L: {position_data.get('pnl', 'N/A')}
        - Duration: {position_data.get('duration', 'N/A')}
        
        Market Conditions:
        - Volatility: {market_data.get('volatility', 'N/A')}
        - Trend Strength: {market_data.get('trend_strength', 'N/A')}
        - Volume: {market_data.get('volume', 'N/A')}
        - Market Phase: {market_data.get('market_phase', 'N/A')}
        
        Provide risk analysis in JSON format:
        {{
            "risk_level": "low|medium|high|extreme",
            "risk_score": 0-100,
            "risk_factors": ["identified risks"],
            "recommendations": ["risk management actions"],
            "position_adjustments": ["suggested adjustments"],
            "exit_signals": ["conditions to consider exit"],
            "monitoring_points": ["key levels to watch"]
        }}
        
        Focus on position sizing, market volatility, and correlation risks.
        """
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response for market analysis"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback parsing
            return {
                'sentiment': 'neutral',
                'confidence': 50,
                'analysis': response_text,
                'recommendations': [],
                'risk_factors': []
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0,
                'analysis': response_text,
                'recommendations': [],
                'risk_factors': []
            }
    
    def _parse_signal_validation(self, response_text: str) -> Dict:
        """Parse AI response for signal validation"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                'valid': True,
                'confidence': 50,
                'reasoning': response_text,
                'adjustments': []
            }
            
        except Exception as e:
            logger.error(f"Error parsing signal validation: {e}")
            return {
                'valid': True,
                'confidence': 50,
                'reasoning': response_text,
                'adjustments': []
            }
    
    def _parse_risk_analysis(self, response_text: str) -> Dict:
        """Parse AI response for risk analysis"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                'risk_level': 'medium',
                'risk_factors': [],
                'recommendations': [],
                'position_adjustments': []
            }
            
        except Exception as e:
            logger.error(f"Error parsing risk analysis: {e}")
            return {
                'risk_level': 'medium',
                'risk_factors': [],
                'recommendations': [],
                'position_adjustments': []
            }
