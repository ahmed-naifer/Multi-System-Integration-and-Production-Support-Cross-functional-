# Cahier de Recette — Pipeline d'Intégration

| ID | Scénario | Étapes | Résultat attendu | Statut |
|---|---|---|---|---|
| INT-01 | Message valide traité de bout en bout | Parser un message FpML valide | Le message est parsé, validé, transformé, et une écriture apparaît dans `accounting_entries` | ✅ PASS |
| INT-02 | Détection XML mal formé | Fournir un message avec une balise mal fermée | `ParsingError` levée, message déplacé vers `failed/`, incident `CRITICAL` créé | ✅ PASS |
| INT-03 | Détection champ obligatoire manquant | Fournir un message sans `counterpartyId` | `ValidationError` levée, message déplacé vers `failed/`, incident `HIGH` créé | ✅ PASS |
| INT-04 | Détection contrepartie inconnue | Fournir un message avec `counterpartyId` hors référentiel | `ValidationError` levée avec message explicite | ✅ PASS |
| INT-05 | Détection notional invalide | Fournir un message avec `notional` négatif ou non numérique | `ValidationError` levée | ✅ PASS |
| INT-06 | Mapping comptable FX_FORWARD | Transformer un message `FX_FORWARD` validé | `debit_account = 1201-FX-POSITIONS`, `credit_account = 4001-FX-COUNTERPARTY` | ✅ PASS |
| INT-07 | Mapping comptable IRS | Transformer un message `IRS` validé | `debit_account = 1202-RATES-POSITIONS`, `credit_account = 4002-RATES-COUNTERPARTY` | ✅ PASS |
| INT-08 | Isolation des environnements | Lancer le pipeline avec `--env uat` puis `--env prod` | Deux bases de données distinctes créées (`data/uat/` et `data/prod/`), aucune donnée mélangée | ✅ PASS |
| INT-09 | SLA différencié par sévérité | Générer un incident `CRITICAL` et un incident `HIGH` | Le `sla_deadline` du `CRITICAL` est plus proche dans le temps que celui du `HIGH` | ✅ PASS |
| INT-10 | Piste d'audit des fichiers | Lancer le pipeline sur un lot mixte (valides + invalides) | Chaque fichier source se retrouve soit dans `processed/`, soit dans `failed/` -- aucun fichier "perdu" | ✅ PASS |
| INT-11 | Exécution orchestrée complète | Lancer `run_integration.sh uat` | Code de sortie 0, log généré, résumé des incidents ouverts affiché en fin d'exécution | ✅ PASS |
| INT-12 | Rejet d'un environnement invalide | Lancer `run_integration.sh staging` (environnement non prévu) | Le script s'arrête avec un message d'erreur explicite, sans tenter de traiter quoi que ce soit | ✅ PASS |

---

### Méthodologie

Ces cas de test valident les 3 dimensions critiques d'une plateforme
d'intégration bancaire : **robustesse face aux erreurs** (INT-02 à
INT-05), **exactitude du mapping métier** (INT-06, INT-07), et
**isolation/traçabilité des environnements** (INT-08 à INT-12).
