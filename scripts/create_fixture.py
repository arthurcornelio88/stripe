import stripe
import os
import json
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Charger les données depuis le fichier JSON
with open("fixtures/stripe_batch_fixture.json") as f:
    data = json.load(f)

# Dictionnaires pour stocker les objets créés
customers = {}
products = {}
prices = {}

# Créer les clients
for cust in data["customers"]:
    customer = stripe.Customer.create(
        name=cust["name"],
        email=cust["email"]
    )
    customers[cust["email"]] = customer.id
    print(f"✅ Client créé : {cust['name']} ({customer.id})")

# Créer les produits et les prix
for prod in data["products"]:
    product = stripe.Product.create(
        name=prod["name"],
        description=prod["description"]
    )
    products[prod["name"]] = product.id
    for pr in prod["prices"]:
        price = stripe.Price.create(
            unit_amount=pr["amount"],
            currency=pr["currency"],
            recurring={"interval": pr["interval"]},
            product=product.id
        )
        prices[(prod["name"], pr["amount"])] = price.id
        print(f"✅ Prix créé pour {prod['name']}: {price.id}")

# Créer les abonnements
for sub in data["subscriptions"]:
    customer_id = customers[sub["customer_email"]]
    product_id = products[sub["product_name"]]
    # Récupérer le price_id correspondant
    price_id = None
    for (prod_name, amount), pid in prices.items():
        if prod_name == sub["product_name"]:
            price_id = pid
            break
    if not price_id:
        print(f"❌ Prix non trouvé pour {sub['product_name']}")
        continue

    # Utiliser une méthode de paiement de test
    payment_method = stripe.PaymentMethod.create(
        type="card",
        card={"token": "tok_visa"}
    )

    # Attacher la méthode de paiement au client
    stripe.PaymentMethod.attach(
        payment_method.id,
        customer=customer_id
    )

    # Définir la méthode de paiement par défaut
    stripe.Customer.modify(
        customer_id,
        invoice_settings={"default_payment_method": payment_method.id}
    )

    # Créer l'abonnement
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        cancel_at_period_end=False
    )
    print(f"✅ Abonnement créé pour {sub['customer_email']}: {subscription.id}")
