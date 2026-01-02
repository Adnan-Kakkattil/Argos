"""
Utility Functions
"""
import random
import string
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.tenant import Tenant
from backend.models.company import Company
from backend.models.branch import Branch

def generate_org_id(prefix: str = "", length: Optional[int] = None, db: Optional[Session] = None) -> str:
    """
    Generate unique 5-8 character alphanumeric Org ID
    
    Args:
        prefix: Optional prefix for the org_id (e.g., "TNT", "CMP", "BRN")
        length: Optional fixed length (default: random between 5-8)
        db: Database session for uniqueness check
    
    Returns:
        Unique org_id string
    """
    if length is None:
        length = random.randint(5, 8)
    
    # Ensure length accounts for prefix
    if prefix:
        length = max(length, len(prefix) + 3)  # At least 3 random chars after prefix
    
    chars = string.ascii_uppercase + string.digits
    
    max_attempts = 100
    for _ in range(max_attempts):
        # Generate random part
        random_part_length = length - len(prefix)
        random_part = ''.join(random.choices(chars, k=random_part_length))
        org_id = prefix + random_part
        
        # Check uniqueness if database session provided
        if db is not None:
            # Check in tenants
            if db.query(Tenant).filter(Tenant.tenant_org_id == org_id).first():
                continue
            # Check in companies
            if db.query(Company).filter(Company.company_org_id == org_id).first():
                continue
            # Check in branches
            if db.query(Branch).filter(Branch.branch_org_id == org_id).first():
                continue
        
        return org_id
    
    # Fallback: add timestamp if uniqueness can't be achieved
    import time
    timestamp = str(int(time.time()))[-4:]
    return prefix + timestamp

def is_org_id_unique(org_id: str, db: Session) -> bool:
    """
    Check if org_id is globally unique across all tables
    
    Args:
        org_id: The org_id to check
        db: Database session
    
    Returns:
        True if unique, False otherwise
    """
    # Check tenants
    if db.query(Tenant).filter(Tenant.tenant_org_id == org_id).first():
        return False
    # Check companies
    if db.query(Company).filter(Company.company_org_id == org_id).first():
        return False
    # Check branches
    if db.query(Branch).filter(Branch.branch_org_id == org_id).first():
        return False
    
    return True

