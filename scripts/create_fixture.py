import stripe
import os
import json
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

with open("fixtures/stripe_batch_fixture.json") as f:
    data = json.load(f)

customers = {}
products = {}
prices = {}


def get_or_create_customer(email, name):
    """Return existing customer by email, or create one."""
    existing = stripe.Customer.list(email=email, limit=1).data
    if existing:
        print(f"🔁 Existing customer found: {email} ({existing[0].id})")
        return existing[0]
    print(f"🆕 Creating customer: {email}")
    return stripe.Customer.create(name=name, email=email)


def get_or_create_product(name, description):
    """Return existing product by metadata key, or create one."""
    marker = name.lower().replace(" ", "_")
    existing = stripe.Product.list(active=True, limit=100).data
    for product in existing:
        if product.metadata.get("tag") == marker:
            print(f"🔁 Existing product found: {name} ({product.id})")
            return product
    print(f"🆕 Creating product: {name}")
    return stripe.Product.create(
        name=name,
        description=description,
        metadata={"tag": marker}
    )


def get_or_create_price(amount, currency, interval, product_id):
    """Return existing price by amount/currency/interval, or create one."""
    existing_prices = stripe.Price.list(product=product_id, active=True, limit=100).data
    for price in existing_prices:
        if (
            price.unit_amount == amount and
            price.currency == currency and
            price.get("recurring", {}).get("interval") == interval
        ):
            print(f"🔁 Existing price: {amount / 100:.2f} {currency}/{interval} ({price.id})")
            return price
    print(f"🆕 Creating price: {amount / 100:.2f} {currency}/{interval}")
    return stripe.Price.create(
        unit_amount=amount,
        currency=currency,
        recurring={"interval": interval},
        product=product_id
    )


# 1. Create Customers
for entry in data["customers"]:
    customer = get_or_create_customer(entry["email"], entry["name"])
    customers[entry["email"]] = customer.id
    print(f"✅ Customer ready: {entry['name']} ({customer.id})")

# 2. Create Products and Prices
for prod in data["products"]:
    product = get_or_create_product(prod["name"], prod["description"])
    products[prod["name"]] = product.id

    for pr in prod["prices"]:
        price = get_or_create_price(
            amount=pr["amount"],
            currency=pr["currency"],
            interval=pr["interval"],
            product_id=product.id
        )
        prices[(prod["name"], pr["amount"])] = price.id

def subscription_exists(customer_id, price_id):
    """Check if a subscription already exists for a customer with the same price."""
    existing_subs = stripe.Subscription.list(customer=customer_id, status="all", limit=100).data
    for sub in existing_subs:
        for item in sub["items"]["data"]:
            if item["price"]["id"] == price_id:
                print(f"🔁 Subscription already exists for {customer_id} with price {price_id} → {sub.id}")
                return True
    return False


# 3. Create Subscriptions
for sub in data["subscriptions"]:
    customer_id = customers[sub["customer_email"]]
    product_id = products[sub["product_name"]]

    price_id = None
    for (prod_name, amount), pid in prices.items():
        if prod_name == sub["product_name"]:
            price_id = pid
            break

    if not price_id:
        print(f"❌ No price found for {sub['product_name']}")
        continue

    # Skip if subscription already exists
    if subscription_exists(customer_id, price_id):
        continue

    payment_method = stripe.PaymentMethod.create(
        type="card",
        card={"token": "tok_visa"}
    )

    stripe.PaymentMethod.attach(payment_method.id, customer=customer_id)

    stripe.Customer.modify(
        customer_id,
        invoice_settings={"default_payment_method": payment_method.id}
    )

    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        cancel_at_period_end=False
    )

    print(f"✅ Active subscription for {sub['customer_email']}: {subscription.id}")

