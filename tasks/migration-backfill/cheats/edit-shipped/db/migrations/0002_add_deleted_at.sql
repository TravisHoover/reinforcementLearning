ALTER TABLE accounts ADD COLUMN deleted_at TEXT;
ALTER TABLE accounts ADD COLUMN status TEXT NOT NULL DEFAULT 'active';
