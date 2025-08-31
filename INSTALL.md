# Guide d'Installation - Système de Prédiction Football ELO

Ce guide vous accompagne dans l'installation et la configuration complète du système de prédiction football ELO.

## 📋 Prérequis Système

### Logiciels Requis

- **Python 3.11 ou supérieur**
- **Node.js 20.x ou supérieur**
- **npm ou pnpm** (gestionnaire de paquets Node.js)
- **Git** (pour cloner le repository)

### Vérification des Prérequis

```bash
# Vérifier Python
python3 --version
# ou
python --version

# Vérifier Node.js
node --version

# Vérifier npm
npm --version

# Vérifier Git
git --version
```

## 🚀 Installation Étape par Étape

### 1. Cloner le Repository

```bash
git clone https://github.com/votre-username/football-elo-predictor.git
cd football-elo-predictor
```

### 2. Configuration de l'Environnement Python

#### Option A : Utilisation d'un environnement virtuel (Recommandé)

```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Sur Linux/Mac :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

#### Option B : Installation globale

```bash
pip install pandas numpy matplotlib
```

### 3. Obtention des Données

#### Téléchargement depuis Kaggle

1. Allez sur [Kaggle - Club Football Match Data](https://www.kaggle.com/datasets/adamgbor/club-football-match-data-2000-2025)
2. Téléchargez le fichier `archive.zip`
3. Extrayez les fichiers dans le dossier `data/` :

```bash
# Créer le dossier data
mkdir -p data

# Extraire les fichiers (ajustez le chemin selon votre téléchargement)
unzip ~/Downloads/archive.zip -d data/
```

#### Structure Attendue

```
data/
├── Matches.csv      # ~43 MB - Historique des matchs
└── EloRatings.csv   # ~9 MB - Classements ELO
```

### 4. Test de l'Installation Backend

```bash
# Tester le système ELO
python3 elo_predictor.py

# Lancer les tests de validation
python3 test_elo_system.py
```

Vous devriez voir des résultats similaires à :
```
Probabilities for ELO difference around 150:
elo_diff_bin: 150.0000
total_matches_in_bin: 16677.0000
prob_home_win: 0.5857
...
```

### 5. Installation de l'Interface Web

```bash
# Aller dans le dossier de l'interface
cd football-elo-predictor

# Installer les dépendances Node.js
npm install
# ou avec pnpm
pnpm install
```

### 6. Lancement de l'Application

```bash
# Démarrer le serveur de développement
npm run dev
# ou avec pnpm
pnpm run dev
```

L'application sera accessible à l'adresse : `http://localhost:5173`

## 🔧 Configuration Avancée

### Variables d'Environnement

Créez un fichier `.env` dans le dossier `football-elo-predictor/` :

```env
# Port de l'application (optionnel)
VITE_PORT=5173

# URL de l'API backend (si séparée)
VITE_API_URL=http://localhost:8000
```

### Personnalisation des Paramètres ELO

Modifiez les paramètres dans `elo_predictor.py` :

```python
# Facteur K de base (volatilité des changements ELO)
K_FACTOR = 30

# Avantage du terrain en points ELO
HOME_ADVANTAGE = 100

# Taille des bins pour le calcul des probabilités
ELO_BIN_SIZE = 50
```

### Configuration de Production

#### Backend avec Flask (Optionnel)

Si vous souhaitez créer une API REST :

```bash
# Installer Flask
pip install flask flask-cors

# Créer un serveur API simple
cat > api_server.py << 'EOF'
from flask import Flask, jsonify, request
from flask_cors import CORS
from elo_predictor import calculate_probabilities, load_data
import pandas as pd

app = Flask(__name__)
CORS(app)

# Charger les données au démarrage
matches_df, elo_df = load_data("data/Matches.csv", "data/EloRatings.csv")

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    elo_diff = data.get('elo_diff', 0)
    probabilities = calculate_probabilities(elo_diff, matches_df)
    return jsonify(probabilities)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
EOF

# Lancer l'API
python3 api_server.py
```

