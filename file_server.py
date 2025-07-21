#!/usr/bin/env python3
"""
Serveur MCP File System - Version FastMCP avec décorateurs
"""

import os
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Création du serveur FastMCP
mcp = FastMCP("Filesystem Service")

@mcp.tool()
def read_file(path: str) -> str:
    """Lit le contenu d'un fichier"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Fichier '{path}' non trouvé")
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture: {str(e)}")

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Écrit du contenu dans un fichier"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Fichier '{path}' écrit avec succès"
    except Exception as e:
        raise ValueError(f"Erreur lors de l'écriture: {str(e)}")

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """Liste les fichiers d'un répertoire"""
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                files.append(f"📄 {item}")
            elif os.path.isdir(item_path):
                files.append(f"📁 {item}/")
        return "\n".join(files) if files else "Aucun fichier trouvé"
    except Exception as e:
        raise ValueError(f"Erreur: {str(e)}")

@mcp.tool()
def get_file_info(path: str) -> str:
    """Obtient les informations d'un fichier"""
    try:
        stat = os.stat(path)
        info = {
            "path": path,
            "size_bytes": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.2f} KB" if stat.st_size > 1024 else f"{stat.st_size} bytes",
            "modified": stat.st_mtime,
            "is_file": os.path.isfile(path),
            "is_directory": os.path.isdir(path)
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        raise ValueError(f"Erreur: {str(e)}")

@mcp.tool()
def create_directory(path: str) -> str:
    """Crée un répertoire"""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Répertoire '{path}' créé avec succès"
    except Exception as e:
        raise ValueError(f"Erreur lors de la création: {str(e)}")

if __name__ == "__main__":
    mcp.run()