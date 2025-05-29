#!/bin/bash

# Charge les variables d'environnement
set -o allexport
source .env.dev
set +o allexport

mkdir -p data/imported_stripe_data

echo 'Fetching customers...'
curl https://api.stripe.com/v1/customers \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  --data-urlencode "expand[]=data.invoice_settings.default_payment_method" \
  -o data/imported_stripe_data/customers.json

echo 'Fetching products...'
curl https://api.stripe.com/v1/products \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  -o data/imported_stripe_data/products.json

echo 'Fetching prices...'
curl https://api.stripe.com/v1/prices \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  --data-urlencode "expand[]=data.product" \
  -o data/imported_stripe_data/prices.json

echo 'Fetching subscriptions...'
curl https://api.stripe.com/v1/subscriptions \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  --data-urlencode "expand[]=data.customer" \
  --data-urlencode "expand[]=data.items.data.price" \
  -o data/imported_stripe_data/subscriptions.json

echo 'Fetching invoices...'
curl https://api.stripe.com/v1/invoices \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  --data-urlencode "expand[]=data.customer" \
  -o data/imported_stripe_data/invoices.json

echo 'Fetching charges...'
curl https://api.stripe.com/v1/charges \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  --data-urlencode "expand[]=data.payment_intent" \
  -o data/imported_stripe_data/charges.json

echo 'Fetching payment_intents...'
curl https://api.stripe.com/v1/payment_intents \
  -u $STRIPE_API_KEY: \
  -G \
  --data-urlencode "limit=100" \
  -o data/imported_stripe_data/payment_intents.json

