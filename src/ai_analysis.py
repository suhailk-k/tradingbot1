"""
Google Gemini AI integration for enhanced market analysis.
"""

import asyncio
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime
import json

from config import config

logger = logging.getLogger(__name__)

class GeminiAI:
    """Google Gemini AI integration for trading analysis"""
    
    def __init__(self):
        """Initialize Gemini AI client"""
        try:
            genai.configure(api_key=config.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            raise
    
    async def analyze_market_sentiment(self, symbol: str, price_data: Dict, 
                                     technical_indicators: Dict) -> Dict:
        """Analyze market sentiment using AI"""
        try:
            prompt = self._create_market_analysis_prompt(symbol, price_data, technical_indicators)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            analysis = self._parse_ai_response(response.text)
            
            logger.info(f"AI market analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI market analysis: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0,
                'analysis': 'AI analysis unavailable',
                'recommendations': [],
                'risk_factors': []
            }
    
    async def validate_trading_signal(self, signal_data: Dict, market_context: Dict) -> Dict:
        """Validate trading signal using AI analysis"""
        try:
            prompt = self._create_signal_validation_prompt(signal_data, market_context)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            validation = self._parse_signal_validation(response.text)
            
            logger.info("AI signal validation completed")
            return validation
            
        except Exception as e:
            logger.error(f"Error in AI signal validation: {e}")
            return {
                'valid': True,
                'confidence': 50,
                'reasoning': 'AI validation unavailable',
                'adjustments': []
            }
    
    async def analyze_risk_factors(self, position_data: Dict, market_data: Dict) -> Dict:
        """Analyze risk factors using AI"""
        try:
            prompt = self._create_risk_analysis_prompt(position_data, market_data)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            risk_analysis = self._parse_risk_analysis(response.text)
            
            logger.info("AI risk analysis completed")
            return risk_analysis
            
        except Exception as e:
            logger.error(f"Error in AI risk analysis: {e}")
            return {
                'risk_level': 'medium',
                'risk_factors': [],
                'recommendations': [],
                'position_adjustments': []
            }
    
    async def generate_trade_commentary(self, trade_data: Dict, performance: Dict) -> str:
        """Generate AI commentary on trade performance"""
        try:
            prompt = f"""
            Analyze this trading performance and provide insights:
            
            Trade Data: {json.dumps(trade_data, indent=2)}
            Performance Metrics: {json.dumps(performance, indent=2)}
            
            Please provide:
            1. Trade execution analysis
            2. Performance insights
            3. Areas for improvement
            4. Market lessons learned
            
            Keep the response concise and actionable.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating trade commentary: {e}")
            return "AI commentary unavailable"
    
    def _create_market_analysis_prompt(self, symbol: str, price_data: Dict, 
                                     technical_indicators: Dict) -> str:
        """Create prompt for market analysis"""
        return f"""
        As an expert crypto futures trader, analyze the current market conditions for {symbol}:
        
        Current Price Data:
        - Price: ${price_data.get('price', 'N/A')}
        - 24h Change: {price_data.get('change_24h', 'N/A')}%
        - Volume: {price_data.get('volume', 'N/A')}
        
        Technical Indicators:
        - EMA Fast: {technical_indicators.get('ema_fast', 'N/A')}
        - EMA Slow: {technical_indicators.get('ema_slow', 'N/A')}
        - RSI: {technical_indicators.get('rsi', 'N/A')}
        - ADX: {technical_indicators.get('adx', 'N/A')}
        - MACD: {technical_indicators.get('macd', 'N/A')}
        - Volume Ratio: {technical_indicators.get('volume_ratio', 'N/A')}
        
        Please provide analysis in this JSON format:
        {{
            "sentiment": "bullish|bearish|neutral",
            "confidence": 0-100,
            "analysis": "detailed market analysis",
            "key_levels": {{
                "support": price_level,
                "resistance": price_level
            }},
            "recommendations": ["actionable recommendations"],
            "risk_factors": ["potential risks"],
            "time_horizon": "short|medium|long"
        }}
        
        Consider current crypto market trends, Bitcoin dominance, and overall market sentiment.
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
