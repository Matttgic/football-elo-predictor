import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os
from elo_predictor import calculate_elo_change, calculate_probabilities, get_k_factor
from team_name_mapping import TeamNameMapper

class EfficientDataManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        self.current_elos = {}
        self.daily_api_calls = 0
        self.max_daily_calls = 35000  # Limite sécurisée sous les 40,000
        self.cache_duration = 1800  # 30 minutes de cache pour les données fréquentes
        
        # Initialiser le mapper de noms d'équipes
        self.team_mapper = TeamNameMapper()
        self.team_mapper.load_mapping_cache()
        
        self.load_current_elos()
        print(f"🔑 API configurée - Limite quotidienne: {self.max_daily_calls} appels")
        
    def load_current_elos(self):
        """Charge les ELO actuels depuis le fichier"""
        try:
            if os.path.exists("data/current_elos.json"):
                with open("data/current_elos.json", "r") as f:
                    data = json.load(f)
                    self.current_elos = data.get("elos", {})
                    self.daily_api_calls = data.get("daily_calls", 0)
                print(f"✅ ELO chargés: {len(self.current_elos)} équipes, {self.daily_api_calls} appels utilisés")
            else:
                # Charger depuis le dataset initial
                elo_df = pd.read_csv("data/EloRatings.csv")
                self.current_elos = dict(zip(elo_df["club"], elo_df["elo"]))
                self.save_current_elos()
                print(f"✅ ELO initialisés: {len(self.current_elos)} équipes")
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            self.current_elos = {}
    
    def save_current_elos(self):
        """Sauvegarde les ELO et le compteur d'appels"""
        os.makedirs("data", exist_ok=True)
        data = {
            "elos": self.current_elos,
            "daily_calls": self.daily_api_calls,
            "last_update": datetime.now().isoformat()
        }
        with open("data/current_elos.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def can_make_api_call(self):
        """Vérifie si on peut faire un appel API"""
        return self.daily_api_calls < self.max_daily_calls
    
    def make_api_call(self, endpoint, params=None):
        """Effectue un appel API avec compteur et cache"""
        if not self.can_make_api_call():
            print(f"⚠️  Limite d'appels atteinte ({self.max_daily_calls})")
            return None
        
        # Vérifier le cache d'abord
        cache_key = f"{endpoint}_{str(params)}"
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            print(f"📁 Données depuis le cache: {endpoint}")
            return cached_data
        
        url = f"{self.base_url}/{endpoint}"
        try:
            print(f"🔄 Appel API: {endpoint} (appel #{self.daily_api_calls + 1})")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            self.daily_api_calls += 1
            self.save_current_elos()  # Sauvegarder le compteur
            
            data = response.json()
            if data.get("errors"):
                print(f"❌ Erreur API: {data['errors']}")
                return None
            
            # Mettre en cache
            self.cache_data(cache_key, data)
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de requête: {e}")
            return None
    
    def get_cached_data(self, cache_key):
        """Récupère les données du cache si valides"""
        cache_file = f"data/cache/{cache_key}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cached = json.load(f)
                
                cache_time = datetime.fromisoformat(cached["timestamp"])
                if (datetime.now() - cache_time).seconds < self.cache_duration:
                    return cached["data"]
            except:
                pass
        return None
    
    def cache_data(self, cache_key, data):
        """Met les données en cache"""
        os.makedirs("data/cache", exist_ok=True)
        cache_file = f"data/cache/{cache_key}.json"
        
        cached = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        with open(cache_file, "w") as f:
            json.dump(cached, f)
    
    def get_today_fixtures_smart(self, date=None):
        """Récupère les matchs du jour de manière intelligente"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Récupération intelligente des matchs du {date}")
        
        # Vérifier d'abord le cache complet
        cache_file = f"data/daily_predictions/fixtures_{date}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cached_fixtures = json.load(f)
                
                cache_time = datetime.fromisoformat(cached_fixtures["timestamp"])
                if (datetime.now() - cache_time).seconds < 7200:  # 2 heures de cache
                    print(f"📁 Matchs chargés depuis le cache ({len(cached_fixtures['fixtures'])} matchs)")
                    return cached_fixtures["fixtures"]
            except:
                pass
        
        # Récupérer seulement les ligues prioritaires
        priority_leagues = [39, 140, 135, 78, 61]  # Top 5 ligues européennes
        all_fixtures = []
        
        for league_id in priority_leagues:
            if not self.can_make_api_call():
                print(f"⚠️  Arrêt - limite d'appels atteinte")
                break
            
            params = {
                "league": league_id,
                "date": date,
                "season": "2024"
            }
            
            data = self.make_api_call("fixtures", params)
            if data and data.get("response"):
                fixtures = data["response"]
                for fixture in fixtures:
                    match_info = self.parse_fixture(fixture)
                    if match_info:
                        all_fixtures.append(match_info)
                
                print(f"✅ {len(fixtures)} matchs - {data['response'][0]['league']['name'] if fixtures else 'Ligue inconnue'}")
                time.sleep(0.2)  # Délai entre les appels
        
        # Sauvegarder en cache
        os.makedirs("data/daily_predictions", exist_ok=True)
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "fixtures": all_fixtures
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"📊 Total: {len(all_fixtures)} matchs récupérés ({self.daily_api_calls} appels utilisés)")
        return all_fixtures
    
    def parse_fixture(self, fixture):
        """Parse un match depuis l'API"""
        try:
            api_home_team = fixture["teams"]["home"]["name"]
            api_away_team = fixture["teams"]["away"]["name"]
            
            # Mapper les noms d'équipes vers notre base ELO
            home_team = self.team_mapper.map_team_name(api_home_team)
            away_team = self.team_mapper.map_team_name(api_away_team)
            
            # Obtenir les ELO actuels
            home_elo = self.current_elos.get(home_team, 1500)
            away_elo = self.current_elos.get(away_team, 1500)
            
            # Log si ELO par défaut utilisé
            if home_elo == 1500 and home_team not in self.current_elos:
                print(f"⚠️  ELO par défaut pour: {home_team} (API: {api_home_team})")
            if away_elo == 1500 and away_team not in self.current_elos:
                print(f"⚠️  ELO par défaut pour: {away_team} (API: {api_away_team})")
            
            match_info = {
                "fixture_id": fixture["fixture"]["id"],
                "date": fixture["fixture"]["date"],
                "status": fixture["fixture"]["status"]["short"],
                "league": fixture["league"]["name"],
                "league_id": fixture["league"]["id"],
                "home_team": home_team,  # Nom mappé
                "away_team": away_team,  # Nom mappé
                "api_home_team": api_home_team,  # Nom original de l'API
                "api_away_team": api_away_team,  # Nom original de l'API
                "home_elo": home_elo,
                "away_elo": away_elo,
                "elo_diff": home_elo - away_elo,
                "kickoff": fixture["fixture"]["date"]
            }
            
            # Ajouter les scores si le match est terminé
            if fixture["fixture"]["status"]["short"] == "FT":
                match_info.update({
                    "home_goals": fixture["goals"]["home"],
                    "away_goals": fixture["goals"]["away"],
                    "finished": True
                })
            else:
                match_info["finished"] = False
            
            return match_info
            
        except KeyError as e:
            print(f"❌ Erreur parsing: {e}")
            return None
    
    def get_match_predictions(self, matches):
        """Calcule les prédictions sans appels API supplémentaires"""
        predictions = []
        
        for match in matches:
            if not match["finished"]:
                # Calculer les probabilités basées sur l'ELO
                probabilities = self.calculate_match_probabilities(match["elo_diff"])
                
                prediction = {
                    **match,
                    "probabilities": probabilities,
                    "best_bet": self.get_best_bet(probabilities) if probabilities else None
                }
                predictions.append(prediction)
        
        return predictions
    
    def calculate_match_probabilities(self, elo_diff):
        """Calcule les probabilités basées sur l'écart ELO"""
        home_advantage = 100
        effective_diff = elo_diff + home_advantage
        
        # Probabilités basées sur l'historique (même logique que l'interface)
        if effective_diff >= 200:
            prob_home_win, prob_draw, prob_away_win = 0.65, 0.22, 0.13
            prob_over_25, prob_btts_yes = 0.58, 0.48
        elif effective_diff >= 100:
            prob_home_win, prob_draw, prob_away_win = 0.58, 0.24, 0.18
            prob_over_25, prob_btts_yes = 0.54, 0.51
        elif effective_diff >= 50:
            prob_home_win, prob_draw, prob_away_win = 0.52, 0.26, 0.22
            prob_over_25, prob_btts_yes = 0.52, 0.52
        elif effective_diff >= 0:
            prob_home_win, prob_draw, prob_away_win = 0.48, 0.27, 0.25
            prob_over_25, prob_btts_yes = 0.51, 0.53
        elif effective_diff >= -50:
            prob_home_win, prob_draw, prob_away_win = 0.44, 0.28, 0.28
            prob_over_25, prob_btts_yes = 0.50, 0.54
        elif effective_diff >= -100:
            prob_home_win, prob_draw, prob_away_win = 0.38, 0.27, 0.35
            prob_over_25, prob_btts_yes = 0.49, 0.52
        else:
            prob_home_win, prob_draw, prob_away_win = 0.32, 0.25, 0.43
            prob_over_25, prob_btts_yes = 0.47, 0.49
        
        return {
            "home_win": prob_home_win,
            "draw": prob_draw,
            "away_win": prob_away_win,
            "home_or_draw": prob_home_win + prob_draw,
            "away_or_draw": prob_away_win + prob_draw,
            "home_or_away": prob_home_win + prob_away_win,
            "over_2_5": prob_over_25,
            "under_2_5": 1 - prob_over_25,
            "btts_yes": prob_btts_yes,
            "btts_no": 1 - prob_btts_yes
        }
    
    def get_best_bet(self, probabilities):
        """Détermine le meilleur pari"""
        bets = [
            {"name": "Victoire Dom.", "prob": probabilities["home_win"], "type": "1"},
            {"name": "Match Nul", "prob": probabilities["draw"], "type": "X"},
            {"name": "Victoire Ext.", "prob": probabilities["away_win"], "type": "2"},
            {"name": "Plus 2.5", "prob": probabilities["over_2_5"], "type": "O2.5"},
            {"name": "Moins 2.5", "prob": probabilities["under_2_5"], "type": "U2.5"},
            {"name": "BTTS Oui", "prob": probabilities["btts_yes"], "type": "BTTS"}
        ]
        
        return max(bets, key=lambda x: x["prob"])
    
    def update_elos_with_results(self, finished_matches):
        """Met à jour les ELO avec les résultats"""
        updated_count = 0
        
        for match in finished_matches:
            if match["finished"]:
                home_team = match["home_team"]
                away_team = match["away_team"]
                home_goals = match["home_goals"]
                away_goals = match["away_goals"]
                
                home_elo = self.current_elos.get(home_team, 1500)
                away_elo = self.current_elos.get(away_team, 1500)
                
                # Calculer les changements ELO
                k_factor = get_k_factor("E0", abs(home_goals - away_goals), 5, 5)
                change_home, change_away = calculate_elo_change(
                    home_elo, away_elo, home_goals, away_goals, k_factor, 100
                )
                
                # Mettre à jour
                self.current_elos[home_team] = home_elo + change_home
                self.current_elos[away_team] = away_elo + change_away
                
                updated_count += 1
                print(f"✅ ELO mis à jour: {home_team} ({home_elo:.1f} → {self.current_elos[home_team]:.1f})")
        
        if updated_count > 0:
            self.save_current_elos()
            print(f"💾 {updated_count} ELO mis à jour")
        
        return updated_count
    
    def get_api_usage_stats(self):
        """Retourne les statistiques d'utilisation de l'API"""
        return {
            "daily_calls": self.daily_api_calls,
            "max_calls": self.max_daily_calls,
            "remaining": self.max_daily_calls - self.daily_api_calls,
            "percentage_used": (self.daily_api_calls / self.max_daily_calls) * 100
        }

def efficient_daily_update(api_key):
    """Mise à jour quotidienne économe en appels API"""
    print("🚀 Mise à jour quotidienne économe")
    
    manager = EfficientDataManager(api_key)
    
    # Afficher les stats d'utilisation
    stats = manager.get_api_usage_stats()
    print(f"📊 Utilisation API: {stats['daily_calls']}/{stats['max_calls']} ({stats['percentage_used']:.1f}%)")
    
    if stats['remaining'] < 10:
        print("⚠️  Pas assez d'appels restants pour la mise à jour")
        return []
    
    # 1. Récupérer les matchs d'aujourd'hui (cache intelligent)
    print("\n⚽ Récupération des matchs d'aujourd'hui...")
    today_matches = manager.get_today_fixtures_smart()
    
    # 2. Calculer les prédictions (sans appels API)
    print("\n🎯 Calcul des prédictions...")
    predictions = manager.get_match_predictions(today_matches)
    
    # 3. Sauvegarder
    date = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("data/daily_predictions", exist_ok=True)
    with open(f"data/daily_predictions/predictions_{date}.json", "w") as f:
        json.dump(predictions, f, indent=2, default=str)
    
    # Stats finales
    final_stats = manager.get_api_usage_stats()
    print(f"\n✅ Mise à jour terminée:")
    print(f"   📊 {len(predictions)} matchs analysés")
    print(f"   🔄 {final_stats['daily_calls']} appels API utilisés")
    print(f"   💾 Données sauvegardées pour l'interface")
    
    return predictions

if __name__ == "__main__":
    API_KEY = "e1e76b8e3emsh2445ffb97db0128p158afdjsnb3175ce8d916"
    
    print("🔧 Mode économe activé - Maximum 200 appels par jour")
    predictions = efficient_daily_update(API_KEY)
    
    if predictions:
        print(f"\n📋 Aperçu des prédictions:")
        for pred in predictions[:3]:
            print(f"   {pred['home_team']} vs {pred['away_team']}")
            print(f"   Écart ELO: {pred['elo_diff']:+.0f}")
            if pred.get('best_bet'):
                best = pred['best_bet']
                print(f"   Meilleur pari: {best['name']} ({best['prob']:.1%})")
            print()

