# Database Migration Scripts

## migrate_database.py

This script updates the database schema to match the current models.

### What it does:

1. **Updates Agent Enum Values**
   - Converts `org_type` enum from lowercase ('tenant', 'company', 'branch') to uppercase ('TENANT', 'COMPANY', 'BRANCH')
   - Converts `status` enum from lowercase ('online', 'offline') to uppercase ('ONLINE', 'OFFLINE')
   - Updates existing data to match new enum values

2. **Safe Migration**
   - Checks current enum values before updating
   - Updates existing data first to avoid constraint errors
   - Provides detailed feedback on what was changed

### Usage:

```bash
python scripts/migrate_database.py
```

### When to run:

- After updating enum values in models
- After schema changes that require data migration
- When enum values don't match between code and database

### Notes:

- The script is idempotent (safe to run multiple times)
- It will only update what needs to be changed
- Always backup your database before running migrations in production

## Future Migrations

To add new migrations:

1. Add a new function in `migrate_database.py`
2. Call it from the `main()` function
3. Follow the same pattern: check first, then update

Example:
```python
def migrate_new_feature(engine):
    """Add new feature migration"""
    print("Migrating new feature...")
    # Check if migration is needed
    # Update schema/data
    print("✅ Migration complete")
```

