#!/usr/bin/env python3
"""
Football ELO Predictor - Serveur Flask Cloud
Version pour déploiement cloud avec GitHub Actions et données réelles
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import threading
import time

# Import des modules locaux
from efficient_data_manager import EfficientDataManager
from team_name_mapping import TeamNameMapper
from elo_predictor import calculate_probabilities

# Configuration
app = Flask(__name__)
CORS(app)

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales
data_manager = None
team_mapper = None
last_update = None
current_matches = []
api_stats = {"daily_calls": 0, "max_calls": 35000}

def init_app():
    """Initialisation de l'application"""
    global data_manager, team_mapper, last_update
    
    try:
        api_key = os.environ.get("RAPIDAPI_KEY")
        if not api_key:
            logger.error("❌ RAPIDAPI_KEY non configurée. Utilisation des données d'exemple.")
            init_sample_data()
            return

        data_manager = EfficientDataManager(api_key)
        team_mapper = TeamNameMapper()
        team_mapper.load_mapping_cache()
        
        # Créer les dossiers nécessaires
        os.makedirs("data/daily_predictions", exist_ok=True)
        os.makedirs("data/cache", exist_ok=True)
        
        # Charger les ELO initiaux
        data_manager.load_current_elos()
        
        last_update = datetime.now()
        logger.info("✅ Application initialisée avec succès (données réelles)")
        
        # Démarrer le planificateur en arrière-plan
        start_scheduler()
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        init_sample_data()

def init_sample_data():
    """Initialise des données d'exemple si l'API n'est pas disponible"""
    global current_matches, last_update
    
    current_matches = [
        {
            "fixture_id": "example_1",
            "home_team": "Manchester City",
            "away_team": "Arsenal",
            "home_elo": 1960,
            "away_elo": 1871,
            "elo_diff": 89,
            "league": "Premier League",
            "kickoff": "2025-08-30T15:00:00Z",
            "predictions": {
                "home_win": 45.2,
                "draw": 28.1,
                "away_win": 26.7,
                "over_2_5": 62.3,
                "under_2_5": 37.7,
                "btts_yes": 58.9,
                "btts_no": 41.1,
                "best_bet": "Over 2.5 Goals (62.3%)"
            }
        },
        {
            "fixture_id": "example_2",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "home_elo": 2063,
            "away_elo": 2107,
            "elo_diff": -44,
            "league": "La Liga",
            "kickoff": "2025-08-30T20:00:00Z",
            "predictions": {
                "home_win": 38.5,
                "draw": 29.2,
                "away_win": 32.3,
                "over_2_5": 68.7,
                "under_2_5": 31.3,
                "btts_yes": 72.1,
                "btts_no": 27.9,
                "best_bet": "BTTS Yes (72.1%)"
            }
        }
    ]
    last_update = datetime.now()
    logger.info("🔄 Données d'exemple chargées")

def start_scheduler():
    """Démarre le planificateur automatique"""
    def run_scheduler():
        # Le planificateur sera géré par GitHub Actions ou un service externe
        # Cette fonction est principalement pour le mode local ou de test
        while True:
            time.sleep(3600) # Vérifier toutes les heures
            logger.info("Planificateur interne: Vérification des mises à jour...")
            # Ici, on pourrait déclencher une mise à jour légère si nécessaire
            # Pour le déploiement cloud, les mises à jour seront externes
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("🤖 Planificateur interne démarré (mode passif pour le cloud)")

