# Guide de l'outil AI Analyst — SP5-CRW

## Présentation générale

L'outil **AI Analyst** est une interface d'analyse boursière intelligente intégrée à l'application SP5-CRW. Il permet d'interroger en langage naturel les données historiques des entreprises du S&P 500, sans avoir besoin de connaître le SQL ou la finance.

L'outil est accessible depuis le menu principal en cliquant sur **AI Analyst**, à l'adresse `http://localhost:5173/ai/analyst`.

Il est propulsé par le modèle **llama-3.3-70b-versatile** via l'API **Groq**, un LLM (Large Language Model) gratuit et performant.

---

## Interface

L'interface se compose de trois parties :

**1. Sélection des entreprises**
Une liste déroulante permet de sélectionner une ou plusieurs entreprises du S&P 500. Pour sélectionner plusieurs entreprises simultanément, maintenir la touche **Ctrl** enfoncée tout en cliquant. Les entreprises disponibles correspondent aux symboles boursiers présents dans la base de données (ex: TSLA, NVDA, GOOGL...).

**2. Choix du mode**
Deux modes sont disponibles : **Chat financier** et **Requête SQL naturelle**. Ils sont décrits en détail ci-dessous.

**3. Zone de chat**
Un espace de conversation où l'utilisateur tape ses questions et reçoit les réponses de l'IA. Les résultats de requêtes SQL sont accompagnés d'un graphique généré automatiquement lorsque les données le permettent.

---

## Les deux modes

### Mode Chat financier

Le **Chat financier** est un assistant conversationnel expert en analyse boursière. Il reçoit les données des entreprises sélectionnées (les 20 dernières entrées par entreprise) et répond à des questions en langage naturel.

**Ce qu'il est capable de faire :**
- Analyser la tendance générale d'une action (haussière, baissière, stable)
- Calculer des indicateurs : prix moyen, volatilité, variation en pourcentage
- Comparer plusieurs entreprises entre elles sur leurs performances, volumes et volatilité
- Détecter des anomalies : journées inhabituelles, pics de volume anormaux, variations de prix extrêmes
- Donner une conclusion sur la meilleure performance parmi les entreprises sélectionnées
- Expliquer ce que les données signifient de manière pédagogique

**Limitation :** Ce mode utilise uniquement les données des entreprises sélectionnées dans la liste. Si aucune entreprise n'est sélectionnée, l'IA répond de manière générale sans données concrètes.

---

### Mode Requête SQL naturelle

Le **Mode SQL naturelle** traduit automatiquement une question en langage naturel en requête SQL, l'exécute sur la base de données, puis résume les résultats en français. Lorsque les résultats contiennent des données numériques en série, un graphique est généré automatiquement.

**Ce qu'il est capable de faire :**
- Récupérer les derniers prix de clôture, d'ouverture, les volumes d'une entreprise
- Calculer des moyennes, des maxima, des minima sur une période
- Comparer des données entre plusieurs entreprises via des requêtes UNION
- Trier et filtrer les données selon des critères précis
- Générer un graphique automatique à partir des résultats

**Limitation :** Ce mode ne nécessite pas de sélectionner une entreprise dans la liste — il suffit de mentionner le symbole boursier dans la question. Cependant, les symboles utilisés doivent exister dans la base de données. Les symboles non disponibles (ex: AAPL, BRK.B) ne peuvent pas être interrogés.

---

## Scénarios de test

Les scénarios suivants permettent de tester les différentes capacités de l'outil. Pour chaque scénario, le mode à utiliser, les entreprises à sélectionner et le prompt exact sont indiqués.

---

### Scénario 1 — Analyse de tendance simple

**Objectif :** Comprendre si une action est en hausse ou en baisse.

