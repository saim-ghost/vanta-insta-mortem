import httpx
import json
from config import Config
from typing import List, Dict, Any

class MistralClient:
    def __init__(self):
        self.api_key = Config.MISTRAL_API_KEY
        self.api_url = Config.MISTRAL_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "mistral-tiny") -> Dict[str, Any]:
        """Send a chat completion request to Mistral API"""
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json=data,
                headers=self.headers,
                timeout=30.0
            )
            return response.json()
    
    async def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """Analyze a transcript and extract insights"""
        prompt = f"""
        Analyze this transcript and provide detailed insights in JSON format:
        
        {transcript}
        
        Return a JSON object with the following structure:
        {{
            "topics": ["topic1", "topic2", ...],
            "concepts": ["concept1", "concept2", ...],
            "key_points": ["point1", "point2", ...],
            "sentiment": "positive/negative/neutral",
            "summary": "brief summary",
            "actionable_takeaways": ["takeaway1", "takeaway2", ...]
        }}
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages)
        
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            return json.loads(content)
        except:
            return {"error": "Failed to parse response"}
    
    async def analyze_image_description(self, description: str) -> Dict[str, Any]:
        """Analyze image description and extract visual insights"""
        prompt = f"""
        Analyze this image description and provide visual insights in JSON format:
        
        {description}
        
        Return a JSON object with the following structure:
        {{
            "visual_elements": ["element1", "element2", ...],
            "colors": ["color1", "color2", ...],
            "design_style": "style description",
            "brand_elements": ["element1", "element2", ...],
            "composition": "composition analysis",
            "aesthetic_qualities": ["quality1", "quality2", ...]
        }}
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages)
        
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            return json.loads(content)
        except:
            return {"error": "Failed to parse response"} 