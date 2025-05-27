import os
from dotenv import load_dotenv

from sync_customers import sync_customers
from sync_products import sync_products
from sync_prices import sync_prices
from sync_subscriptions import sync_subscriptions
from sync_invoices import sync_invoices
from sync_charges import sync_charges
from sync_payment_methods import sync_payment_methods
from sync_payment_intents import sync_payment_intents

load_dotenv()

def main():
    print("🚀 Starting full sync from Stripe to PostgreSQL...\n")

    sync_customers()
    sync_products()
    sync_prices()
    sync_subscriptions()
    sync_invoices()
    sync_charges()
    sync_payment_methods()
    sync_payment_intents()

    print("\n✅ Sync complete!")

if __name__ == "__main__":
    main()
