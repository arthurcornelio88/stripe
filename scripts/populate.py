import stripe
import os
import json
import argparse
from utils import load_project_env

ENV = load_project_env()
stripe.api_key = os.getenv("STRIPE_API_KEY")

FIXTURE_PATH = "fixtures/stripe_batch_fixture.json"


def load_fixture(path):
    with open(path) as f:
        return json.load(f)


def get_or_create_customer(email, name):
    existing = stripe.Customer.list(email=email, limit=1).data
    if existing:
        print(f"🔁 Existing customer found: {email} ({existing[0].id})")
        return existing[0]
    print(f"🆕 Creating customer: {email}")
    return stripe.Customer.create(name=name, email=email)


def get_or_create_product(name, description):
    marker = name.lower().replace(" ", "_")
    existing = stripe.Product.list(active=True, limit=100).data
    for product in existing:
        if product.metadata.get("tag") == marker:
            print(f"🔁 Existing product found: {name} ({product.id})")
            return product
    print(f"🆕 Creating product: {name}")
    return stripe.Product.create(name=name, description=description, metadata={"tag": marker})


def get_or_create_price(amount, currency, interval, product_id):
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


def delete_existing_subscriptions(customer_id):
    subscriptions = stripe.Subscription.list(customer=customer_id, limit=100).data
    for sub in subscriptions:
        print(f"🗑️ Deleting subscription: {sub.id}")
        stripe.Subscription.delete(sub.id)


def subscription_exists(customer_id, price_id):
    subscriptions = stripe.Subscription.list(customer=customer_id, status="all", limit=100).data
    for sub in subscriptions:
        for item in sub["items"]["data"]:
            if item["price"]["id"] == price_id:
                print(f"🔁 Subscription already exists for {customer_id} with price {price_id} → {sub.id}")
                return True
    return False


def run_populate(fixture, force=False):
    customers = {}
    products = {}
    prices = {}

    for entry in fixture["customers"]:
        customer = get_or_create_customer(entry["email"], entry["name"])
        customers[entry["email"]] = customer.id
        print(f"✅ Customer ready: {entry['name']} ({customer.id})")

    for prod in fixture["products"]:
        product = get_or_create_product(prod["name"], prod["description"])
        products[prod["name"]] = product.id
        for pr in prod["prices"]:
            price = get_or_create_price(pr["amount"], pr["currency"], pr["interval"], product.id)
            prices[(prod["name"], pr["amount"])] = price.id

    for sub in fixture["subscriptions"]:
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

        if force:
            delete_existing_subscriptions(customer_id)
        else:
            if subscription_exists(customer_id, price_id):
                continue

        payment_method = stripe.PaymentMethod.create(type="card", card={"token": "tok_visa"})
        stripe.PaymentMethod.attach(payment_method.id, customer=customer_id)
        stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": payment_method.id})

        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            cancel_at_period_end=False
        )
        print(f"✅ Subscription created for {sub['customer_email']}: {subscription.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate Stripe sandbox with test data.")
    parser.add_argument("--force", action="store_true", help="Force deletion of existing subscriptions.")
    parser.add_argument("--fixture", default=FIXTURE_PATH, help="Path to the JSON fixture file.")
    args = parser.parse_args()

    fixture_data = load_fixture(args.fixture)
    account = stripe.Account.retrieve()
    print(f"🌍 Stripe account: {account.get('id')} | {account.get('business_type', 'n/a')} | {account.get('email', 'n/a')}")
    run_populate(fixture_data, force=args.force)
