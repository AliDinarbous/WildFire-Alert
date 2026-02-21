# 🔥 Wildfire Risk Predictor – Mobile Application

## 📌 Description du projet

Ce projet consiste en le développement d’une application mobile intelligente permettant d’évaluer le **risque d’incendie naturel** à partir de la localisation de l’utilisateur.

L’application combine :

- 📱 Un front-end mobile en Java natif  
- ☁️ Un back-end intelligent  
- 🤖 Un modèle de Machine Learning entraîné via une pipeline AutoML  
- 📚 Un système RAG (Retrieval-Augmented Generation) pour contextualiser les prédictions  

L’objectif est de fournir une estimation probabiliste du risque d’incendie, accompagnée d’un contexte basé sur des incendies historiques similaires et des recommandations adaptées.

---

## 🏗️ Architecture Générale

### 1️⃣ Front-end (Mobile – Java natif)

L’utilisateur peut :

- Appuyer sur **“Évaluer le risque”**
- Obtenir :
  - Une probabilité d’incendie  
  - Un contexte explicatif  
  - Des recommandations  

Deux rôles sont définis :

#### 👤 Utilisateur
- Lance l’évaluation du risque  
- Consulte les résultats  

#### 👨‍💼 Administrateur
- Charge un dataset  
- Lance l’entraînement du modèle  
- Évalue les performances  
- Consulte la version du modèle  
- Réinitialise le modèle  

---

### 2️⃣ Back-end

Le back-end effectue les opérations suivantes :

1. 📍 Récupération de la localisation utilisateur  
2. 🛰️ Appel d’une API d’images satellites pour récupérer l’image de la zone  
3. 🌦️ Appel d’une API météo pour récupérer les données climatiques  
4. 🔄 Prétraitement et formatage des données  
5. 🤖 Envoi des données au modèle de Machine Learning  
6. 📊 Récupération d’une probabilité de risque d’incendie  

---

## 🤖 Machine Learning & AutoML

Le modèle de prédiction est entraîné via une **pipeline AutoML** déjà implémentée.

Cette pipeline :

- Charge le dataset  
- Nettoie les données  
- Effectue le feature engineering  
- Teste plusieurs modèles  
- Optimise le meilleur modèle  
- Sauvegarde la version finale  

L’objectif est d’automatiser entièrement le cycle ML.

---

## 📚 Système RAG (Retrieval-Augmented Generation)

Si la probabilité d’incendie est élevée :

- Le système RAG recherche un incendie historique similaire  
- Retourne un contexte enrichi incluant :
  - Taille du périmètre brûlé  
  - Durée de l’incendie  
  - Conditions météorologiques associées  
- Génère des recommandations adaptées à la situation actuelle  

Cela permet d’expliquer la prédiction au lieu de simplement afficher un score.

---

## 🎓 Objectifs Éducatifs du Projet

Ce projet a une forte dimension pédagogique. Il vise à :

- 🚀 Dérouler un projet complet sous une **culture DevOps** (versioning, CI/CD, gestion des versions du modèle, séparation des environnements)  
- 🔌 Concevoir et exposer des **API pour servir des modèles de Machine Learning**  
- 🤖 Concevoir et intégrer un **système RAG** pour enrichir et contextualiser les prédictions  
- 🌍 Collecter des données depuis des **API web externes** (satellite, météo)  
- 🧹 Nettoyer, transformer et formater des données réelles avant exploitation par un modèle ML  
- 🏗️ Structurer une architecture complète combinant mobile, back-end et intelligence artificielle  

---

## 🚧 État actuel

Ce README décrit la **vision et l’architecture cible** du projet.  
Une version plus détaillée sera ajoutée une fois l’implémentation finalisée (endpoints API, structure du projet, dépendances, déploiement, métriques du modèle, etc.).
