import pytest
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.utils.stripe_helpers import ensure_customer_exists

def test_ensure_deleted_customer_placeholder_created(db: Session):
    ghost_id = "cus_DELETED123"

    # Safety: should not exist
    existing = db.get(Customer, ghost_id)
    if existing:
        db.delete(existing)
        db.commit()

    # Ensure the customer does NOT exist
    assert db.get(Customer, ghost_id) is None

    # Run the logic
    ensure_customer_exists(db, ghost_id)
    db.commit()  # Required for persistence

    # Fetch again
    ghost = db.get(Customer, ghost_id)

    # ✅ Check all expected fields
    assert ghost is not None
    assert ghost.id == ghost_id
    assert ghost.deleted is True
    assert ghost.stripe_metadata.get("placeholder") is True
    assert ghost.email is None
    assert ghost.name is None
    assert ghost.created is None