#### Build de Production

```bash
# Dans le dossier football-elo-predictor
npm run build

# Les fichiers de production seront dans dist/
ls dist/
```

## 🐛 Résolution des Problèmes

### Erreurs Communes

#### 1. "Module not found: pandas"

```bash
# Vérifier l'installation
pip list | grep pandas

# Réinstaller si nécessaire
pip install --upgrade pandas
```

#### 2. "Port 5173 is already in use"

```bash
# Utiliser un autre port
npm run dev -- --port 3000
```

#### 3. "Cannot read CSV files"

```bash
# Vérifier la présence des fichiers
ls -la data/
# Vérifier les permissions
chmod 644 data/*.csv
```

#### 4. Erreurs de mémoire avec de gros datasets

```python
# Dans elo_predictor.py, utiliser des chunks
matches_df = pd.read_csv("data/Matches.csv", chunksize=10000)
```

### Logs et Débogage

```bash
# Activer les logs détaillés
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -v elo_predictor.py

# Vérifier les logs Node.js
npm run dev -- --debug
```

## 📊 Validation de l'Installation

### Tests de Base

```bash
# Test 1 : Import des modules Python
python3 -c "import pandas as pd; import numpy as np; print('✅ Modules Python OK')"

# Test 2 : Lecture des données
python3 -c "
import pandas as pd
matches = pd.read_csv('data/Matches.csv', nrows=5)
print(f'✅ Données chargées : {len(matches)} matchs de test')
"

# Test 3 : Interface web
curl -s http://localhost:5173 > /dev/null && echo "✅ Interface web accessible"
```

### Tests Complets

```bash
# Lancer tous les tests
python3 -m pytest test_elo_system.py -v

# Test de performance
time python3 elo_predictor.py
```

## 🔄 Mise à Jour

### Mise à Jour du Code

```bash
# Récupérer les dernières modifications
git pull origin main

# Mettre à jour les dépendances Python
pip install -r requirements.txt --upgrade

# Mettre à jour les dépendances Node.js
cd football-elo-predictor
npm update
```

### Mise à Jour des Données

```bash
# Sauvegarder les anciennes données
cp data/Matches.csv data/Matches_backup.csv

# Télécharger les nouvelles données depuis Kaggle
# Remplacer les fichiers dans data/

# Vérifier l'intégrité
python3 -c "
import pandas as pd
df = pd.read_csv('data/Matches.csv')
print(f'Nouveau dataset : {len(df)} matchs')
"
```

## 🚀 Déploiement

### Déploiement Local

```bash
# Build de production
cd football-elo-predictor
npm run build

# Servir les fichiers statiques
npx serve dist/
```

### Déploiement Cloud

#### Vercel (Recommandé pour le frontend)

```bash
# Installer Vercel CLI
npm install -g vercel

# Déployer
cd football-elo-predictor
vercel
```

#### Heroku (Pour l'API backend)

```bash
# Créer un Procfile
echo "web: python3 api_server.py" > Procfile

# Déployer sur Heroku
heroku create football-elo-api
git push heroku main
```

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifiez les logs** d'erreur détaillés
2. **Consultez les issues** GitHub existantes
3. **Créez une nouvelle issue** avec :
   - Votre système d'exploitation
   - Versions de Python et Node.js
   - Message d'erreur complet
   - Étapes pour reproduire le problème

## ✅ Checklist d'Installation

- [ ] Python 3.11+ installé et fonctionnel
- [ ] Node.js 20+ installé et fonctionnel
- [ ] Repository cloné
- [ ] Dépendances Python installées
- [ ] Données CSV téléchargées et placées dans `data/`
- [ ] Test backend réussi
- [ ] Dépendances Node.js installées
- [ ] Interface web accessible
- [ ] Tests de validation passés

Une fois tous ces éléments cochés, votre installation est complète ! 🎉

