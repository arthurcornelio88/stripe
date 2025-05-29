#!/bin/bash

# Charge les variables d'environnement
set -o allexport
source .env.dev
set +o allexport

# Dossier contenant le JSON des clients
CUSTOMERS_FILE="data/imported_stripe_data/customers.json"
OUTPUT_DIR="data/imported_stripe_data/payment_methods"
MERGED_FILE="data/imported_stripe_data/payment_methods.json"

mkdir -p "$OUTPUT_DIR"

# Vérification que le fichier existe
if [ ! -f "$CUSTOMERS_FILE" ]; then
  echo "❌ Fichier introuvable : $CUSTOMERS_FILE"
  exit 1
fi

# Extraction
echo "📥 Extraction des moyens de paiement pour chaque client..."
for customer_id in $(jq -r '.data[].id' "$CUSTOMERS_FILE"); do
  echo "🔄 Récupération des payment_methods pour $customer_id..."
  curl https://api.stripe.com/v1/payment_methods \
    -u $STRIPE_API_KEY: \
    -G \
    --data-urlencode "limit=100" \
    --data-urlencode "customer=$customer_id" \
    -o "$OUTPUT_DIR/payment_methods_${customer_id}.json"
done

echo "🧩 Fusion des fichiers en un seul JSON..."
echo '{"object": "list", "data": [' > "$MERGED_FILE"
first=true
for f in "$OUTPUT_DIR"/payment_methods_*.json; do
  if [ -f "$f" ]; then
    # Extraire et filtrer les objets non vides
    entries=$(jq -c '.data[]?' "$f")
    if [ -n "$entries" ]; then
      while IFS= read -r line; do
        if [ "$first" = true ]; then
          first=false
        else
          echo "," >> "$MERGED_FILE"
        fi
        echo "$line" >> "$MERGED_FILE"
      done <<< "$entries"
    fi
  fi
done
echo "]}" >> "$MERGED_FILE"

echo "✅ Fichier fusionné propre : $MERGED_FILE"

