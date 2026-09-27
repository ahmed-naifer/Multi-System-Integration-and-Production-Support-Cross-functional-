# Gestion des environnements (UAT / PreProd / Production)

## Pourquoi isoler les environnements ?

Dans une banque, un système comme Murex n'est **jamais** modifié ou testé
directement en production. Trois environnements au minimum coexistent,
avec des niveaux de rigueur croissants :

| Environnement | Objectif | Données | Rigueur |
|---|---|---|---|
| **UAT** (User Acceptance Testing) | Valider le comportement fonctionnel avec les utilisateurs métier | Données de test, souvent anonymisées | Tolérant : `strict_validation: false` |
| **PreProd** | Répétition générale dans des conditions proches de la production | Copie proche de la production (volumes réalistes) | Intermédiaire |
| **Production** | Traitement réel des transactions de la banque | Données réelles, sensibles | Maximal : aucune tolérance, SLA les plus courts |

## Comment ce projet illustre cette isolation

Chaque environnement possède :
- son propre fichier de configuration (`config/uat.yaml`, `preprod.yaml`, `prod.yaml`)
- sa propre base de données cible (`data/uat/`, `data/preprod/`, `data/prod/`)
- ses propres seuils de tolérance (`strict_validation`, `max_batch_size`)
- ses propres SLA d'incident (plus courts en production : une erreur
  CRITICAL doit être traitée en 1h en Prod contre 4h en UAT)

Le code métier (`pipeline.py`, `validator.py`, etc.) ne connaît **jamais**
directement l'environnement -- il reçoit uniquement la configuration
chargée par `config_loader.py`. C'est ce qui permet de garantir qu'on ne
peut pas "se tromper de base" par accident : on ne change que le paramètre
`--env`, jamais le code.

## Cycle de vie typique d'un changement (ex: nouvelle règle de validation)

```
1. Développement + test en local
2. Déploiement en UAT     -> tests fonctionnels avec les utilisateurs métier
3. Validation UAT OK      -> promotion vers PreProd
4. Déploiement en PreProd -> tests de charge, tests de non-régression
5. Validation PreProd OK  -> fenêtre de déploiement planifiée
6. Déploiement en Production -> supervision renforcée (hypercare)
```

Un Analyste Murex (fonctionnel ou technique) est impliqué dans les
étapes 2 à 4 en particulier : configuration/tests en UAT, validation
technique en PreProd, avant le passage en production porté par une
équipe dédiée (souvent appelée "Release Management" ou "Change Management").
