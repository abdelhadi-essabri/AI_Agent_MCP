#!/usr/bin/env python3
"""
Test du prompt pour diagnostiquer pourquoi l'IA ne génère pas les tool_call
"""

import asyncio
import re
import json
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config

def extract_tool_calls(response: str):
    """Extrait les appels d'outils de la réponse"""
    pattern = r'<tool_call>(.*?)</tool_call>'
    matches = re.findall(pattern, response, re.DOTALL)
    
    tool_calls = []
    for match in matches:
        try:
            tool_data = json.loads(match.strip())
            tool_calls.append(tool_data)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
    
    return tool_calls

async def test_prompt():
    """Test le prompt pour voir si l'IA génère les tool_call"""
    
    llm = AzureChatOpenAI(
        azure_endpoint=Config.AZURE_ENDPOINT,
        openai_api_version=Config.AZURE_API_VERSION,
        azure_deployment=Config.AZURE_DEPLOYMENT,
        openai_api_key=Config.AZURE_API_KEY,
        temperature=0.1,  # Plus déterministe
        max_tokens=1000
    )
    
    # Prompt ultra simple et direct
    system_prompt = """Vous êtes un assistant avec des outils. 

Outils disponibles:
- calculator.multiply: Multiplication de deux nombres (paramètres: a, b)
- filesystem.write_file: Écrit un fichier (paramètres: path, content)

FORMAT OBLIGATOIRE pour utiliser un outil:
<tool_call>
{"tool": "serveur.nom_outil", "arguments": {"param": "valeur"}}
</tool_call>

RÈGLE: Utilisez TOUJOURS un outil pour répondre. Ne répondez JAMAIS sans outil.

EXEMPLES:
Utilisateur: "Calcule 5 * 3"
Assistant: <tool_call>
{"tool": "calculator.multiply", "arguments": {"a": 5, "b": 3}}
</tool_call>

Utilisateur: "Crée fichier test.txt avec Hello"
Assistant: <tool_call>
{"tool": "filesystem.write_file", "arguments": {"path": "test.txt", "content": "Hello"}}
</tool_call>"""
    
    # Tests de différentes requêtes
    test_queries = [
        "Calcule 15 * 8",
        "Crée un fichier test.txt avec Hello World",
        "Multiplie 10 par 5",
        "Écris dans un fichier example.txt le texte Bonjour"
    ]
    
    print("🧪 Test du prompt LLM")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 30)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        try:
            response = await llm.ainvoke(messages)
            llm_response = response.content
            
            print(f"🤖 Réponse LLM:\n{llm_response}\n")
            
            # Vérifie les tool_calls
            tool_calls = extract_tool_calls(llm_response)
            
            if tool_calls:
                print(f"✅ {len(tool_calls)} tool_call(s) détecté(s):")
                for j, call in enumerate(tool_calls, 1):
                    print(f"   {j}. {call}")
            else:
                print("❌ Aucun tool_call détecté!")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print(f"\n🎯 Test terminé")

if __name__ == "__main__":
    asyncio.run(test_prompt())