"""
routers/chat.py
---------------
AI Chat Assistant — rule-based chatbot for farming advice.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import random

router = APIRouter(tags=["Chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    suggestions: List[str] = []


KNOWLEDGE_BASE = {
    "fertilizer": {
        "keywords": ["fertilizer", "urea", "npk", "dap", "manure", "compost", "nutrient", "feed"],
        "responses": [
            "For most crops, a balanced NPK fertilizer (like 10-26-26 or 20-20-0) works well. Apply based on soil test results.",
            "Organic options include vermicompost (2-3 tonnes/acre), farmyard manure (5-10 tonnes/acre), or neem cake (200 kg/acre).",
            "Urea (46-0-0) is great for nitrogen. Apply 50-60 kg/acre for wheat and 80-100 kg/acre for rice.",
            "Always apply fertilizers after soil testing. Over-application wastes money and harms the environment.",
        ],
        "suggestions": ["Best fertilizer for rice?", "How much NPK for wheat?", "Organic vs chemical fertilizer?"],
    },
    "crop": {
        "keywords": ["crop", "plant", "grow", "sow", "harvest", "season", "variety", "seed"],
        "responses": [
            "Choose crops based on your soil type, climate, and water availability. Kharif crops (June-Oct): Rice, Maize, Cotton. Rabi (Oct-March): Wheat, Potato, Mustard.",
            "For loamy soil with pH 6-7, most crops grow well. Rice, wheat, and vegetables are great choices.",
            "Use certified seeds from authorized dealers for better germination and yield.",
            "Rotate crops to maintain soil health — follow rice with wheat or pulses.",
        ],
        "suggestions": ["Which crop for clay soil?", "Best season to sow wheat?", "Crop rotation tips?"],
    },
    "pest": {
        "keywords": ["pest", "disease", "insect", "bug", "fungus", "spray", "pesticide", "whitefly", "aphid"],
        "responses": [
            "For general pest control, use Neem oil spray (5ml/L) which is organic and effective against most pests.",
            "Identify the pest first before spraying. Upload a photo using our Pest Scanner for AI-based diagnosis.",
            "Prevention is better than cure — use resistant varieties, maintain field hygiene, and use yellow sticky traps.",
            "For fungal diseases, ensure proper drainage and air circulation. Spray Carbendazim 0.2% if needed.",
        ],
        "suggestions": ["How to control aphids?", "Natural pest remedies?", "When to spray pesticide?"],
    },
    "water": {
        "keywords": ["water", "irrigation", "rain", "moisture", "drip", "sprinkler", "drought"],
        "responses": [
            "Most crops need 4-6 irrigations during the season. Rice needs standing water, while wheat needs moisture at critical stages.",
            "Drip irrigation saves 40-60% water compared to flood irrigation. Great for vegetables and orchards.",
            "Monitor soil moisture — water when the top 2 inches of soil are dry. Over-watering causes root rot.",
            "Mulching with straw or plastic reduces water evaporation by 25-30%.",
        ],
        "suggestions": ["Drip irrigation setup?", "How often to water rice?", "Water conservation tips?"],
    },
    "soil": {
        "keywords": ["soil", "ph", "acidic", "alkaline", "clay", "sandy", "loam", "compost", "organic"],
        "responses": [
            "Ideal soil pH for most crops is 6.0-7.5. Add lime to raise pH or sulfur to lower pH.",
            "Improve sandy soil by adding organic matter (compost, vermicompost). For clay soil, add gypsum and sand.",
            "Test your soil regularly — use our Soil Analysis tool for detailed NPK and pH assessment.",
            "Healthy soil has good drainage, adequate organic matter (3-5%), and balanced nutrients.",
        ],
        "suggestions": ["How to improve clay soil?", "Best pH for vegetables?", "Soil testing method?"],
    },
    "weather": {
        "keywords": ["weather", "rain", "storm", "temperature", "frost", "heat", "cold", "season"],
        "responses": [
            "Check our Weather Alerts for farming-specific forecasts. We notify you about rain, frost, and heat waves.",
            "Before heavy rain, ensure drainage is clear. After rain, apply light fertilizer to help crop recovery.",
            "During heat waves (above 40°C), irrigate crops in early morning or late evening.",
            "Frost protection: irrigate the night before, use mulch, or set up wind machines in orchards.",
        ],
        "suggestions": ["Weather forecast for farming?", "Protect crops from frost?", "Heat wave precautions?"],
    },
    "general": {
        "keywords": [],
        "responses": [
            "I'm here to help with farming advice! Ask me about fertilizers, crops, pests, irrigation, soil health, or market prices.",
            "Try asking about specific topics like 'How to control pests organically?' or 'Best fertilizer for rice?'",
            "I can help with soil analysis, crop recommendations, and farming best practices.",
        ],
        "suggestions": ["Fertilizer advice", "Pest control tips", "Best crops for my soil?"],
    },
}


def get_response(message: str) -> tuple:
    msg_lower = message.lower()
    for category, data in KNOWLEDGE_BASE.items():
        if category == "general":
            continue
        for keyword in data["keywords"]:
            if keyword in msg_lower:
                return random.choice(data["responses"]), data["suggestions"]

    return random.choice(KNOWLEDGE_BASE["general"]["responses"]), KNOWLEDGE_BASE["general"]["suggestions"]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply, suggestions = get_response(req.message)
    return ChatResponse(reply=reply, suggestions=suggestions)
