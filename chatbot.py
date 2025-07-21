#!/usr/bin/env python3
"""
Chatbot avec outils FastMCP utilisant JSON-RPC
"""

import asyncio
import json
import re
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from mcp_client import MCPClient
from config import Config

class ChatbotWithTools:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=Config.AZURE_ENDPOINT,
            openai_api_version=Config.AZURE_API_VERSION,
            azure_deployment=Config.AZURE_DEPLOYMENT,
            openai_api_key=Config.AZURE_API_KEY,
            temperature=0.1,  # ← Plus déterministe comme dans le test
            max_tokens=Config.MAX_TOKENS
        )
        self.mcp_client = MCPClient()
        self.conversation_history = []
        
    async def initialize(self):
        """Initialise le chatbot et connecte aux serveurs FastMCP"""
        print("🚀 Initialisation du chatbot FastMCP avec JSON-RPC...")
        
        # Connexion aux serveurs FastMCP
        try:
            success1 = await self.mcp_client.connect_to_server(
                "calculator", "calculator_server.py"
            )
            success2 = await self.mcp_client.connect_to_server(
                "filesystem", "file_server.py"
            )
            success3 = await self.mcp_client.connect_to_server(
                "employees", "employee_server.py"
            )
            
            if success1 and success2 and success3:
                print("✅ Chatbot FastMCP avec JSON-RPC initialisé avec succès!")
            else:
                print("⚠️  Certains serveurs FastMCP n'ont pas pu être connectés")
        except Exception as e:
            print(f"❌ Erreur lors de la connexion FastMCP: {e}")
        
        # Affiche les outils disponibles
        tools = self.mcp_client.get_available_tools()
        if tools:
            print(f"📋 {len(tools)} outils disponibles:")
            for tool_key, tool_info in tools.items():
                print(f"  • {tool_key}: {tool_info['description']}")
        
        print("\n" + "="*50)
        print("💬 Chatbot FastMCP JSON-RPC prêt! Tapez 'quit' pour quitter.")
        print("="*50)
    
    def build_system_prompt(self) -> str:
        """Construit le prompt système avec les outils FastMCP"""
        tools_desc = self.mcp_client.get_tools_for_prompt()
        
        return f"""Vous êtes un assistant avec des outils. Vous DEVEZ TOUJOURS utiliser un outil.

{tools_desc}

FORMAT EXACT OBLIGATOIRE:
<tool_call>
{{"tool": "serveur.nom_outil", "arguments": {{"param": "valeur"}}}}
</tool_call>

EXEMPLES À COPIER EXACTEMENT:

Pour "Calcule 15 * 8":
<tool_call>
{{"tool": "calculator.multiply", "arguments": {{"a": 15, "b": 8}}}}
</tool_call>

Pour "Crée fichier test.txt avec Hello":
<tool_call>
{{"tool": "filesystem.write_file", "arguments": {{"path": "test.txt", "content": "Hello"}}}}
</tool_call>

Pour "Liste les employés":
<tool_call>
{{"tool": "employees.list_employees", "arguments": {{}}}}
</tool_call>

RÈGLE ABSOLUE: Répondez TOUJOURS avec un <tool_call>. Sinon c'est une ERREUR."""
    
    def extract_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Extrait les appels d'outils de la réponse"""
        pattern = r'<tool_call>(.*?)</tool_call>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        tool_calls = []
        for match in matches:
            try:
                tool_data = json.loads(match.strip())
                tool_calls.append(tool_data)
            except json.JSONDecodeError as e:
                print(f"⚠️  Erreur de parsing JSON: {e}")
        
        return tool_calls
    
    def remove_tool_calls_from_response(self, response: str) -> str:
        """Supprime les balises tool_call de la réponse"""
        pattern = r'<tool_call>.*?</tool_call>'
        return re.sub(pattern, '', response, flags=re.DOTALL).strip()
    
    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        """Exécute les appels d'outils FastMCP via JSON-RPC"""
        results = []
        
        for tool_call in tool_calls:
            try:
                tool_name = tool_call["tool"]
                arguments = tool_call["arguments"]
                
                # Parse le nom de l'outil
                if "." in tool_name:
                    server_name, tool_name = tool_name.split(".", 1)
                else:
                    print(f"⚠️  Format d'outil invalide: {tool_name}")
                    results.append(f"Erreur: Format d'outil invalide")
                    continue
                
                print(f"🔧 Exécution JSON-RPC: {server_name}.{tool_name} avec {arguments}")
                
                # Appelle l'outil FastMCP via JSON-RPC
                result = await self.mcp_client.call_tool(server_name, tool_name, arguments)
                results.append(str(result))
                
            except Exception as e:
                error_msg = f"Erreur lors de l'exécution de l'outil JSON-RPC: {str(e)}"
                print(f"❌ {error_msg}")
                results.append(error_msg)
        
        return results
    
    async def process_message(self, user_message: str) -> str:
        """Traite un message utilisateur avec FastMCP via JSON-RPC"""
        try:
            # Ajoute le message à l'historique
            self.conversation_history.append(HumanMessage(content=user_message))
            
            # Construit les messages pour l'LLM
            messages = [SystemMessage(content=self.build_system_prompt())] + self.conversation_history
            
            # Première réponse de l'LLM
            response = await self.llm.ainvoke(messages)
            llm_response = response.content
            
            # Debug: affiche la réponse brute de l'LLM
            print(f"🔍 Réponse LLM: {llm_response[:200]}...")
            
            # Vérifie s'il y a des appels d'outils
            tool_calls = self.extract_tool_calls(llm_response)
            
            if tool_calls:
                print(f"🔧 {len(tool_calls)} appel(s) d'outil détecté(s)")
                
                # Exécute les outils FastMCP via JSON-RPC
                tool_results = await self.execute_tool_calls(tool_calls)
                
                # Supprime les appels d'outils de la réponse
                clean_response = self.remove_tool_calls_from_response(llm_response)
                
                # Prépare le message avec les résultats des outils
                tool_results_text = "\n".join([
                    f"Résultat outil JSON-RPC {i+1}: {result}" 
                    for i, result in enumerate(tool_results)
                ])
                
                # Ajoute à l'historique
                self.conversation_history.append(SystemMessage(content=clean_response))
                self.conversation_history.append(SystemMessage(content=f"Résultats des outils JSON-RPC:\n{tool_results_text}"))
                
                # Demande une réponse finale
                final_messages = [
                    SystemMessage(content=self.build_system_prompt())
                ] + self.conversation_history + [
                    HumanMessage(content="Basé sur les résultats des outils JSON-RPC, donnez une réponse finale complète à l'utilisateur.")
                ]
                
                final_response = await self.llm.ainvoke(final_messages)
                final_answer = final_response.content
                
                self.conversation_history.append(SystemMessage(content=final_answer))
                
                return final_answer
            else:
                print("⚠️ Aucun appel d'outil détecté")
                # Pas d'outils, réponse normale
                self.conversation_history.append(SystemMessage(content=llm_response))
                return llm_response
                
        except Exception as e:
            error_msg = f"Erreur lors du traitement JSON-RPC: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    async def chat_loop(self):
        """Boucle de conversation principale JSON-RPC"""
        while True:
            try:
                user_input = input("\n👤 Vous: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Au revoir!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Assistant JSON-RPC: ", end="", flush=True)
                response = await self.process_message(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    async def cleanup(self):
        """Nettoie les ressources JSON-RPC"""
        await self.mcp_client.close()

async def main():
    # Initialise le chatbot FastMCP avec JSON-RPC
    chatbot = ChatbotWithTools()
    
    try:
        await chatbot.initialize()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())