"""
generate_fpml_messages.py
Simule le "Système A" (un système de trading/core banking) qui émet des
messages de confirmation de trade au format FpML simplifié (XML), à
destination du système comptable via le middleware d'intégration.

FpML (Financial products Markup Language) est un standard XML réel de
l'industrie financière pour l'échange de données sur produits dérivés.
Ce projet en simplifie fortement la structure à but pédagogique.

Certains messages sont volontairement malformés (champ manquant, XML
invalide) pour permettre de démontrer le comportement du middleware
face aux erreurs et la génération d'incidents.
"""

import os
import random
import uuid
from datetime import date, timedelta

OUTBOX_DIR = os.path.join(os.path.dirname(__file__), "outbox")

COUNTERPARTIES = ["CP_001", "CP_002", "CP_003", "CP_004"]
CURRENCIES = ["EUR", "USD", "GBP", "CHF"]
PRODUCTS = ["FX_FORWARD", "IRS"]


def _valid_fpml_message(trade_id, counterparty, currency, product, notional, trade_date):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<FpML version="5.simplified">
  <trade>
    <tradeHeader>
      <tradeId>{trade_id}</tradeId>
      <tradeDate>{trade_date}</tradeDate>
    </tradeHeader>
    <productType>{product}</productType>
    <counterpartyId>{counterparty}</counterpartyId>
    <notionalAmount currency="{currency}">{notional}</notionalAmount>
  </trade>
</FpML>
"""


def _malformed_missing_field(trade_id, counterparty, currency, product, notional, trade_date):
    """Simule un message avec un champ obligatoire manquant (counterpartyId absent)."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<FpML version="5.simplified">
  <trade>
    <tradeHeader>
      <tradeId>{trade_id}</tradeId>
      <tradeDate>{trade_date}</tradeDate>
    </tradeHeader>
    <productType>{product}</productType>
    <notionalAmount currency="{currency}">{notional}</notionalAmount>
  </trade>
</FpML>
"""


def _malformed_invalid_xml(trade_id, counterparty, currency, product, notional, trade_date):
    """Simule un message avec une balise XML mal fermée (XML invalide)."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<FpML version="5.simplified">
  <trade>
    <tradeHeader>
      <tradeId>{trade_id}</tradeId>
      <tradeDate>{trade_date}</tradeDate>
    </tradeHeader>
    <productType>{product}</productType>
    <counterpartyId>{counterparty}
    <notionalAmount currency="{currency}">{notional}</notionalAmount>
  </trade>
</FpML>
"""


def generate_messages(n=30, error_rate=0.15):
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    # Nettoie l'outbox précédente pour un test reproductible
    for f in os.listdir(OUTBOX_DIR):
        os.remove(os.path.join(OUTBOX_DIR, f))

    counts = {"valid": 0, "missing_field": 0, "invalid_xml": 0}

    for i in range(n):
        trade_id = f"TRD-{uuid.uuid4().hex[:8].upper()}"
        counterparty = random.choice(COUNTERPARTIES)
        currency = random.choice(CURRENCIES)
        product = random.choice(PRODUCTS)
        notional = round(random.uniform(500_000, 15_000_000), 2)
        trade_date = (date.today() - timedelta(days=random.randint(0, 5))).isoformat()

        roll = random.random()
        if roll < error_rate * 0.5:
            content = _malformed_missing_field(trade_id, counterparty, currency, product, notional, trade_date)
            counts["missing_field"] += 1
            suffix = "ERR-MISSING"
        elif roll < error_rate:
            content = _malformed_invalid_xml(trade_id, counterparty, currency, product, notional, trade_date)
            counts["invalid_xml"] += 1
            suffix = "ERR-XML"
        else:
            content = _valid_fpml_message(trade_id, counterparty, currency, product, notional, trade_date)
            counts["valid"] += 1
            suffix = "OK"

        filename = f"{trade_id}_{suffix}.xml"
        with open(os.path.join(OUTBOX_DIR, filename), "w") as f:
            f.write(content)

    print(f"[Source System] {n} messages FpML générés dans {OUTBOX_DIR}")
    print(f"[Source System] Répartition : {counts['valid']} valides, "
          f"{counts['missing_field']} champ manquant, {counts['invalid_xml']} XML invalide")
    return counts


if __name__ == "__main__":
    generate_messages(n=30)
