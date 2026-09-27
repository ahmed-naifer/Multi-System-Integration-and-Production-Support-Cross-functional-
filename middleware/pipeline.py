"""
pipeline.py
Orchestrateur du middleware d'intégration :

  lecture des messages (outbox du Système A)
      -> parsing FpML
      -> validation métier
      -> transformation vers le format cible
      -> chargement dans le système comptable (Système B)

  En cas d'échec (parsing ou validation), le message est déplacé vers
  failed/ et un incident est créé automatiquement (support N2/N3).
  En cas de succès, il est déplacé vers processed/ (piste d'audit).
"""

import os
import sys
import logging
import shutil

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "target_system"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "incident_management"))

from config_loader import load_config
from parser import parse_fpml, ParsingError
from validator import validate, ValidationError
from transformer import transform
import db as target_db
import incident_manager

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


def setup_logging(level_name):
    log_dir = os.path.join(PROJECT_ROOT, "logs")
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "integration.log")),
            logging.StreamHandler(),
        ],
    )


def run_pipeline(env="uat"):
    config = load_config(env)
    setup_logging(config["logging"]["level"])
    logger = logging.getLogger("integration")

    logger.info(f"=== Démarrage du pipeline d'intégration - Environnement {config['environment']} ===")

    outbox_dir = os.path.join(PROJECT_ROOT, config["source_system"]["outbox_path"])
    processed_dir = os.path.join(PROJECT_ROOT, "source_system", "processed")
    failed_dir = os.path.join(PROJECT_ROOT, "source_system", "failed")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    target_db.init_target_system(config["target_system"]["db_path"])

    files = sorted(f for f in os.listdir(outbox_dir) if f.endswith(".xml"))
    max_batch = config["middleware"]["max_batch_size"]
    if len(files) > max_batch:
        logger.warning(f"Batch tronqué : {len(files)} messages présents, max_batch_size={max_batch}")
        files = files[:max_batch]

    stats = {"processed": 0, "failed": 0}
    sla_config = config["incident_management"]["sla_hours"]

    for filename in files:
        filepath = os.path.join(outbox_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()

        try:
            message = parse_fpml(content, source_ref=filename)
            validate(message)
            entry = transform(message)
            target_db.insert_entry(config["target_system"]["db_path"], entry)

            shutil.move(filepath, os.path.join(processed_dir, filename))
            stats["processed"] += 1
            logger.info(f"OK   | {filename} | trade_id={message.get('trade_id')}")

        except (ParsingError, ValidationError) as e:
            incident = incident_manager.create_incident(e, filename, sla_config)
            shutil.move(filepath, os.path.join(failed_dir, filename))
            stats["failed"] += 1
            logger.error(
                f"FAIL | {filename} | {type(e).__name__} | {e} | "
                f"incident={incident['incident_id']} | SLA={incident['sla_hours']}h"
            )

    logger.info(
        f"=== Pipeline terminé : {stats['processed']} intégré(s), {stats['failed']} en échec ==="
    )
    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline d'intégration multi-systèmes bancaires")
    parser.add_argument("--env", default="uat", choices=["uat", "preprod", "prod"])
    args = parser.parse_args()

    run_pipeline(env=args.env)
