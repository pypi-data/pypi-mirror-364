#!/bin/bash
set -e
PASSWORD="$1"
HASH=$(echo -n "$PASSWORD" | htpasswd -BinC 10 admin | cut -d: -f2)
echo "{\"hash\": \"$HASH\"}"
