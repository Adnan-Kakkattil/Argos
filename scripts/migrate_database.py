"""
Database Migration Script
Updates database schema to match current models
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from backend.core.config import settings

def get_engine():
    """Get database engine"""
    return create_engine(settings.database_url, pool_pre_ping=True)

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_table_exists(engine, table_name):
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_enum_values(engine, table_name, column_name):
    """Get current enum values for a column"""
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT COLUMN_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """))
        row = result.fetchone()
        if row:
            enum_str = row[0]
            # Extract enum values from string like "enum('TENANT','COMPANY','BRANCH')"
            if enum_str.startswith("enum("):
                values = enum_str[5:-1].replace("'", "").split(",")
                return [v.strip() for v in values]
        return None

def migrate_agents_enum(engine):
    """Update agents table enum values to uppercase"""
    print("Checking agents table enum values...")
    
    # Check org_type enum
    org_type_values = get_enum_values(engine, 'agents', 'org_type')
    print(f"Current org_type enum values: {org_type_values}")
    
    if org_type_values and org_type_values != ['TENANT', 'COMPANY', 'BRANCH']:
        print("Updating org_type enum to uppercase values...")
        with engine.connect() as conn:
            # MySQL doesn't support direct enum modification, so we need to alter the column
            try:
                conn.execute(text("""
                    ALTER TABLE agents 
                    MODIFY COLUMN org_type ENUM('TENANT', 'COMPANY', 'BRANCH') NOT NULL
                """))
                conn.commit()
                print("✅ Updated org_type enum to uppercase values")
            except Exception as e:
                print(f"⚠️  Error updating org_type enum: {e}")
                print("   You may need to update existing data first")
                conn.rollback()
    else:
        print("✅ org_type enum values are correct")
    
    # Check status enum
    status_values = get_enum_values(engine, 'agents', 'status')
    print(f"Current status enum values: {status_values}")
    
    if status_values and status_values != ['ONLINE', 'OFFLINE']:
        print("Updating status enum to uppercase values...")
        with engine.connect() as conn:
            try:
                conn.execute(text("""
                    ALTER TABLE agents 
                    MODIFY COLUMN status ENUM('ONLINE', 'OFFLINE') DEFAULT 'OFFLINE' NOT NULL
                """))
                conn.commit()
                print("✅ Updated status enum to uppercase values")
            except Exception as e:
                print(f"⚠️  Error updating status enum: {e}")
                print("   You may need to update existing data first")
                conn.rollback()
    else:
        print("✅ status enum values are correct")

def update_existing_agent_data(engine):
    """Update existing agent data to use uppercase enum values"""
    print("\nUpdating existing agent data...")
    
    with engine.connect() as conn:
        # Update org_type values
        try:
            result = conn.execute(text("""
                UPDATE agents 
                SET org_type = UPPER(org_type)
                WHERE org_type IN ('tenant', 'company', 'branch')
            """))
            conn.commit()
            if result.rowcount > 0:
                print(f"✅ Updated {result.rowcount} agent org_type values to uppercase")
            else:
                print("✅ No agent org_type values needed updating")
        except Exception as e:
            print(f"⚠️  Error updating org_type data: {e}")
            conn.rollback()
        
        # Update status values
        try:
            result = conn.execute(text("""
                UPDATE agents 
                SET status = UPPER(status)
                WHERE status IN ('online', 'offline')
            """))
            conn.commit()
            if result.rowcount > 0:
                print(f"✅ Updated {result.rowcount} agent status values to uppercase")
            else:
                print("✅ No agent status values needed updating")
        except Exception as e:
            print(f"⚠️  Error updating status data: {e}")
            conn.rollback()

def main():
    """Main migration function"""
    print("=" * 60)
    print("Database Migration Script")
    print("=" * 60)
    
    try:
        engine = get_engine()
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.scalar()
            print(f"\n✅ Connected to database: {db_name}")
        
        # Check if agents table exists
        if not check_table_exists(engine, 'agents'):
            print("\n⚠️  Agents table does not exist. Run database/schema.sql first.")
            return
        
        # Update existing data first (to avoid enum constraint errors)
        update_existing_agent_data(engine)
        
        # Update enum definitions
        migrate_agents_enum(engine)
        
        print("\n" + "=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

