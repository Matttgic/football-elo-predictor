#!/usr/bin/env python3
"""
Football ELO Predictor - Serveur Flask Principal
Optimisé pour déploiement cloud avec automatisation complète
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from efficient_data_manager import EfficientDataManager
from team_name_mapping import TeamNameMapper
from elo_predictor import calculate_probabilities
import threading
import time
import schedule

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
        # Récupérer la clé API depuis les variables d'environnement
        api_key = os.environ.get('RAPIDAPI_KEY', 'e1e76b8e3emsh2445ffb97db0128p158afdjsnb3175ce8d916')
        
        # Initialiser le gestionnaire de données
        data_manager = EfficientDataManager(api_key)
        team_mapper = TeamNameMapper()
        team_mapper.load_mapping_cache()
        
        # Créer les dossiers nécessaires
        os.makedirs("data/daily_predictions", exist_ok=True)
        os.makedirs("data/cache", exist_ok=True)
        
        last_update = datetime.now()
        logger.info("✅ Application initialisée avec succès")
        
        # Démarrer le planificateur en arrière-plan
        start_scheduler()
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        # Continuer avec des données d'exemple
        init_fallback_data()

def init_fallback_data():
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
        # Planifier les tâches
        schedule.every().day.at("07:00").do(morning_update)
        schedule.every().day.at("12:00").do(midday_refresh)
        schedule.every().day.at("22:00").do(evening_update)
        schedule.every().hour.do(hourly_check)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute
    
    # Démarrer dans un thread séparé
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("🤖 Planificateur automatique démarré")

def morning_update():
    """Mise à jour matinale - récupération des matchs du jour"""
    global current_matches, last_update
    
    try:
        if data_manager:
            logger.info("🌅 Mise à jour matinale en cours...")
            matches = data_manager.get_today_fixtures_smart()
            
            if matches:
                # Calculer les prédictions
                for match in matches:
                    predictions = calculate_match_predictions(match)
                    match["predictions"] = predictions
                
                current_matches = matches
                last_update = datetime.now()
                
                # Sauvegarder
                save_daily_predictions(matches)
                logger.info(f"✅ {len(matches)} matchs mis à jour")
            else:
                logger.info("ℹ️ Aucun match trouvé pour aujourd'hui")
                
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour matinale: {e}")

def midday_refresh():
    """Rafraîchissement de midi"""
    logger.info("🕐 Rafraîchissement de midi...")
    # Mise à jour légère sans appels API supplémentaires

def evening_update():
    """Mise à jour du soir - résultats et ELO"""
    try:
        if data_manager:
            logger.info("🌙 Mise à jour du soir en cours...")
            # Récupérer les résultats d'hier et mettre à jour les ELO
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            results = data_manager.get_today_fixtures_smart(yesterday)
            
            if results:
                finished_matches = [m for m in results if m.get("finished", False)]
                if finished_matches:
                    logger.info(f"📊 {len(finished_matches)} résultats à traiter")
                    # Ici on pourrait mettre à jour les ELO
                    
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour du soir: {e}")

def hourly_check():
    """Vérification horaire"""
    global api_stats
    
    if data_manager:
        api_stats = data_manager.get_api_usage_stats()
        
        # Alerte si usage élevé
        if api_stats["percentage_used"] > 90:
            logger.warning(f"⚠️ Usage API élevé: {api_stats['percentage_used']:.1f}%")

def calculate_match_predictions(match):
    """Calcule les prédictions pour un match"""
    try:
        home_elo = match["home_elo"]
        away_elo = match["away_elo"]
        elo_diff = home_elo - away_elo
        
        # Utiliser notre système de calcul de probabilités
        probs = calculate_probabilities(elo_diff)
        
        # Déterminer le meilleur pari
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
    
    # Trouver le pari avec la plus haute probabilité
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
@app.route('/api/health')
def health_check():
    """Vérification de l'état de l'API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "last_update": last_update.isoformat() if last_update else None,
        "api_configured": data_manager is not None,
        "matches_count": len(current_matches)
    })

@app.route('/api/today-matches')
def get_today_matches():
    """Récupère les matchs du jour avec prédictions"""
    global current_matches
    
    return jsonify({
        "success": True,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "matches": current_matches,
        "count": len(current_matches),
        "last_update": last_update.isoformat() if last_update else None,
        "source": "live" if data_manager else "example"
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Force une mise à jour des données"""
    try:
        morning_update()
        return jsonify({
            "success": True,
            "message": "Données mises à jour",
            "matches_count": len(current_matches),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Statistiques de l'API"""
    return jsonify({
        "api_usage": api_stats,
        "last_update": last_update.isoformat() if last_update else None,
        "matches_today": len(current_matches),
        "system_status": "operational" if data_manager else "fallback"
    })

@app.route('/api/top-teams')
def get_top_teams():
    """Top des équipes par ELO"""
    try:
        if data_manager and hasattr(data_manager, 'current_elos'):
            # Trier les équipes par ELO
            sorted_teams = sorted(
                data_manager.current_elos.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20
            
            return jsonify({
                "success": True,
                "teams": [{"name": name, "elo": elo} for name, elo in sorted_teams]
            })
        else:
            # Données d'exemple
            example_teams = [
                {"name": "Barcelona", "elo": 2107.5},
                {"name": "Real Madrid", "elo": 2063.2},
                {"name": "Manchester City", "elo": 1959.9},
                {"name": "Bayern Munich", "elo": 1954.8},
                {"name": "Liverpool", "elo": 1932.1}
            ]
            return jsonify({
                "success": True,
                "teams": example_teams
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Route pour servir les fichiers statiques React
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Sert l'application React"""
    if path != "" and os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    else:
        return send_from_directory('static', 'index.html')

# Point d'entrée
if __name__ == '__main__':
    # Initialiser l'application
    init_app()
    
    # Configuration pour le déploiement
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Démarrage du serveur sur le port {port}")
    logger.info("📊 Endpoints disponibles:")
    logger.info("   GET  /api/health - État du système")
    logger.info("   GET  /api/today-matches - Matchs du jour")
    logger.info("   POST /api/refresh - Actualiser les données")
    logger.info("   GET  /api/stats - Statistiques API")
    logger.info("   GET  /api/top-teams - Classement ELO")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