def calculate_match_predictions(match):
    """Calcule les prédictions pour un match"""
    try:
        home_elo = match["home_elo"]
        away_elo = match["away_elo"]
        elo_diff = home_elo - away_elo
        
        probs = calculate_probabilities(elo_diff)
        best_bet = determine_best_bet(probs)
        
        return {
            "home_win": round(probs["home_win"] * 100, 1),
            "draw": round(probs["draw"] * 100, 1),
            "away_win": round(probs["away_win"] * 100, 1),
            "over_2_5": round(probs["over_2_5"] * 100, 1),
            "under_2_5": round(probs["under_2_5"] * 100, 1),
            "btts_yes": round(probs["btts_yes"] * 100, 1),
            "btts_no": round(probs["btts_no"] * 100, 1),
            "best_bet": best_bet
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul prédictions: {e}")
        return {
            "home_win": 33.3,
            "draw": 33.3,
            "away_win": 33.3,
            "over_2_5": 50.0,
            "under_2_5": 50.0,
            "btts_yes": 50.0,
            "btts_no": 50.0,
            "best_bet": "Données indisponibles"
        }

def determine_best_bet(probs):
    """Détermine le meilleur pari basé sur les probabilités"""
    bets = {
        "Victoire Domicile": probs["home_win"],
        "Match Nul": probs["draw"],
        "Victoire Extérieur": probs["away_win"],
        "Over 2.5 Goals": probs["over_2_5"],
        "Under 2.5 Goals": probs["under_2_5"],
        "BTTS Yes": probs["btts_yes"],
        "BTTS No": probs["btts_no"]
    }
    
    best_bet_name = max(bets, key=bets.get)
    best_prob = bets[best_bet_name]
    
    return f"{best_bet_name} ({best_prob*100:.1f}%)"

def save_daily_predictions(matches):
    """Sauvegarde les prédictions quotidiennes"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"data/daily_predictions/predictions_{today}.json"
        
        with open(filename, "w") as f:
            json.dump({
                "date": today,
                "matches": matches,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)
            
        logger.info(f"💾 Prédictions sauvegardées: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde: {e}")

# Routes API
@app.route("/api/health")
def health_check():
    """Vérification de l'état de l'API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "last_update": last_update.isoformat() if last_update else None,
        "api_configured": data_manager is not None,
        "matches_count": len(current_matches),
        "mode": "real" if data_manager else "demo",
        "version": "1.0.0"
    })

@app.route("/api/today-matches")
def get_today_matches():
    """Récupère les matchs du jour avec prédictions"""
    global current_matches
    
    # Tenter de charger les prédictions du jour depuis le fichier
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/daily_predictions/predictions_{today}.json"
    
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                current_matches = data["matches"]
                global last_update
                last_update = datetime.fromisoformat(data["timestamp"])
                logger.info(f"📁 Prédictions chargées depuis le fichier pour {today}")
        except Exception as e:
            logger.error(f"❌ Erreur lecture fichier prédictions: {e}")
            init_sample_data() # Revenir aux données d'exemple en cas d'erreur
    else:
        logger.info(f"ℹ️ Pas de fichier de prédictions pour {today}. Utilisation des données d'exemple.")
        init_sample_data() # Utiliser les données d'exemple si pas de fichier

    return jsonify({
        "success": True,
        "date": today,
        "matches": current_matches,
        "count": len(current_matches),
        "last_update": last_update.isoformat() if last_update else None,
        "source": "real" if os.path.exists(filename) else "demo",
        "message": "Données réelles chargées depuis le fichier ou données de démonstration si non disponibles"
    })

