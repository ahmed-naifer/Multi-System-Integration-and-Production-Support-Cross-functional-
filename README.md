# Plateforme d'Intégration Multi-Systèmes Bancaires

Middleware d'intégration simulant le flux entre un système de trading
(Système A, façon Murex) et un système comptable cible (Système B),
avec parsing FpML, validation métier, transformation, gestion
d'environnements (UAT/PreProd/Prod), et gestion d'incidents avec SLA.

> ⚠️ **Projet pédagogique / démonstration de compétences.** Le format
> FpML est volontairement simplifié (voir `docs/message_format.md`) et
> ne représente pas la norme complète. Ce n'est pas un connecteur Murex
> réel, mais une illustration fidèle de la logique d'intégration.

## Ce que couvre ce projet

- **Parsing** de messages FpML (XML) avec gestion explicite des erreurs
  de format
- **Validation métier** (contrepartie connue, devise connue, notional
  positif, champs obligatoires)
- **Transformation** vers un format cible (mapping comptable débit/crédit
  par type de produit)
- **Gestion multi-environnements** (UAT / PreProd / Production) via
  configuration YAML externalisée, avec seuils de tolérance et SLA
  différenciés
- **Gestion d'incidents** : création automatique de tickets avec
  criticité (`CRITICAL`/`HIGH`) et SLA calculé selon l'environnement
- **Piste d'audit** : chaque message source est archivé (`processed/`
  ou `failed/`), jamais perdu
- **Orchestration Unix** : pipeline complet scriptable, loggé, avec
  résumé des incidents ouverts

## Structure du projet

```
banking-integration-platform/
├── README.md
├── requirements.txt
├── config/
│   ├── uat.yaml
│   ├── preprod.yaml
│   └── prod.yaml
├── source_system/
│   ├── generate_fpml_messages.py   # Système A : génère les messages
│   ├── outbox/                      # messages en attente de traitement
│   ├── processed/                   # messages intégrés avec succès
│   └── failed/                      # messages en échec (quarantaine)
├── middleware/
│   ├── config_loader.py
│   ├── parser.py                    # parsing FpML
│   ├── validator.py                 # règles métier
│   ├── transformer.py               # mapping comptable
│   └── pipeline.py                  # orchestrateur
├── target_system/
│   ├── schema.sql                   # Système B : base comptable
│   └── db.py
├── incident_management/
│   └── incident_manager.py          # tickets d'incident + SLA
├── scripts/
│   └── run_integration.sh           # orchestration Unix complète
├── docs/
│   ├── architecture.md
│   ├── message_format.md
│   └── environments.md
└── tests/
    └── integration_test_cases.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Exécution

### Pipeline complet (recommandé)
```bash
chmod +x scripts/run_integration.sh
./scripts/run_integration.sh uat        # ou preprod / prod
```
Génère les messages source, exécute le middleware, affiche le résumé
des incidents. Log complet dans `logs/integration_run_<env>_<timestamp>.log`.

### Étape par étape
```bash
cd source_system
python3 generate_fpml_messages.py

cd ../middleware
python3 pipeline.py --env uat
```

### Consulter les incidents ouverts
```bash
cd incident_management
python3 -c "
import incident_manager
for inc in incident_manager.list_open_incidents():
    print(inc['incident_id'], inc['severity'], inc['sla_deadline'], inc['message'])
"
```

### Explorer la base comptable cible
```bash
sqlite3 data/uat/accounting.db
.tables
SELECT * FROM accounting_entries LIMIT 10;
.quit
```

## Documentation

- [Architecture du pipeline](docs/architecture.md)
- [Format de message FpML simplifié](docs/message_format.md)
- [Gestion des environnements UAT/PreProd/Prod](docs/environments.md)
- [Cahier de recette](tests/integration_test_cases.md)

## Compétences illustrées

`Intégration de systèmes bancaires` · `Parsing XML/FpML` ·
`Validation de données` · `Mapping de champs` ·
`Gestion multi-environnements (UAT/PreProd/Prod)` ·
`Gestion d'incidents & SLA` · `Support technique N2/N3` ·
`Python` · `SQL` · `Unix shell scripting` · `Configuration YAML` ·
`Logging & audit trail`
