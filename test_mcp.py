#!/usr/bin/env python3
"""
Tests pour les serveurs MCP FastMCP
"""

import asyncio
from real_mcp_client import RealMCPClient

async def test_calculator():
    """Test du serveur calculator"""
    print("🧪 Test du serveur Calculator JSON-RPC")
    print("=" * 40)
    
    client = RealMCPClient()
    
    try:
        # Test de connexion
        success = await client.connect_to_server("calculator", "calculator_server.py")
        
        if success:
            # Tests d'appels d'outils
            print("\n🧮 Test d'addition 5 + 3:")
            result = await client.call_tool("calculator", "add", {"a": 5, "b": 3})
            print(f"Résultat: {result}")
            
            print("\n🧮 Test de racine carrée de 16:")
            result = await client.call_tool("calculator", "square_root", {"number": 16})
            print(f"Résultat: {result}")
            
            print("\n🧮 Test de factorielle de 5:")
            result = await client.call_tool("calculator", "factorial", {"n": 5})
            print(f"Résultat: {result}")
        
        print("\n✅ Test Calculator terminé!")
        
    except Exception as e:
        print(f"❌ Erreur durant le test Calculator: {e}")
    
    finally:
        await client.close()

async def test_employees():
    """Test du serveur employees"""
    print("🧪 Test du serveur Employees JSON-RPC")
    print("=" * 40)
    
    client = RealMCPClient()
    
    try:
        # Test de connexion
        success = await client.connect_to_server("employees", "employee_server.py")
        
        if success:
            # Test de création d'employé
            print("\n👤 Création d'un employé test:")
            result = await client.call_tool("employees", "create_employee", {
                "prenom": "Test",
                "nom": "User",
                "email": "test.user@example.com",
                "poste": "Testeur",
                "departement": "QA",
                "salaire": 50000,
                "date_embauche": "2024-01-01",
                "telephone": "01.23.45.67.89"
            })
            print(f"Résultat: {result}")
            
            # Test de liste des employés
            print("\n📋 Liste des employés:")
            result = await client.call_tool("employees", "list_employees", {})
            print(f"Résultat: {result[:300]}...")
            
            # Test de recherche
            print("\n🔍 Recherche d'employés:")
            result = await client.call_tool("employees", "search_employees", {"term": "test"})
            print(f"Résultat: {result}")
            
            # Test de statistiques
            print("\n📊 Statistiques générales:")
            result = await client.call_tool("employees", "get_department_stats", {})
            print(f"Résultat: {result[:300]}...")
        
        print("\n✅ Test Employees terminé!")
        
    except Exception as e:
        print(f"❌ Erreur durant le test Employees: {e}")
    
    finally:
        await client.close()

async def test_filesystem():
    """Test du serveur filesystem"""
    print("🧪 Test du serveur Filesystem JSON-RPC")
    print("=" * 40)
    
    client = RealMCPClient()
    
    try:
        # Test de connexion
        success = await client.connect_to_server("filesystem", "file_server.py")
        
        if success:
            # Test d'écriture de fichier
            print("\n📝 Création d'un fichier test:")
            result = await client.call_tool("filesystem", "write_file", {
                "path": "test_json_rpc.txt",
                "content": "Test du protocole JSON-RPC avec FastMCP"
            })
            print(f"Résultat: {result}")
            
            # Test de lecture de fichier
            print("\n📖 Lecture du fichier test:")
            result = await client.call_tool("filesystem", "read_file", {
                "path": "test_json_rpc.txt"
            })
            print(f"Résultat: {result}")
            
            # Test de liste des fichiers
            print("\n📁 Liste des fichiers:")
            result = await client.call_tool("filesystem", "list_files", {"directory": "."})
            print(f"Résultat: {result[:300]}...")
        
        print("\n✅ Test Filesystem terminé!")
        
    except Exception as e:
        print(f"❌ Erreur durant le test Filesystem: {e}")
    
    finally:
        await client.close()

async def test_all_servers():
    """Test de tous les serveurs"""
    print("🚀 Test complet de tous les serveurs JSON-RPC")
    print("=" * 50)
    
    await test_calculator()
    print()
    await test_employees()
    print()
    await test_filesystem()
    
    print("\n🎉 Tous les tests terminés!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "calculator":
            asyncio.run(test_calculator())
        elif sys.argv[1] == "employees":
            asyncio.run(test_employees())
        elif sys.argv[1] == "filesystem":
            asyncio.run(test_filesystem())
        else:
            print("Usage: python test_mcp.py [calculator|employees|filesystem]")
    else:
        asyncio.run(test_all_servers())