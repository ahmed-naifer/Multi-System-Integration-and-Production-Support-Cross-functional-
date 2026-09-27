"""
db.py (target_system)
Connexion au système comptable cible. Le chemin de la base dépend de
l'environnement (UAT/PreProd/Prod) fourni par la configuration --
c'est la mise en pratique concrète de l'isolation d'environnements.
"""

import sqlite3
import os

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


def get_connection(db_relative_path):
    """Ouvre une connexion vers la base de l'environnement demandé.
    db_relative_path vient de la config (ex: 'data/uat/accounting.db')."""
    db_path = os.path.join(PROJECT_ROOT, db_relative_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_target_system(db_relative_path):
    conn = get_connection(db_relative_path)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"[Target System] Base comptable initialisée : {db_relative_path}")


def insert_entry(db_relative_path, entry):
    conn = get_connection(db_relative_path)
    conn.execute(
        """INSERT INTO accounting_entries
           (trade_id, trade_date, counterparty_id, product_type, currency,
            notional, debit_account, credit_account, source_ref)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (entry["trade_id"], entry["trade_date"], entry["counterparty_id"],
         entry["product_type"], entry["currency"], entry["notional"],
         entry["debit_account"], entry["credit_account"], entry["source_ref"]),
    )
    conn.commit()
    conn.close()