@app.route("/api/refresh", methods=["POST"])
def refresh_data():
    """Force une mise à jour des données (déclenchée par workflow)"""
    global current_matches, last_update, api_stats
    
    try:
        if data_manager:
            logger.info("🔄 Déclenchement de la mise à jour des matchs...")
            matches = data_manager.get_today_fixtures_smart()
            
            if matches:
                for match in matches:
                    predictions = calculate_match_predictions(match)
                    match["predictions"] = predictions
                
                current_matches = matches
                last_update = datetime.now()
                save_daily_predictions(matches)
                api_stats = data_manager.get_api_usage_stats()
                logger.info(f"✅ {len(matches)} matchs mis à jour et sauvegardés.")
            else:
                logger.info("ℹ️ Aucun match trouvé pour la mise à jour.")
                init_sample_data() # Revenir aux données d'exemple
        else:
            logger.warning("⚠️ Data Manager non initialisé. Impossible de rafraîchir les données réelles.")
            init_sample_data() # Utiliser les données d'exemple

        return jsonify({
            "success": True,
            "message": "Données mises à jour",
            "matches_count": len(current_matches),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Erreur rafraîchissement: {e}")
        init_sample_data() # Revenir aux données d'exemple en cas d'erreur
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/update-elos", methods=["POST"])
def update_elos_endpoint():
    """Met à jour les ELO avec les résultats des matchs terminés (déclenchée par workflow)"""
    global data_manager
    try:
        if data_manager:
            logger.info("🔄 Mise à jour des ELO en cours...")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            finished_matches = data_manager.get_today_fixtures_smart(yesterday)
            
            if finished_matches:
                finished_matches = [m for m in finished_matches if m.get("finished", False)]
                if finished_matches:
                    logger.info(f"📊 {len(finished_matches)} résultats à traiter pour la mise à jour ELO.")
                    data_manager.update_elos_from_matches(finished_matches)
                    data_manager.save_current_elos()
                    logger.info("✅ ELO mis à jour et sauvegardés.")
                else:
                    logger.info("ℹ️ Aucun match terminé hier pour la mise à jour ELO.")
            else:
                logger.info("ℹ️ Impossible de récupérer les matchs d'hier pour la mise à jour ELO.")
            
            return jsonify({
                "success": True,
                "message": "Mise à jour des ELO déclenchée",
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.warning("⚠️ Data Manager non initialisé. Impossible de mettre à jour les ELO.")
            return jsonify({
                "success": False,
                "error": "Data Manager non initialisé"
            }), 500
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour ELO: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/stats")
def get_stats():
    """Statistiques de l'API"""
    return jsonify({
        "api_usage": api_stats,
        "last_update": last_update.isoformat() if last_update else None,
        "matches_today": len(current_matches),
        "system_status": "operational" if data_manager else "fallback"
    })

@app.route("/api/top-teams")
def get_top_teams():
    """Top des équipes par ELO"""
    try:
        if data_manager and hasattr(data_manager, "current_elos") and data_manager.current_elos:
            sorted_teams = sorted(
                data_manager.current_elos.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]
            return jsonify({
                "success": True,
                "teams": [{"name": name, "elo": elo} for name, elo in sorted_teams],
                "source": "real"
            })
        else:
            example_teams = [
                {"name": "Barcelona", "elo": 2107.5},
                {"name": "Real Madrid", "elo": 2063.2},
                {"name": "Paris SG", "elo": 1971.0},
                {"name": "Manchester City", "elo": 1959.9},
                {"name": "Bayern Munich", "elo": 1954.8},
                {"name": "Liverpool", "elo": 1932.1},
                {"name": "Arsenal", "elo": 1871.7},
                {"name": "Juventus", "elo": 1852.3},
                {"name": "Borussia Dortmund", "elo": 1823.1},
                {"name": "AC Milan", "elo": 1798.4}
            ]
            return jsonify({
                "success": True,
                "teams": example_teams,
                "source": "demo"
            })
    except Exception as e:
        logger.error(f"❌ Erreur top teams: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Point d'entrée
if __name__ == "__main__":
    init_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    
    logger.info(f"🚀 Démarrage du serveur sur le port {port}")
    logger.info("📊 Endpoints disponibles:")
    logger.info("   GET  /api/health - État du système")
    logger.info("   GET  /api/today-matches - Matchs du jour")
    logger.info("   POST /api/refresh - Actualiser les données")
    logger.info("   POST /api/update-elos - Mettre à jour les ELO")
    logger.info("   GET  /api/stats - Statistiques API")
    logger.info("   GET  /api/top-teams - Classement ELO")
    
    app.run(host="0.0.0.0", port=port, debug=debug)


