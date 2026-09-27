"""
config_loader.py
Charge la configuration correspondant à l'environnement demandé
(UAT / PreProd / Production), comme le ferait un vrai système bancaire
qui isole strictement ses environnements de déploiement.
"""

import os
import yaml

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")

VALID_ENVIRONMENTS = {"uat", "preprod", "prod"}


def load_config(env="uat"):
    """Charge le fichier YAML correspondant à l'environnement.
    Lève une erreur explicite si l'environnement n'existe pas -- on ne
    veut jamais qu'un mauvais nom d'environnement retombe silencieusement
    sur une config par défaut (risque en production)."""
    env = env.lower()
    if env not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"Environnement '{env}' inconnu. Valeurs autorisées : {sorted(VALID_ENVIRONMENTS)}"
        )

    config_path = os.path.join(CONFIG_DIR, f"{env}.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config


if __name__ == "__main__":
    import json
    for env in VALID_ENVIRONMENTS:
        print(f"--- {env.upper()} ---")
        print(json.dumps(load_config(env), indent=2))
