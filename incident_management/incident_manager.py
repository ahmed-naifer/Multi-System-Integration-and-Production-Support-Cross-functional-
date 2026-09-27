"""
incident_manager.py
Génère un ticket d'incident structuré lorsqu'un message échoue en
intégration (erreur de parsing ou de validation) -- reproduit la
logique d'un outil de support N2/N3 : criticité, SLA, horodatage.
"""

import json
import os
import uuid
from datetime import datetime, timedelta

INCIDENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "incidents")

# La criticité dépend du type d'erreur : un XML illisible est plus grave
# qu'une valeur métier suspecte, car il bloque tout traitement automatique.
SEVERITY_MAPPING = {
    "ParsingError": "CRITICAL",
    "ValidationError": "HIGH",
}


def create_incident(error, source_ref, sla_hours_config):
    """Crée un ticket d'incident à partir d'une exception levée par le
    pipeline. sla_hours_config vient de la config d'environnement
    (ex: {'CRITICAL': 1, 'HIGH': 4, 'MEDIUM': 24})."""
    error_type = type(error).__name__
    severity = SEVERITY_MAPPING.get(error_type, "MEDIUM")
    sla_hours = sla_hours_config.get(severity, 24)

    now = datetime.now()
    incident = {
        "incident_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
        "source_ref": source_ref,
        "error_type": error_type,
        "message": str(error),
        "severity": severity,
        "status": "OPEN",
        "created_at": now.isoformat(),
        "sla_deadline": (now + timedelta(hours=sla_hours)).isoformat(),
        "sla_hours": sla_hours,
    }

    os.makedirs(INCIDENTS_DIR, exist_ok=True)
    incident_path = os.path.join(INCIDENTS_DIR, f"{incident['incident_id']}.json")
    with open(incident_path, "w") as f:
        json.dump(incident, f, indent=2)

    return incident


def list_open_incidents():
    """Liste tous les incidents encore ouverts (pour un dashboard support)."""
    if not os.path.isdir(INCIDENTS_DIR):
        return []

    incidents = []
    for filename in os.listdir(INCIDENTS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(INCIDENTS_DIR, filename), "r") as f:
                incidents.append(json.load(f))
    return sorted(incidents, key=lambda i: i["created_at"])
