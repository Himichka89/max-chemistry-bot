#!/usr/bin/env bash
set -euo pipefail

python -m pip install -r requirements.txt

CERT_URL="https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer"
CERT_RAW="/tmp/russian_trusted_root_ca.cer"
CERT_PEM="/tmp/russian_trusted_root_ca.pem"
EXPECTED_SHA256="D26D2D0231B7C39F92CC738512BA54103519E4405D68B5BD703E9788CA8ECF31"

# gu-st.ru itself can require the Russian trusted CA, so bootstrap download
# is allowed without TLS verification ONLY for this certificate file.
# Authenticity is then enforced by the pinned SHA-256 fingerprint below.
curl -kfsSL "$CERT_URL" -o "$CERT_RAW"

# Accept either PEM or DER input and normalize to PEM.
if grep -q "BEGIN CERTIFICATE" "$CERT_RAW" 2>/dev/null; then
  cp "$CERT_RAW" "$CERT_PEM"
else
  openssl x509 -inform DER -in "$CERT_RAW" -out "$CERT_PEM"
fi

ACTUAL_SHA256="$(openssl x509 -in "$CERT_PEM" -noout -fingerprint -sha256 \
  | sed 's/^sha256 Fingerprint=//I; s/://g; s/[[:space:]]//g' \
  | tr '[:lower:]' '[:upper:]')"

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
  echo "ERROR: Russian Trusted Root CA fingerprint mismatch"
  echo "Expected: $EXPECTED_SHA256"
  echo "Actual:   $ACTUAL_SHA256"
  exit 1
fi

CA_BUNDLE="$(python -m certifi)"
cat "$CERT_PEM" >> "$CA_BUNDLE"

echo "Russian Trusted Root CA added to Python CA bundle."
echo "Verified SHA-256: $ACTUAL_SHA256"
