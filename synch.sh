#!/bin/bash

LOCAL_DIR="/home/ali/WildFire-Alert"
REMOTE_DIR="/info/raid-etu/m1/s2506992/WildFire-Alert"

if ping -c 1 fac-Skinner &> /dev/null; then
    CLUSTER="fac-Skinner"
    echo "Connexion au cluster sur le réseau de la fac..."
else
    CLUSTER="fac-Skinner-dist"
    echo "Connexion au cluster depuis l'extérieur..."
fi

# Synchronisation avec rsync
rsync -avz --exclude='.git' -e ssh "$LOCAL_DIR/" "$CLUSTER":"$REMOTE_DIR"

echo "Synchronisation terminée !"