**Mode :** Chat financier
**Entreprises à sélectionner :** TSLA (faire défiler la liste jusqu'à TSLA)
**Prompt à envoyer :**
```
Est-ce que l'action est en tendance haussière ou baissière ces derniers jours ? Donne moi des chiffres précis.
```

**Résultat attendu :** L'IA analyse les prix d'ouverture et de clôture sur les 20 dernières entrées et donne une conclusion claire sur la tendance avec des valeurs concrètes.

---

### Scénario 2 — Comparaison de plusieurs entreprises

**Objectif :** Comparer les performances de trois entreprises du secteur technologique.

**Mode :** Chat financier
**Entreprises à sélectionner :** NVDA, MSFT, GOOGL (Ctrl+clic pour sélectionner les trois)
**Prompt à envoyer :**
```
Compare ces trois entreprises. Laquelle a la meilleure performance ? Laquelle est la plus volatile ?
```

**Résultat attendu :** L'IA présente un tableau comparatif avec le prix de clôture moyen, la volatilité et le volume de chaque entreprise, puis donne une conclusion argumentée.

---

### Scénario 3 — Détection d'anomalies

**Objectif :** Identifier des journées ou des événements inhabituels dans les données.

**Mode :** Chat financier
**Entreprises à sélectionner :** EW, EXC (Ctrl+clic pour sélectionner les deux)
**Prompt à envoyer :**
```
Détecte les anomalies et les journées inhabituelles pour ces entreprises. Y a-t-il des pics de volume ou des variations de prix extrêmes ?
```

**Résultat attendu :** L'IA identifie des dates spécifiques avec des comportements anormaux, explique pourquoi c'est inhabituel par rapport aux autres journées et donne des chiffres précis.

---

### Scénario 4 — Requête SQL : derniers prix d'une entreprise

**Objectif :** Récupérer les derniers prix de clôture d'une entreprise et visualiser l'évolution.

**Mode :** Requête SQL naturelle
**Entreprises à sélectionner :** Aucune (le symbole est mentionné dans le prompt)
**Prompt à envoyer :**
```
Donne moi les 20 derniers prix de clôture de NVDA triés par date
```

**Résultat attendu :** L'IA génère une requête SQL, l'exécute, résume les données en français et affiche un graphique de l'évolution du prix de clôture.

---

### Scénario 5 — Requête SQL : meilleurs volumes

**Objectif :** Trouver les journées avec le plus grand volume d'échanges.

**Mode :** Requête SQL naturelle
**Entreprises à sélectionner :** Aucune
**Prompt à envoyer :**
```
Quels sont les 10 jours avec le plus grand volume d'échanges pour TSLA ?
```

**Résultat attendu :** L'IA retourne les 10 journées avec les volumes les plus élevés pour Tesla, avec un résumé et un graphique des volumes.

---

### Scénario 6 — Requête SQL : comparaison de prix moyens

**Objectif :** Comparer le prix de clôture moyen de plusieurs entreprises via SQL.

**Mode :** Requête SQL naturelle
**Entreprises à sélectionner :** Aucune
**Prompt à envoyer :**
```
Compare le prix de clôture moyen entre GOOGL, META et MSFT
```

**Résultat attendu :** L'IA génère une requête SQL avec des UNION ou des sous-requêtes pour comparer les moyennes des trois entreprises et résume les résultats.

---

### Scénario 7 — Analyse approfondie avec données financières

**Objectif :** Obtenir une analyse complète d'une entreprise avec recommandation.

**Mode :** Chat financier
**Entreprises à sélectionner :** NVDA
**Prompt à envoyer :**
```
Fais une analyse complète de cette entreprise : tendance, volatilité, volume, anomalies détectées et ce que tu recommandes comme conclusion pour un investisseur.
```

**Résultat attendu :** L'IA produit un rapport structuré avec plusieurs sections couvrant tous les aspects de l'analyse boursière.

---

## Notes techniques

- Les données disponibles couvrent les entreprises dont les fichiers CSV ont été importés lors de l'installation. Certains symboles comme AAPL, BRK.B ou FOXA peuvent ne pas être disponibles.
- Le mode SQL naturelle est limité à 100 résultats par requête pour des raisons de performance.
- Les graphiques sont générés automatiquement uniquement en mode SQL naturelle lorsque les données retournées contiennent des valeurs numériques en série.
- Pour de meilleures comparaisons, il est recommandé de ne pas sélectionner plus de 5 entreprises simultanément en mode Chat financier.