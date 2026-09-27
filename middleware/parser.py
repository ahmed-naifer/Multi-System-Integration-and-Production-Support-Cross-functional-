"""
parser.py
Parse un message FpML (XML) en dictionnaire Python exploitable.
Gère explicitement les erreurs de parsing (XML mal formé), qui sont
un incident réel et fréquent en intégration de systèmes bancaires.
"""

import xml.etree.ElementTree as ET


class ParsingError(Exception):
    """Levée quand un message ne peut pas être parsé (XML invalide)."""
    pass


def parse_fpml(xml_content, source_ref=""):
    """Parse le contenu XML et extrait les champs métier.
    Ne fait AUCUNE validation métier ici (c'est le rôle de validator.py) --
    ce module se contente de la structure technique du message."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ParsingError(f"XML mal formé dans '{source_ref}' : {e}")

    trade = root.find("trade")
    if trade is None:
        raise ParsingError(f"Balise <trade> absente dans '{source_ref}'")

    header = trade.find("tradeHeader")
    trade_id = header.findtext("tradeId") if header is not None else None
    trade_date = header.findtext("tradeDate") if header is not None else None

    product_type = trade.findtext("productType")
    counterparty_id = trade.findtext("counterpartyId")

    notional_elem = trade.find("notionalAmount")
    notional = notional_elem.text if notional_elem is not None else None
    currency = notional_elem.get("currency") if notional_elem is not None else None

    return {
        "trade_id": trade_id,
        "trade_date": trade_date,
        "product_type": product_type,
        "counterparty_id": counterparty_id,
        "notional": notional,
        "currency": currency,
        "source_ref": source_ref,
    }
