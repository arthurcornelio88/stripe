import pytest
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.utils.stripe_helpers import ensure_customer_exists

def test_ensure_deleted_customer_placeholder_created(test_db: Session):
    ghost_id = "cus_DELETED123"

    # Safety: should not exist
    existing = test_db.get(Customer, ghost_id)
    if existing:
        test_db.delete(existing)
        test_db.commit()

    # Ensure the customer does NOT exist
    assert test_db.get(Customer, ghost_id) is None

    # Run the logic
    ensure_customer_exists(test_db, ghost_id)
    test_db.commit()  # Required for persistence

    # Fetch again
    ghost = test_db.get(Customer, ghost_id)

    # ✅ Check all expected fields
    assert ghost is not None
    assert ghost.id == ghost_id
    assert ghost.deleted is True
    assert ghost.stripe_metadata.get("placeholder") is True
    assert ghost.email is None
    assert ghost.name is None
    assert ghost.created is None
