#!/bin/bash
# =============================================================
# run_integration.sh
# Orchestration complète du pipeline d'intégration bancaire :
#   1. Génération des messages source (simule le Système A)
#   2. Exécution du middleware (parse -> validate -> transform -> load)
#   3. Résumé des incidents ouverts
#
# Usage : ./run_integration.sh [uat|preprod|prod]
# =============================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV="${1:-uat}"

if [[ ! "$ENV" =~ ^(uat|preprod|prod)$ ]]; then
    echo "Erreur : environnement '$ENV' invalide. Valeurs autorisées : uat, preprod, prod" >&2
    exit 1
fi

LOG_DIR="$PROJECT_ROOT/logs"
DATE_TAG=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/integration_run_${ENV}_${DATE_TAG}.log"
mkdir -p "$LOG_DIR"

echo "=== Démarrage de l'intégration - Environnement: $ENV - $(date) ===" | tee -a "$LOG_FILE"

{
    echo "--- Étape 1/2 : génération des messages source ---"
    cd "$PROJECT_ROOT/source_system"
    python3 generate_fpml_messages.py

    echo "--- Étape 2/2 : exécution du pipeline d'intégration ---"
    cd "$PROJECT_ROOT/middleware"
    python3 pipeline.py --env "$ENV"

} >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "--- Résumé des incidents ouverts ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT/incident_management"
python3 -c "
import incident_manager
incidents = incident_manager.list_open_incidents()
print(f'{len(incidents)} incident(s) ouvert(s).')
for inc in incidents:
    print(f\"  {inc['incident_id']} | {inc['severity']:<8} | SLA {inc['sla_hours']}h | {inc['message']}\")
" | tee -a "$LOG_FILE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Intégration terminée avec SUCCES - $(date) ===" | tee -a "$LOG_FILE"
else
    echo "=== ECHEC de l'intégration - voir $LOG_FILE ===" | tee -a "$LOG_FILE"
fi

echo "Log complet disponible dans : $LOG_FILE"
exit $EXIT_CODE

# -------------------------------------------------------------
# Exemple d'entrée crontab pour exécution en production toutes
# les 15 minutes pendant les heures de marché :
#   */15 8-18 * * 1-5 /chemin/vers/scripts/run_integration.sh prod >> /var/log/integration_cron.log 2>&1
# -------------------------------------------------------------
