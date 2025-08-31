import os
import json
import logging
from datetime import datetime, timedelta
import requests

# Import des modules locaux
from efficient_data_manager import EfficientDataManager
from team_name_mapping import TeamNameMapper
from elo_predictor import calculate_probabilities

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def save_daily_predictions(matches):
    """Sauvegarde les prédictions quotidiennes"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"backend/data/daily_predictions/predictions_{today}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as f:
            json.dump({
                "date": today,
                "matches": matches,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)
            
        logger.info(f"💾 Prédictions sauvegardées: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde: {e}")

def main():
    logger.info("🚀 Démarrage du script de mise à jour quotidienne...")
    
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        logger.error("❌ RAPIDAPI_KEY non configurée. Impossible de récupérer les données réelles.")
        return

    api_base_url = os.environ.get("API_BASE_URL") # URL de votre backend déployé
    if not api_base_url:
        logger.error("❌ API_BASE_URL non configurée. Impossible de notifier le backend.")
        return

    try:
        # Initialiser le gestionnaire de données
        data_manager = EfficientDataManager(api_key)
        team_mapper = TeamNameMapper()
        team_mapper.load_mapping_cache()
        data_manager.load_current_elos()

        # --- Étape 1: Mettre à jour les ELO avec les résultats d'hier ---
        logger.info("🔄 Mise à jour des ELO avec les résultats d'hier...")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        finished_matches = data_manager.get_fixtures_by_date(yesterday)
        
        if finished_matches:
            finished_matches = [m for m in finished_matches if m.get("status") == "Match Finished"]
            if finished_matches:
                logger.info(f"📊 {len(finished_matches)} résultats à traiter pour la mise à jour ELO.")
                data_manager.update_elos_from_matches(finished_matches)
                data_manager.save_current_elos()
                logger.info("✅ ELO mis à jour et sauvegardés.")
            else:
                logger.info("ℹ️ Aucun match terminé hier pour la mise à jour ELO.")
        else:
            logger.info("ℹ️ Impossible de récupérer les matchs d'hier pour la mise à jour ELO.")

        # --- Étape 2: Récupérer les matchs du jour et calculer les prédictions ---
        logger.info("🌅 Récupération des matchs du jour et calcul des prédictions...")
        today_matches = data_manager.get_fixtures_by_date(datetime.now().strftime("%Y-%m-%d"))
        
        if today_matches:
            for match in today_matches:
                # Assurez-vous que les ELO sont à jour pour les équipes du match
                home_team_elo = data_manager.current_elos.get(team_mapper.map_team_name(match["home_team"]), 1500)
                away_team_elo = data_manager.current_elos.get(team_mapper.map_team_name(match["away_team"]), 1500)
                match["home_elo"] = home_team_elo
                match["away_elo"] = away_team_elo
                match["elo_diff"] = home_team_elo - away_team_elo

                predictions = calculate_match_predictions(match)
                match["predictions"] = predictions
            
            save_daily_predictions(today_matches)
            logger.info(f"✅ {len(today_matches)} matchs du jour traités et prédictions sauvegardées.")
        else:
            logger.info("ℹ️ Aucun match trouvé pour aujourd'hui.")

        # --- Étape 3: Notifier le backend déployé pour qu'il recharge les données ---
        logger.info("🔔 Notification du backend déployé...")
        try:
            response = requests.post(f"{api_base_url}/api/refresh", json={})
            response.raise_for_status() # Lève une exception pour les codes d'état HTTP d'erreur
            logger.info(f"✅ Backend notifié avec succès: {response.json()}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur lors de la notification du backend: {e}")

    except Exception as e:
        logger.error(f"❌ Erreur générale dans le script quotidien: {e}")

if __name__ == "__main__":
    main()


