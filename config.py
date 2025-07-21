#!/usr/bin/env python3
"""
Configuration pour le chatbot FastMCP
"""

import os
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

class Config:
    # Configuration Azure OpenAI
    AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "your-endpoint-here")
    AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your-api-key-here")
    AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    
    # Configuration du modèle
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    @classmethod
    def validate(cls):
        """Valide la configuration"""
        required_vars = [
            "AZURE_ENDPOINT",
            "AZURE_API_KEY",
            "AZURE_DEPLOYMENT"
        ]
        
        missing = []
        for var in required_vars:
            if not getattr(cls, var) or getattr(cls, var).startswith("your-"):
                missing.append(var)
        
        if missing:
            print("❌ Variables de configuration manquantes:")
            for var in missing:
                print(f"   - {var}")
            print("\nVeuillez configurer ces variables dans votre fichier .env")
            return False
        
        print("✅ Configuration validée")
        return True