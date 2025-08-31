# ⚽ Système de Prédiction Football ELO

Un système complet de prédiction de matchs de football utilisant un algorithme ELO perfectionné pour calculer les probabilités de différents types de paris basé sur l'historique des matchs des 20 ligues majeures européennes.

## 🎯 Fonctionnalités Principales

- **Système ELO Perfectionné** : Calcul dynamique des classements ELO avec prise en compte de l'avantage du terrain, de la différence de buts, et de la forme récente
- **Prédictions Multi-Paris** : Calcul des probabilités pour tous les types de paris (résultat, double chance, over/under 2.5, BTTS)
- **Interface Web Moderne** : Application React pour visualiser les prédictions des matchs du jour
- **Analyse Historique** : Utilisation de plus de 230,000 matchs historiques pour calibrer les probabilités
- **20 Ligues Européennes** : Couverture des principales ligues européennes avec ajustement par niveau de compétition

## 📊 Données Supportées

Le système analyse les matchs des ligues suivantes :

| Ligue | Code | Pays | Niveau |
|-------|------|------|--------|
| Premier League | E0 | Angleterre | ⭐⭐⭐⭐⭐ |
| Serie A | I1 | Italie | ⭐⭐⭐⭐⭐ |
| La Liga | SP1 | Espagne | ⭐⭐⭐⭐⭐ |
| Bundesliga | D1 | Allemagne | ⭐⭐⭐⭐ |
| Ligue 1 | F1 | France | ⭐⭐⭐⭐ |
| Liga Portugal | P1 | Portugal | ⭐⭐⭐ |
| Eredivisie | N1 | Pays-Bas | ⭐⭐⭐ |
| Jupiler Pro League | B1 | Belgique | ⭐⭐ |
| Süper Lig | T1 | Turquie | ⭐⭐ |
| Et 11 autres ligues... | | | |

## 🚀 Installation et Utilisation

### Prérequis

- Python 3.11+
- Node.js 20+
- npm ou pnpm

### Installation Backend

```bash
# Cloner le repository
git clone https://github.com/votre-username/football-elo-predictor.git
cd football-elo-predictor

# Installer les dépendances Python
pip install pandas numpy matplotlib

# Télécharger les données (voir section Données)
# Placer les fichiers CSV dans le dossier /data/
```

### Installation Frontend

```bash
# Aller dans le dossier de l'interface
cd football-elo-predictor

# Installer les dépendances
npm install

# Lancer l'application
npm run dev
```

### Utilisation du Système ELO

```python
from elo_predictor import load_data, calculate_probabilities

# Charger les données
matches_df, elo_df = load_data("data/Matches.csv", "data/EloRatings.csv")

# Calculer les probabilités pour un écart ELO de 150 points
probabilities = calculate_probabilities(150, matches_df)

print(f"Victoire domicile: {probabilities['prob_home_win']:.2%}")
print(f"Match nul: {probabilities['prob_draw']:.2%}")
print(f"Victoire extérieur: {probabilities['prob_away_win']:.2%}")
```

## 🧮 Algorithme ELO Perfectionné

### Formule de Base

Le système utilise la formule ELO classique avec des améliorations :

```
Nouveau_ELO = Ancien_ELO + K × (Résultat_Réel - Résultat_Attendu)
```

### Améliorations Intégrées

1. **Avantage du Terrain** : +100 points ELO pour l'équipe à domicile
2. **Facteur K Dynamique** : Ajustement selon l'importance de la ligue et la différence de buts
3. **Forme Récente** : Prise en compte des 5 derniers matchs
4. **Différence de Buts** : Amplification du facteur K pour les victoires larges

### Calcul des Probabilités

Les probabilités sont calculées en analysant l'historique des matchs avec des écarts ELO similaires (±25 points) :

- **Résultat du Match** : Victoire domicile, match nul, victoire extérieur
- **Double Chance** : 1X, X2, 12
- **Buts** : Plus/Moins de 2.5 buts
- **BTTS** : Les deux équipes marquent (Oui/Non)

