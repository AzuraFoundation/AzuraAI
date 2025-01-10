from typing import Dict, Any, List
import openai
import os
import base64
from io import BytesIO
import json

class OpenAIAnalyzer:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview')

    async def analyze_meme(self, image_data: bytes, text: str = "") -> Dict[str, Any]:
        """
        Get advanced meme analysis using OpenAI's vision model
        
        Args:
            image_data: Raw image bytes
            text: Additional text context (caption, comments, etc.)
            
        Returns:
            Dictionary containing AI insights
        """
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the messages
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert meme analyst specializing in crypto and memecoin trends. 
                    Analyze the meme for:
                    1. Cultural references and symbolism
                    2. Potential impact on crypto markets
                    3. Memetic value and viral potential
                    4. Hidden meanings or subtle jokes
                    5. Related cryptocurrencies or projects
                    Provide detailed but concise analysis."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": f"Analyze this meme. Additional context: {text}"
                        }
                    ]
                }
            ]

            # Get completion from OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            # Parse and structure the response
            analysis = json.loads(response.choices[0].message.content)
            
            # Ensure consistent structure
            structured_analysis = {
                'cultural_references': analysis.get('cultural_references', []),
                'market_impact': {
                    'sentiment': analysis.get('market_impact', {}).get('sentiment', 'neutral'),
                    'strength': analysis.get('market_impact', {}).get('strength', 0.5),
                    'reasoning': analysis.get('market_impact', {}).get('reasoning', '')
                },
                'viral_potential': {
                    'score': analysis.get('viral_potential', {}).get('score', 0.5),
                    'factors': analysis.get('viral_potential', {}).get('factors', [])
                },
                'hidden_meanings': analysis.get('hidden_meanings', []),
                'related_cryptos': analysis.get('related_cryptos', []),
                'additional_insights': analysis.get('additional_insights', '')
            }
            
            return structured_analysis
            
        except Exception as e:
            print(f"Error in OpenAI analysis: {str(e)}")
            return {
                'cultural_references': [],
                'market_impact': {'sentiment': 'neutral', 'strength': 0.5, 'reasoning': ''},
                'viral_potential': {'score': 0.5, 'factors': []},
                'hidden_meanings': [],
                'related_cryptos': [],
                'additional_insights': ''
            }

    async def get_market_prediction(self, meme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get market prediction based on meme analysis
        
        Args:
            meme_data: Dictionary containing meme analysis data
            
        Returns:
            Dictionary containing market predictions
        """
        try:
            # Prepare context for GPT
            context = json.dumps({
                'analysis': meme_data,
                'timestamp': meme_data.get('timestamp', ''),
                'platform': meme_data.get('source', 'unknown'),
                'engagement_metrics': meme_data.get('metrics', {})
            })
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a crypto market analyst specializing in memecoin trends.
                    Based on the meme analysis data, predict:
                    1. Potential market movements
                    2. Trading volume impact
                    3. Social sentiment spread
                    4. Timeline of effects
                    Be specific but cautious with predictions."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this meme data for market predictions: {context}"
                }
            ]

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            prediction = json.loads(response.choices[0].message.content)
            
            return {
                'market_movement': {
                    'direction': prediction.get('market_movement', {}).get('direction', 'neutral'),
                    'confidence': prediction.get('market_movement', {}).get('confidence', 0.5),
                    'timeframe': prediction.get('market_movement', {}).get('timeframe', '24h')
                },
                'volume_impact': {
                    'expected_change': prediction.get('volume_impact', {}).get('expected_change', 0),
                    'affected_coins': prediction.get('volume_impact', {}).get('affected_coins', [])
                },
                'sentiment_spread': {
                    'velocity': prediction.get('sentiment_spread', {}).get('velocity', 0.5),
                    'platforms': prediction.get('sentiment_spread', {}).get('platforms', [])
                },
                'timeline': prediction.get('timeline', []),
                'risk_factors': prediction.get('risk_factors', [])
            }
            
        except Exception as e:
            print(f"Error in market prediction: {str(e)}")
            return {
                'market_movement': {'direction': 'neutral', 'confidence': 0.5, 'timeframe': '24h'},
                'volume_impact': {'expected_change': 0, 'affected_coins': []},
                'sentiment_spread': {'velocity': 0.5, 'platforms': []},
                'timeline': [],
                'risk_factors': []
            } 