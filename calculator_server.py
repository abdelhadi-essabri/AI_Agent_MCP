#!/usr/bin/env python3
"""
Serveur MCP Calculator - Version FastMCP avec décorateurs
"""

import math
from mcp.server.fastmcp import FastMCP

# Création du serveur FastMCP
mcp = FastMCP("Calculator Service")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Addition de deux nombres"""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Soustraction de deux nombres"""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplication de deux nombres"""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Division de deux nombres"""
    if b == 0:
        raise ValueError("Division par zéro impossible")
    return a / b

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Élévation à la puissance"""
    return base ** exponent

@mcp.tool()
def square_root(number: float) -> float:
    """Racine carrée d'un nombre"""
    if number < 0:
        raise ValueError("Racine carrée d'un nombre négatif impossible")
    return math.sqrt(number)

@mcp.tool()
def factorial(n: int) -> int:
    """Factorielle d'un nombre entier"""
    if n < 0:
        raise ValueError("Factorielle d'un nombre négatif impossible")
    return math.factorial(n)

if __name__ == "__main__":
    mcp.run()