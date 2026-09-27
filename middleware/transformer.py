"""
transformer.py
Transforme un message validé (format source FpML) vers le format
attendu par le système comptable cible -- le "mapping de champs"
au cœur de tout projet d'intégration bancaire.

Simplification pédagogique : chaque trade génère une écriture
comptable en partie double (débit/crédit) selon des comptes
génériques par classe d'actif.
"""

ACCOUNT_MAPPING = {
    "FX_FORWARD": {"debit_account": "1201-FX-POSITIONS", "credit_account": "4001-FX-COUNTERPARTY"},
    "IRS": {"debit_account": "1202-RATES-POSITIONS", "credit_account": "4002-RATES-COUNTERPARTY"},
}


def transform(message):
    """Transforme un message source validé en écriture comptable cible.
    Retourne un dictionnaire au format attendu par target_system.db."""
    accounts = ACCOUNT_MAPPING.get(message["product_type"])
    if accounts is None:
        # Ne devrait jamais arriver si validate() a été appelé avant,
        # mais on se protège quand même (défense en profondeur).
        raise ValueError(f"Pas de mapping comptable pour le produit '{message['product_type']}'")

    return {
        "trade_id": message["trade_id"],
        "trade_date": message["trade_date"],
        "counterparty_id": message["counterparty_id"],
        "product_type": message["product_type"],
        "currency": message["currency"],
        "notional": float(message["notional"]),
        "debit_account": accounts["debit_account"],
        "credit_account": accounts["credit_account"],
        "source_ref": message["source_ref"],
    }
