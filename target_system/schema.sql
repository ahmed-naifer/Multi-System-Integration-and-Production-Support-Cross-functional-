-- =============================================================
-- Système comptable cible (Système B)
-- Reçoit les écritures transformées par le middleware d'intégration.
-- =============================================================

DROP TABLE IF EXISTS accounting_entries;

CREATE TABLE accounting_entries (
    entry_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id             TEXT NOT NULL UNIQUE,
    trade_date            DATE NOT NULL,
    counterparty_id        TEXT NOT NULL,
    product_type            TEXT NOT NULL,
    currency                TEXT NOT NULL,
    notional                 NUMERIC NOT NULL,
    debit_account             TEXT NOT NULL,
    credit_account             TEXT NOT NULL,
    source_ref                  TEXT,
    integrated_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