## 📈 Performance du Système

### Résultats de Validation

- **Précision Générale** : ~47.7% sur 1000 matchs de test
- **Couverture** : 230,557 matchs analysés
- **Équipes** : 245,033 équipes dans la base de données
- **ELO Moyen** : 1505.1 points

### Précision par Type de Pari

| Type de Pari | Précision | Échantillon |
|--------------|-----------|-------------|
| Résultat 1X2 | 47.7% | 1,000 matchs |
| Over/Under 2.5 | ~52% | Estimation |
| BTTS | ~51% | Estimation |
| Double Chance | ~65% | Estimation |

## 🎨 Interface Utilisateur

L'interface web permet de :

- **Visualiser les matchs du jour** avec leurs écarts ELO
- **Consulter toutes les probabilités** pour chaque type de pari
- **Identifier le meilleur pari** selon les probabilités calculées
- **Analyser les écarts ELO** avec un code couleur intuitif

### Capture d'Écran

L'interface affiche pour chaque match :
- Les équipes et leurs classements ELO
- L'écart ELO avec code couleur
- Toutes les probabilités de paris
- La suggestion du meilleur pari

## 📁 Structure du Projet

```
football-elo-predictor/
├── data/                          # Données CSV
│   ├── Matches.csv               # Historique des matchs
│   └── EloRatings.csv           # Classements ELO initiaux
├── src/                          # Interface React
│   ├── components/
│   ├── App.jsx                  # Application principale
│   └── ...
├── elo_predictor.py             # Système ELO principal
├── test_elo_system.py          # Tests et validation
├── elo_system_design.md        # Documentation technique
└── README.md                   # Ce fichier
```

## 🔧 Configuration Avancée

### Ajustement des Paramètres

Vous pouvez modifier les paramètres dans `elo_predictor.py` :

```python
# Facteur K de base
K_FACTOR = 30

# Avantage du terrain
HOME_ADVANTAGE = 100

# Multiplicateurs par ligue
major_leagues = {
    'E0': 1.2,  # Premier League
    'I1': 1.15, # Serie A
    'SP1': 1.15, # La Liga
    # ...
}
```

### Personnalisation de l'Interface

L'interface utilise Tailwind CSS et shadcn/ui. Vous pouvez personnaliser :
- Les couleurs dans `src/App.css`
- Les composants dans `src/components/`
- La logique de calcul dans `src/App.jsx`

## 📊 Données Requises

Le système nécessite deux fichiers CSV :

1. **Matches.csv** : Historique des matchs avec colonnes :
   - `Division`, `MatchDate`, `HomeTeam`, `AwayTeam`
   - `FTHome`, `FTAway`, `FTResult`
   - `HomeElo`, `AwayElo`, `Form5Home`, `Form5Away`

2. **EloRatings.csv** : Classements ELO initiaux avec colonnes :
   - `date`, `club`, `country`, `elo`

### Source de Données Recommandée

Les données utilisées proviennent du dataset Kaggle "Club Football Match Data (2000 - 2025)" qui contient :
- Plus de 475,000 matchs
- 27 pays et 42 ligues
- Données ELO historiques
- Statistiques détaillées des matchs

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

### Domaines d'Amélioration

- Intégration d'APIs de données en temps réel
- Ajout de nouvelles ligues
- Amélioration de l'algorithme de prédiction
- Interface mobile optimisée
- Système de notifications

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- Dataset Kaggle "Club Football Match Data" par Adam Gábor
- ClubElo.com pour les données ELO historiques
- Football-Data.co.uk pour les statistiques de matchs
- La communauté open source pour les outils utilisés

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation technique dans `elo_system_design.md`
- Vérifiez les tests dans `test_elo_system.py`

---

**Développé avec ❤️ pour la communauté football et paris sportifs**

