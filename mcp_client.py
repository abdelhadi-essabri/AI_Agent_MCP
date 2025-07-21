#!/usr/bin/env python3
"""
Client MCP utilisant le protocole JSON-RPC
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any, List, Optional
import uuid

class MCPClient:
    def __init__(self):
        self.servers: Dict[str, subprocess.Popen] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    async def connect_to_server(self, server_name: str, script_path: str) -> bool:
        """Connecte à un serveur FastMCP avec protocole JSON-RPC"""
        try:
            print(f"🔌 Connexion JSON-RPC au serveur '{server_name}'...")
            
            # Lance le processus serveur FastMCP
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Teste si le processus démarre
            await asyncio.sleep(0.5)
            if process.returncode is not None:
                stderr_output = await process.stderr.read()
                print(f"❌ Le serveur '{server_name}' s'est arrêté: {stderr_output.decode()}")
                return False
            
            # Stocke le processus
            self.servers[server_name] = process
            
            # Effectue le handshake MCP avec initialize
            success = await self._initialize_server(server_name, process)
            if success:
                # Liste les outils disponibles
                await self._list_tools(server_name, process)
                print(f"✅ Serveur JSON-RPC '{server_name}' connecté")
                return True
            else:
                print(f"❌ Échec du handshake avec '{server_name}'")
                return False
            
        except Exception as e:
            print(f"❌ Erreur de connexion JSON-RPC au serveur '{server_name}': {e}")
            return False
    
    async def _send_jsonrpc_request(self, process: subprocess.Popen, method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Envoie une requête JSON-RPC et attend la réponse"""
        try:
            # Prépare la requête JSON-RPC 2.0
            request_id = str(uuid.uuid4())
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method
            }
            
            if params:
                request["params"] = params
            
            # Sérialise et envoie
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Lit la réponse
            response_line = await process.stdout.readline()
            if not response_line:
                return None
            
            response = json.loads(response_line.decode().strip())
            
            # Vérifie si c'est une réponse valide
            if response.get("id") == request_id:
                return response
            else:
                print(f"⚠️ ID de réponse incorrect: attendu {request_id}, reçu {response.get('id')}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur JSON-RPC: {e}")
            return None
    
    async def _initialize_server(self, server_name: str, process: subprocess.Popen) -> bool:
        """Effectue le handshake d'initialisation MCP"""
        try:
            # Envoie la requête initialize
            params = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "FastMCP-Client",
                    "version": "1.0.0"
                }
            }
            
            response = await self._send_jsonrpc_request(process, "initialize", params)
            
            if response and "result" in response:
                print(f"🤝 Handshake réussi avec {server_name}")
                
                # Envoie initialized notification
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                notification_json = json.dumps(notification) + "\n"
                process.stdin.write(notification_json.encode())
                await process.stdin.drain()
                
                return True
            else:
                print(f"❌ Échec de l'initialisation: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur d'initialisation: {e}")
            return False
    
    async def _list_tools(self, server_name: str, process: subprocess.Popen) -> bool:
        """Liste les outils disponibles du serveur"""
        try:
            response = await self._send_jsonrpc_request(process, "tools/list")
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                print(f"📋 {len(tools)} outils trouvés pour '{server_name}':")
                
                for tool in tools:
                    tool_name = tool.get("name")
                    tool_desc = tool.get("description", "")
                    
                    # Ajoute l'outil à notre registry
                    tool_key = f"{server_name}.{tool_name}"
                    self.tools[tool_key] = {
                        "name": tool_name,
                        "description": tool_desc,
                        "server": server_name,
                        "schema": tool.get("inputSchema", {})
                    }
                    
                    print(f"  • {tool_name}: {tool_desc}")
                
                return True
            else:
                print(f"❌ Impossible de lister les outils: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur de listing des outils: {e}")
            return False
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Appelle un outil via JSON-RPC"""
        if server_name not in self.servers:
            raise ValueError(f"Serveur '{server_name}' non connecté")
        
        process = self.servers[server_name]
        
        try:
            # Prépare les paramètres de l'appel d'outil
            params = {
                "name": tool_name,
                "arguments": arguments
            }
            
            # Envoie la requête tools/call
            response = await self._send_jsonrpc_request(process, "tools/call", params)
            
            if response and "result" in response:
                # Extrait le contenu de la réponse
                content = response["result"].get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "Pas de résultat")
                else:
                    return "Réponse vide"
            elif response and "error" in response:
                error = response["error"]
                raise Exception(f"Erreur serveur: {error.get('message', 'Erreur inconnue')}")
            else:
                raise Exception("Réponse invalide du serveur")
                
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel JSON-RPC de l'outil '{tool_name}': {e}")
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des outils disponibles"""
        return self.tools
    
    def get_tools_for_prompt(self) -> str:
        """Génère la description des outils pour le prompt"""
        if not self.tools:
            return "Aucun outil disponible."
        
        tools_text = "Outils disponibles (via JSON-RPC):\n"
        for tool_key, tool_info in self.tools.items():
            tools_text += f"- {tool_key}: {tool_info['description']}\n"
            
            # Ajoute les paramètres depuis le schema
            schema = tool_info.get('schema', {})
            properties = schema.get('properties', {})
            if properties:
                params = list(properties.keys())
                tools_text += f"  Paramètres: {', '.join(params)}\n"
        
        return tools_text
    
    async def close(self):
        """Ferme toutes les connexions JSON-RPC"""
        for server_name, process in self.servers.items():
            try:
                # Envoie une notification de fermeture si possible
                if process and process.returncode is None:
                    try:
                        # Optionnel: envoyer une notification de shutdown
                        shutdown_notification = {
                            "jsonrpc": "2.0",
                            "method": "notifications/shutdown"
                        }
                        notification_json = json.dumps(shutdown_notification) + "\n"
                        process.stdin.write(notification_json.encode())
                        await process.stdin.drain()
                        
                        # Donne un peu de temps pour la fermeture propre
                        await asyncio.sleep(0.1)
                    except:
                        pass  # Ignore les erreurs de fermeture
                    
                    # Termine le processus
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=3.0)
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                
                print(f"🔌 Déconnecté JSON-RPC du serveur '{server_name}'")
                
            except Exception as e:
                print(f"⚠️ Erreur lors de la fermeture JSON-RPC du serveur '{server_name}': {e}")
        
        self.servers.clear()
        self.tools.clear()