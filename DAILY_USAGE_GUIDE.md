# 📅 Guide d'Utilisation Quotidienne - Football ELO Predictor

## 🚀 Démarrage Quotidien

### 1. Mise à Jour Matinale (7h00)
```bash
cd /home/ubuntu
python3.11 smart_scheduler.py manual
```

**Ce que ça fait :**
- Récupère les matchs du jour (5-15 appels API)
- Calcule les probabilités pour chaque match
- Sauvegarde les prédictions pour l'interface
- Met à jour les ELO avec les résultats d'hier

### 2. Consultation de l'Interface
```bash
# Démarrer l'API backend
cd /home/ubuntu
RAPIDAPI_KEY=
python3.11 api_server.py &

# Démarrer l'interface React
cd /home/ubuntu/football-elo-predictor
npm run dev -- --host
```

**Accès :** http://localhost:5178 (ou port affiché)

### 3. Mise à Jour du Soir (22h00)
```bash
cd /home/ubuntu
python3.11 -c "
from smart_scheduler import SmartScheduler
scheduler = SmartScheduler('')
scheduler.evening_update()
"
```

## 📊 Utilisation de l'Interface

### Fonctionnalités Disponibles :
- **📋 Matchs du Jour :** Tous les matchs avec écarts ELO
- **🎯 Probabilités :** 1X2, Double Chance, Over/Under 2.5, BTTS
- **💡 Meilleur Pari :** Suggestion automatique basée sur les probabilités
- **🔄 Actualisation :** Bouton pour recharger les données
- **📈 Mise à Jour Complète :** Récupération + calcul ELO

### Interprétation des Couleurs :
- 🟢 **Vert :** Écart ELO < 50 (match équilibré)
- 🟡 **Jaune :** Écart ELO 50-100 (léger favori)
- 🟠 **Orange :** Écart ELO 100-200 (favori net)
- 🔴 **Rouge :** Écart ELO > 200 (très gros favori)

## 🤖 Automatisation Complète

### Planificateur Automatique :
```bash
cd /home/ubuntu
python3.11 smart_scheduler.py
```

**Programme automatique :**
- **00:01** - Remise à zéro des compteurs
- **03:00** - Nettoyage du cache
- **07:00** - Mise à jour matinale (matchs du jour)
- **12:00** - Rafraîchissement (matchs en cours)
- **22:00** - Mise à jour du soir (résultats + ELO)

### Variables d'Environnement :
```bash
export RAPIDAPI_KEY=""
```

## 📈 Monitoring et Statistiques

### Vérifier l'Utilisation API :
```bash
python3.11 -c "
from efficient_data_manager import EfficientDataManager
manager = EfficientDataManager('e1e76b8e3emsh2445ffb97db0128p158afdjsnb3175ce8d916')
stats = manager.get_api_usage_stats()
print(f'Appels utilisés: {stats[\"daily_calls\"]}/{stats[\"max_calls\"]}')
print(f'Pourcentage: {stats[\"percentage_used\"]:.1f}%')
"
```

### Endpoints API Disponibles :
- `GET /api/health` - État du système
- `GET /api/today-matches` - Matchs du jour avec prédictions
- `GET /api/top-teams` - Classement ELO
- `POST /api/daily-update` - Mise à jour complète
- `POST /api/update-elos` - Mise à jour ELO seulement

## 🎯 Utilisation des Prédictions

### Types de Paris Supportés :

**1. Résultat (1X2) :**
- Victoire Domicile (1)
- Match Nul (X)
- Victoire Extérieur (2)

**2. Double Chance :**
- 1X (Domicile ou Nul)
- X2 (Extérieur ou Nul)
- 12 (Domicile ou Extérieur)

**3. Buts :**
- Plus de 2.5 buts
- Moins de 2.5 buts

**4. BTTS (Both Teams To Score) :**
- Oui (les deux équipes marquent)
- Non (au moins une équipe ne marque pas)

### Interprétation des Probabilités :

**Probabilité > 60% :** Pari très sûr
**Probabilité 50-60% :** Pari intéressant
**Probabilité 45-50% :** Pari risqué
**Probabilité < 45% :** Éviter

## 🔧 Maintenance et Dépannage

### Problèmes Courants :

**1. "Équipe non trouvée" :**
```bash
# Ajouter un mapping manuel
python3.11 -c "
from team_name_mapping import TeamNameMapper
mapper = TeamNameMapper()
mapper.add_manual_mapping('Nom API', 'Nom ELO')
mapper.save_mapping_cache()
"
```

**2. Cache corrompu :**
```bash
rm -rf data/cache/*
rm data/team_mapping_cache.json
```

**3. ELO incohérents :**
```bash
# Recharger depuis le dataset original
rm data/current_elos.json
python3.11 elo_predictor.py
```

### Logs et Debugging :
- Les logs sont affichés en temps réel
- Fichiers de cache dans `data/cache/`
- Prédictions sauvegardées dans `data/daily_predictions/`

## 📱 Accès Mobile

L'interface React est responsive et fonctionne sur mobile.
Pour un accès externe, utilisez :

```bash
# Exposer le port publiquement
python3.11 -c "
from service_expose_port import expose_port
expose_port(5178)
"
```

## 🎲 Conseils d'Utilisation

### Stratégies de Paris :

**1. Écarts ELO élevés (>150) :**
- Privilégier les paris "sûrs" (1X, X2)
- Éviter les cotes trop faibles

**2. Matchs équilibrés (<50) :**
- BTTS souvent intéressant
- Double chance plus sûr que 1X2

**3. Derbys et rivalités :**
- Les écarts ELO peuvent être trompeurs
- Privilégier Under 2.5 et BTTS

### Gestion Bankroll :
- Ne jamais parier plus de 2-5% de votre bankroll
- Diversifier sur plusieurs matchs
- Suivre les performances sur le long terme

## 📊 Statistiques de Performance

Le système maintient automatiquement :
- Précision des prédictions par type de pari
- Évolution des ELO des équipes
- Historique des mises à jour API
- Cache des correspondances d'équipes

**Précision moyenne attendue :**
- 1X2 : ~47-52%
- Double Chance : ~65-75%
- Over/Under 2.5 : ~55-60%
- BTTS : ~58-62%

---

## 🚀 Démarrage Rapide Quotidien

```bash
# 1. Mise à jour matinale
cd /home/ubuntu && python3.11 smart_scheduler.py manual

# 2. Démarrer l'interface
cd /home/ubuntu && RAPIDAPI_KEY= python3.11 api_server.py &
cd /home/ubuntu/football-elo-predictor && npm run dev -- --host

# 3. Accéder à l'interface
# http://localhost:5178
```

**Votre système de prédiction est prêt ! 🎯**

