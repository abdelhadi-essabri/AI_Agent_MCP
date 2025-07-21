#!/usr/bin/env python3
"""
Serveur MCP Employee Management - Version FastMCP avec décorateurs
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from mcp.server.fastmcp import FastMCP

# Création du serveur FastMCP
mcp = FastMCP("Employee Management Service")

# Fichier de stockage des employés
EMPLOYEES_FILE = "employees.json"

def load_employees() -> List[Dict[str, Any]]:
    """Charge les employés depuis le fichier JSON"""
    if not os.path.exists(EMPLOYEES_FILE):
        return []
    
    try:
        with open(EMPLOYEES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_employees(employees: List[Dict[str, Any]]) -> None:
    """Sauvegarde les employés dans le fichier JSON"""
    with open(EMPLOYEES_FILE, 'w', encoding='utf-8') as f:
        json.dump(employees, f, indent=2, ensure_ascii=False, default=str)

def generate_employee_id() -> int:
    """Génère un nouvel ID d'employé"""
    employees = load_employees()
    if not employees:
        return 1
    return max(emp.get('id', 0) for emp in employees) + 1

@mcp.tool()
def create_employee(
    prenom: str,
    nom: str,
    email: str,
    poste: str,
    departement: str,
    salaire: float,
    date_embauche: str,
    telephone: str = "",
    adresse: str = ""
) -> str:
    """Crée un nouvel employé
    
    Args:
        prenom: Prénom de l'employé
        nom: Nom de famille de l'employé
        email: Adresse email (doit être unique)
        poste: Poste occupé
        departement: Département de travail
        salaire: Salaire annuel
        date_embauche: Date d'embauche (format YYYY-MM-DD)
        telephone: Numéro de téléphone (optionnel)
        adresse: Adresse postale (optionnelle)
    """
    employees = load_employees()
    
    # Vérification de l'unicité de l'email
    if any(emp.get('email') == email for emp in employees):
        raise ValueError(f"Un employé avec l'email '{email}' existe déjà")
    
    # Validation de la date
    try:
        datetime.strptime(date_embauche, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD")
    
    # Validation du salaire
    if salaire < 0:
        raise ValueError("Le salaire ne peut pas être négatif")
    
    # Création du nouvel employé
    nouvel_employe = {
        "id": generate_employee_id(),
        "prenom": prenom.strip(),
        "nom": nom.strip(),
        "email": email.strip().lower(),
        "poste": poste.strip(),
        "departement": departement.strip(),
        "salaire": float(salaire),
        "date_embauche": date_embauche,
        "telephone": telephone.strip(),
        "adresse": adresse.strip(),
        "date_creation": datetime.now().isoformat(),
        "date_modification": datetime.now().isoformat(),
        "actif": True
    }
    
    employees.append(nouvel_employe)
    save_employees(employees)
    
    return f"✅ Employé créé avec succès!\nID: {nouvel_employe['id']}\nNom: {prenom} {nom}\nPoste: {poste}\nDépartement: {departement}"

@mcp.tool()
def get_employee(employee_id: int) -> str:
    """Récupère les informations d'un employé par son ID"""
    employees = load_employees()
    
    employee = next((emp for emp in employees if emp.get('id') == employee_id), None)
    if not employee:
        raise ValueError(f"Aucun employé trouvé avec l'ID {employee_id}")
    
    return json.dumps(employee, indent=2, ensure_ascii=False)

@mcp.tool()
def list_employees(departement: str = "", actif_seulement: bool = True) -> str:
    """Liste tous les employés avec filtres optionnels
    
    Args:
        departement: Filtrer par département (optionnel)
        actif_seulement: Afficher seulement les employés actifs
    """
    employees = load_employees()
    
    # Filtres
    if actif_seulement:
        employees = [emp for emp in employees if emp.get('actif', True)]
    
    if departement:
        employees = [emp for emp in employees if emp.get('departement', '').lower() == departement.lower()]
    
    if not employees:
        return "Aucun employé trouvé avec les critères spécifiés"
    
    # Formatage de la liste
    result = f"📋 Liste des employés ({len(employees)} trouvé(s)):\n\n"
    
    for emp in employees:
        status = "🟢 Actif" if emp.get('actif', True) else "🔴 Inactif"
        result += f"ID: {emp.get('id')}\n"
        result += f"👤 {emp.get('prenom')} {emp.get('nom')}\n"
        result += f"📧 {emp.get('email')}\n"
        result += f"💼 {emp.get('poste')} - {emp.get('departement')}\n"
        result += f"💰 {emp.get('salaire'):,.2f} €\n"
        result += f"📅 Embauché le: {emp.get('date_embauche')}\n"
        result += f"Status: {status}\n"
        result += "-" * 40 + "\n"
    
    return result

@mcp.tool()
def update_employee(
    employee_id: int,
    prenom: str = None,
    nom: str = None,
    email: str = None,
    poste: str = None,
    departement: str = None,
    salaire: float = None,
    telephone: str = None,
    adresse: str = None
) -> str:
    """Met à jour les informations d'un employé
    
    Args:
        employee_id: ID de l'employé à modifier
        Autres paramètres: Nouveaux valeurs (None = pas de modification)
    """
    employees = load_employees()
    
    # Trouve l'employé
    employee_index = next((i for i, emp in enumerate(employees) if emp.get('id') == employee_id), None)
    if employee_index is None:
        raise ValueError(f"Aucun employé trouvé avec l'ID {employee_id}")
    
    employee = employees[employee_index]
    
    # Vérification de l'unicité de l'email si modifié
    if email and email != employee.get('email'):
        if any(emp.get('email') == email.lower() for emp in employees):
            raise ValueError(f"Un employé avec l'email '{email}' existe déjà")
    
    # Mise à jour des champs modifiés
    modifications = []
    
    if prenom is not None:
        employee['prenom'] = prenom.strip()
        modifications.append(f"Prénom: {prenom}")
    
    if nom is not None:
        employee['nom'] = nom.strip()
        modifications.append(f"Nom: {nom}")
    
    if email is not None:
        employee['email'] = email.strip().lower()
        modifications.append(f"Email: {email}")
    
    if poste is not None:
        employee['poste'] = poste.strip()
        modifications.append(f"Poste: {poste}")
    
    if departement is not None:
        employee['departement'] = departement.strip()
        modifications.append(f"Département: {departement}")
    
    if salaire is not None:
        if salaire < 0:
            raise ValueError("Le salaire ne peut pas être négatif")
        employee['salaire'] = float(salaire)
        modifications.append(f"Salaire: {salaire:,.2f} €")
    
    if telephone is not None:
        employee['telephone'] = telephone.strip()
        modifications.append(f"Téléphone: {telephone}")
    
    if adresse is not None:
        employee['adresse'] = adresse.strip()
        modifications.append(f"Adresse: {adresse}")
    
    if not modifications:
        return "Aucune modification effectuée"
    
    # Met à jour la date de modification
    employee['date_modification'] = datetime.now().isoformat()
    
    # Sauvegarde
    employees[employee_index] = employee
    save_employees(employees)
    
    return f"✅ Employé {employee_id} mis à jour avec succès!\nModifications:\n" + "\n".join(f"• {mod}" for mod in modifications)

@mcp.tool()
def delete_employee(employee_id: int, permanent: bool = False) -> str:
    """Supprime ou désactive un employé
    
    Args:
        employee_id: ID de l'employé
        permanent: Si True, suppression définitive. Si False, désactivation
    """
    employees = load_employees()
    
    employee_index = next((i for i, emp in enumerate(employees) if emp.get('id') == employee_id), None)
    if employee_index is None:
        raise ValueError(f"Aucun employé trouvé avec l'ID {employee_id}")
    
    employee = employees[employee_index]
    
    if permanent:
        # Suppression définitive
        employees.pop(employee_index)
        save_employees(employees)
        return f"🗑️ Employé {employee_id} ({employee.get('prenom')} {employee.get('nom')}) supprimé définitivement"
    else:
        # Désactivation
        employee['actif'] = False
        employee['date_modification'] = datetime.now().isoformat()
        employees[employee_index] = employee
        save_employees(employees)
        return f"⏸️ Employé {employee_id} ({employee.get('prenom')} {employee.get('nom')}) désactivé"

@mcp.tool()
def reactivate_employee(employee_id: int) -> str:
    """Réactive un employé désactivé"""
    employees = load_employees()
    
    employee_index = next((i for i, emp in enumerate(employees) if emp.get('id') == employee_id), None)
    if employee_index is None:
        raise ValueError(f"Aucun employé trouvé avec l'ID {employee_id}")
    
    employee = employees[employee_index]
    
    if employee.get('actif', True):
        return f"L'employé {employee_id} est déjà actif"
    
    employee['actif'] = True
    employee['date_modification'] = datetime.now().isoformat()
    employees[employee_index] = employee
    save_employees(employees)
    
    return f"▶️ Employé {employee_id} ({employee.get('prenom')} {employee.get('nom')}) réactivé avec succès"

@mcp.tool()
def search_employees(term: str) -> str:
    """Recherche des employés par nom, email, poste ou département
    
    Args:
        term: Terme de recherche (minimum 2 caractères)
    """
    if len(term.strip()) < 2:
        raise ValueError("Le terme de recherche doit contenir au moins 2 caractères")
    
    employees = load_employees()
    term_lower = term.lower().strip()
    
    # Recherche dans les champs pertinents
    matching_employees = []
    for emp in employees:
        if (term_lower in emp.get('prenom', '').lower() or
            term_lower in emp.get('nom', '').lower() or
            term_lower in emp.get('email', '').lower() or
            term_lower in emp.get('poste', '').lower() or
            term_lower in emp.get('departement', '').lower()):
            matching_employees.append(emp)
    
    if not matching_employees:
        return f"Aucun employé trouvé pour le terme '{term}'"
    
    result = f"🔍 Résultats de recherche pour '{term}' ({len(matching_employees)} trouvé(s)):\n\n"
    
    for emp in matching_employees:
        status = "🟢" if emp.get('actif', True) else "🔴"
        result += f"{status} ID: {emp.get('id')} - {emp.get('prenom')} {emp.get('nom')}\n"
        result += f"   📧 {emp.get('email')}\n"
        result += f"   💼 {emp.get('poste')} - {emp.get('departement')}\n"
        result += f"   💰 {emp.get('salaire'):,.2f} €\n\n"
    
    return result

@mcp.tool()
def get_department_stats(departement: str = "") -> str:
    """Obtient les statistiques d'un département ou de tous les départements
    
    Args:
        departement: Nom du département (vide = tous les départements)
    """
    employees = load_employees()
    
    if departement:
        # Statistiques d'un département spécifique
        dept_employees = [emp for emp in employees if emp.get('departement', '').lower() == departement.lower()]
        if not dept_employees:
            return f"Aucun employé trouvé dans le département '{departement}'"
        
        actifs = [emp for emp in dept_employees if emp.get('actif', True)]
        salaires = [emp.get('salaire', 0) for emp in actifs]
        
        result = f"📊 Statistiques du département '{departement}':\n\n"
        result += f"👥 Nombre total d'employés: {len(dept_employees)}\n"
        result += f"🟢 Employés actifs: {len(actifs)}\n"
        result += f"🔴 Employés inactifs: {len(dept_employees) - len(actifs)}\n"
        
        if salaires:
            result += f"💰 Salaire moyen: {sum(salaires) / len(salaires):,.2f} €\n"
            result += f"💰 Salaire minimum: {min(salaires):,.2f} €\n"
            result += f"💰 Salaire maximum: {max(salaires):,.2f} €\n"
            result += f"💰 Masse salariale totale: {sum(salaires):,.2f} €\n"
        
        return result
    else:
        # Statistiques globales par département
        from collections import defaultdict
        
        dept_stats = defaultdict(lambda: {'total': 0, 'actifs': 0, 'salaires': []})
        
        for emp in employees:
            dept = emp.get('departement', 'Non défini')
            dept_stats[dept]['total'] += 1
            
            if emp.get('actif', True):
                dept_stats[dept]['actifs'] += 1
                dept_stats[dept]['salaires'].append(emp.get('salaire', 0))
        
        result = "📊 Statistiques par département:\n\n"
        
        for dept, stats in sorted(dept_stats.items()):
            result += f"🏢 {dept}:\n"
            result += f"   👥 Total: {stats['total']} employés\n"
            result += f"   🟢 Actifs: {stats['actifs']}\n"
            
            if stats['salaires']:
                avg_salary = sum(stats['salaires']) / len(stats['salaires'])
                total_salary = sum(stats['salaires'])
                result += f"   💰 Salaire moyen: {avg_salary:,.2f} €\n"
                result += f"   💰 Masse salariale: {total_salary:,.2f} €\n"
            
            result += "\n"
        
        # Statistiques globales
        total_employees = len(employees)
        active_employees = len([emp for emp in employees if emp.get('actif', True)])
        total_salaries = sum(emp.get('salaire', 0) for emp in employees if emp.get('actif', True))
        
        result += f"🌐 TOTAL ENTREPRISE:\n"
        result += f"   👥 {total_employees} employés au total\n"
        result += f"   🟢 {active_employees} employés actifs\n"
        result += f"   💰 Masse salariale totale: {total_salaries:,.2f} €\n"
        
        return result

if __name__ == "__main__":
    mcp.run()