# Format de message : FpML simplifié

## Qu'est-ce que FpML ?

**FpML (Financial products Markup Language)** est un standard XML réel,
largement utilisé dans l'industrie financière pour décrire et échanger
des données sur les produits dérivés (swaps, forwards, options) entre
systèmes -- notamment entre un système de trading (comme Murex) et des
systèmes en aval (comptabilité, risque, référentiels de trades EMIR).

Ce projet utilise une **version très simplifiée** de FpML, à but
pédagogique : la structure réelle de la norme est bien plus riche
(des dizaines de champs optionnels, gestion de plusieurs legs pour un
swap, conventions de calendrier, etc.).

## Structure du message utilisé dans ce projet

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FpML version="5.simplified">
  <trade>
    <tradeHeader>
      <tradeId>TRD-XXXXXXXX</tradeId>
      <tradeDate>2026-09-27</tradeDate>
    </tradeHeader>
    <productType>FX_FORWARD</productType>
    <counterpartyId>CP_001</counterpartyId>
    <notionalAmount currency="USD">14665027.43</notionalAmount>
  </trade>
</FpML>
```

| Champ | Description | Obligatoire |
|---|---|---|
| `tradeId` | Identifiant unique de la transaction | Oui |
| `tradeDate` | Date de la transaction (ISO 8601) | Oui |
| `productType` | Type de produit (`FX_FORWARD` ou `IRS`) | Oui |
| `counterpartyId` | Identifiant de la contrepartie | Oui |
| `notionalAmount` (+ attribut `currency`) | Montant notionnel et devise | Oui |

## Autres standards réels d'échange bancaire (pour référence)

Ce projet se concentre sur FpML/XML, mais il existe d'autres standards
qu'un Analyste Murex technique rencontre en mission :

- **SWIFT MT (Message Type)** : format texte structuré plus ancien,
  encore massivement utilisé pour les paiements et confirmations
  (ex : MT300 pour une confirmation de change, MT320 pour un dépôt/prêt)
- **SWIFT MX (ISO 20022)** : successeur XML de SWIFT MT, de plus en plus
  adopté pour les paiements internationaux
- **FIX (Financial Information eXchange)** : standard pour les ordres
  et exécutions, plus utilisé côté Front Office/trading électronique

## Anomalies simulées dans ce projet

`generate_fpml_messages.py` injecte volontairement deux types de messages
invalides pour tester la robustesse du middleware :

1. **Champ manquant** (`_ERR-MISSING`) : la balise `<counterpartyId>` est
   absente -- simule un bug côté système émetteur ou un champ optionnel
   mal configuré
2. **XML invalide** (`_ERR-XML`) : une balise mal fermée -- simule une
   troncature réseau ou une erreur d'encodage lors de la génération du
   message côté source
