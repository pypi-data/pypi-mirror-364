#!/bin/bash

# Usage function
usage() {
    echo "Usage: $0 -p PROJECT_NAME [-n NAMESPACE] [-h HOST]"
    echo "  -p: Project name to create API keys for"
    echo "  -n: Kubernetes namespace where LangFuse is deployed (default: ai-observability)"
    echo "  -h: LangFuse host (default: http://langfuse.ai-observability.svc.cluster.local:3000)"
    exit 1
}

# Default values
NAMESPACE="ai-observability"
HOST="http://langfuse.ai-observability.svc.cluster.local:3000"

# Parse command line arguments
while getopts "p:n:h:" opt; do
    case $opt in
        p) PROJECT_NAME="$OPTARG";;
        n) NAMESPACE="$OPTARG";;
        h) HOST="$OPTARG";;
        *) usage;;
    esac
done

# Check if project name is provided
if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    usage
fi

# Get admin credentials from the running LangFuse instance
echo "Getting admin credentials from LangFuse deployment..."
ADMIN_EMAIL=$(kubectl get configmap -n $NAMESPACE langfuse-config -o jsonpath='{.data.LANGFUSE_INIT_USER_EMAIL}')
ADMIN_PASSWORD=$(kubectl get configmap -n $NAMESPACE langfuse-config -o jsonpath='{.data.LANGFUSE_INIT_USER_PASSWORD}')

if [ -z "$ADMIN_EMAIL" ] || [ -z "$ADMIN_PASSWORD" ]; then
    echo "Error: Could not get admin credentials from LangFuse configmap"
    exit 1
fi

# Get auth token
echo "Getting authentication token..."
AUTH_RESPONSE=$(curl -s -X POST "$HOST/api/auth/signin/credentials" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

AUTH_TOKEN=$(echo $AUTH_RESPONSE | jq -r '.token')

if [ -z "$AUTH_TOKEN" ] || [ "$AUTH_TOKEN" = "null" ]; then
    echo "Error: Failed to get authentication token"
    echo "Response: $AUTH_RESPONSE"
    exit 1
fi

# Create new API keys
echo "Creating new API keys for project: $PROJECT_NAME"
API_KEY_RESPONSE=$(curl -s -X POST "$HOST/api/projects/$PROJECT_NAME/api-keys" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -d "{\"name\":\"$(date +%Y-%m-%d)-auto-generated\"}")

# Extract API keys
PUBLIC_KEY=$(echo $API_KEY_RESPONSE | jq -r '.publicKey')
SECRET_KEY=$(echo $API_KEY_RESPONSE | jq -r '.secretKey')

if [ -z "$PUBLIC_KEY" ] || [ "$PUBLIC_KEY" = "null" ] || [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "null" ]; then
    echo "Error: Failed to create API keys"
    echo "Response: $API_KEY_RESPONSE"
    exit 1
fi

# Output the keys
echo "Successfully created new API keys:"
echo "Public Key: $PUBLIC_KEY"
echo "Secret Key: $SECRET_KEY"
echo "Host: $HOST"

# Create a tfvars file
echo "Creating terraform.tfvars file..."
cat > terraform.tfvars << EOF
# Developer Environment Configuration
region = "us-west-2"
namespace = "$NAMESPACE"

# LangFuse API Credentials
langfuse_public_key = "$PUBLIC_KEY"
langfuse_secret_key = "$SECRET_KEY"
langfuse_host = "$HOST"

# Developer Environment Tags
tags = {
  Environment = "developer"
  Service     = "langfuse"
  Cluster     = "developer-eks"
}
EOF

echo "Created terraform.tfvars file with the new API keys" 