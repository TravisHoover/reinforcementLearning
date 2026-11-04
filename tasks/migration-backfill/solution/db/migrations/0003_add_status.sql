ALTER TABLE accounts ADD COLUMN status TEXT NOT NULL DEFAULT 'active';
UPDATE accounts SET status = 'inactive' WHERE deleted_at IS NOT NULL;
