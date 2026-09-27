# Architecture du Pipeline d'Intégration

## Vue d'ensemble du flux

```
[Système A - Source]
  generate_fpml_messages.py écrit des messages .xml dans source_system/outbox/
  (simule un système de trading/core banking qui émet des confirmations)
              │
              ▼
[MIDDLEWARE - pipeline.py orchestre 4 étapes]
              │
              ├─ 1. PARSING (parser.py)
              │      XML -> dictionnaire Python
              │      Erreur possible : ParsingError (XML mal formé)
              │
              ├─ 2. VALIDATION (validator.py)
              │      Contrôle des règles métier (champs requis, contrepartie
              │      connue, devise connue, notional positif)
              │      Erreur possible : ValidationError
              │
              ├─ 3. TRANSFORMATION (transformer.py)
              │      Mapping vers le format cible : détermine les comptes
              │      comptables (débit/crédit) selon le type de produit
              │
              └─ 4. ROUTAGE / CHARGEMENT (target_system/db.py)
                     Insertion dans accounting_entries
              │
              ▼
[Système B - Cible]
  data/<env>/accounting.db : base comptable recevant les écritures
              │
              ▼
  Le fichier XML d'origine est déplacé vers :
    - source_system/processed/  si succès (piste d'audit)
    - source_system/failed/     si échec (mis en quarantaine)
  ET un incident est créé automatiquement en cas d'échec (incident_manager.py)
```

## Pourquoi séparer parsing et validation ?

Ce sont deux catégories d'erreurs fondamentalement différentes :

- **Erreur de parsing** = le message est **techniquement invalide** (XML
  cassé). On ne peut même pas lire son contenu. C'est presque toujours un
  problème côté système émetteur (bug, encodage, troncature réseau).
- **Erreur de validation** = le message est **techniquement lisible**,
  mais son **contenu métier** est incohérent (contrepartie inconnue,
  devise absente). C'est un problème de données, pas de format.

Séparer les deux permet de diagnostiquer un incident plus vite : "est-ce
un problème technique (parsing) ou un problème de données (validation) ?"
-- question typique posée par un analyste support N2 face à un incident.

## Pourquoi une criticité différente selon le type d'erreur ?

Dans `incident_manager.py`, une `ParsingError` est taguée `CRITICAL`
(SLA le plus court) alors qu'une `ValidationError` est taguée `HIGH`
(SLA plus long). Justification métier : un message illisible bloque
totalement son traitement et peut cacher un problème système plus large
affectant d'autres messages ; un message lisible mais avec une donnée
incohérente est un cas isolé, généralement plus facile et moins urgent
à corriger.

## Pourquoi déplacer les fichiers (processed/ vs failed/) plutôt que les supprimer ?

C'est un principe de **piste d'audit (audit trail)** : dans un système
bancaire réel, on ne perd jamais un message source, même après
traitement. `processed/` prouve qu'un message a bien été intégré ;
`failed/` (avec l'incident associé) prouve qu'une anomalie a été
détectée et tracée, jamais silencieusement ignorée.

## Pourquoi la configuration est-elle externalisée en YAML par environnement ?

Un vrai système bancaire ne pointe **jamais** vers la production par
accident. Séparer `uat.yaml` / `preprod.yaml` / `prod.yaml` avec des
chemins de base et des seuils différents (`strict_validation`,
`max_batch_size`, SLA) permet de :
- tester en toute sécurité sans toucher aux données réelles
- durcir progressivement les règles à mesure qu'on se rapproche de la prod
- ne jamais coder en dur un chemin ou un identifiant d'environnement
  dans la logique métier (`pipeline.py` ne connaît que la clé `--env`)
