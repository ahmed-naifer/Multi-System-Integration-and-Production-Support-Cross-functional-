"""
validator.py
Applique les règles métier de validation sur un message déjà parsé
(structure technique OK, mais contenu à vérifier).
"""

KNOWN_COUNTERPARTIES = {"CP_001", "CP_002", "CP_003", "CP_004"}
KNOWN_CURRENCIES = {"EUR", "USD", "GBP", "CHF", "JPY"}
KNOWN_PRODUCTS = {"FX_FORWARD", "IRS"}


class ValidationError(Exception):
    """Levée quand un message parsé viole une règle métier bloquante."""
    pass


def validate(message):
    """Valide un message déjà parsé. Lève ValidationError au premier
    champ obligatoire manquant ou invalide (fail-fast), avec un message
    explicite -- comme le ferait un vrai contrôle de conformité avant
    intégration en comptabilité."""

    if not message.get("trade_id"):
        raise ValidationError("Champ 'tradeId' manquant")

    if not message.get("counterparty_id"):
        raise ValidationError(f"Champ 'counterpartyId' manquant pour le trade {message.get('trade_id')}")

    if message["counterparty_id"] not in KNOWN_COUNTERPARTIES:
        raise ValidationError(
            f"Contrepartie inconnue '{message['counterparty_id']}' pour le trade {message.get('trade_id')}"
        )

    if not message.get("currency"):
        raise ValidationError(f"Devise manquante pour le trade {message.get('trade_id')}")

    if message["currency"] not in KNOWN_CURRENCIES:
        raise ValidationError(
            f"Devise inconnue '{message['currency']}' pour le trade {message.get('trade_id')}"
        )

    if message.get("product_type") not in KNOWN_PRODUCTS:
        raise ValidationError(
            f"Type de produit inconnu '{message.get('product_type')}' pour le trade {message.get('trade_id')}"
        )

    try:
        notional = float(message.get("notional", ""))
        if notional <= 0:
            raise ValidationError(f"Notional invalide ({notional}) pour le trade {message.get('trade_id')}")
    except (TypeError, ValueError):
        raise ValidationError(f"Notional non numérique pour le trade {message.get('trade_id')}")

    return True
