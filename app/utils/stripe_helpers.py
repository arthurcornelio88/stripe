# app/utils/stripe_helpers.py
from app.models.customer import Customer

def ensure_customer_exists(db, customer_id: str):
    """Create a placeholder customer in DB if it doesn't exist (e.g. deleted Stripe customer)"""
    if customer_id and not db.get(Customer, customer_id):
        print(f"👻 Creating placeholder for deleted customer: {customer_id}")
        ghost = Customer(
            id=customer_id,
            deleted=True,
            email=None,
            name=None,
            livemode=False,
            created=None,
            stripe_metadata={"placeholder": True},
        )
        db.add(ghost)
