import json
import pandas as pd
from difflib import SequenceMatcher

class TeamNameMapper:
    def __init__(self):
        # Mapping manuel des noms d'équipes les plus courants
        self.manual_mapping = {
            # API -> Base ELO
            "Paris Saint Germain": "Paris SG",
            "Paris Saint-Germain": "Paris SG",
            "PSG": "Paris SG",
            "Manchester City": "Man City",
            "Manchester United": "Man United",
            "FC Barcelona": "Barcelona",
            "Real Madrid CF": "Real Madrid",
            "Bayern München": "Bayern Munich",
            "Bayern Munich": "Bayern Munich",
            "Juventus FC": "Juventus",
            "Atletico Madrid": "Ath Madrid",
            "Athletic Bilbao": "Ath Bilbao",
            "Athletic Club": "Ath Bilbao",
            "Borussia Dortmund": "Dortmund",
            "AC Milan": "AC Milan",
            "Inter Milan": "Inter",
            "AS Roma": "Roma",
            "SSC Napoli": "Napoli",
            "Chelsea FC": "Chelsea",
            "Arsenal FC": "Arsenal",
            "Liverpool FC": "Liverpool",
            "Tottenham Hotspur": "Tottenham",
            "Tottenham": "Tottenham",
            "Newcastle United": "Newcastle",
            "Aston Villa": "Aston Villa",
            "West Ham United": "West Ham",
            "Leicester City": "Leicester",
            "Brighton & Hove Albion": "Brighton",
            "Crystal Palace": "Crystal Palace",
            "Everton FC": "Everton",
            "Fulham FC": "Fulham",
            "Brentford FC": "Brentford",
            "Wolverhampton Wanderers": "Wolves",
            "Sheffield United": "Sheffield United",
            "Burnley FC": "Burnley",
            "Norwich City": "Norwich",
            "Watford FC": "Watford",
            "Leeds United": "Leeds",
            "Southampton FC": "Southampton",
            "Olympique Lyonnais": "Lyon",
            "Olympique de Marseille": "Marseille",
            "AS Monaco": "Monaco",
            "Lille OSC": "Lille",
            "OGC Nice": "Nice",
            "Stade Rennais": "Rennes",
            "RC Strasbourg": "Strasbourg",
            "Montpellier HSC": "Montpellier",
            "FC Nantes": "Nantes",
            "Girondins Bordeaux": "Bordeaux",
            "Real Sociedad": "Sociedad",
            "Sevilla FC": "Sevilla",
            "Valencia CF": "Valencia",
            "Villarreal CF": "Villarreal",
            "Real Betis": "Betis",
            "Celta Vigo": "Celta",
            "RCD Espanyol": "Espanyol",
            "Getafe CF": "Getafe",
            "CA Osasuna": "Osasuna",
            "Deportivo Alaves": "Alaves",
            "Cadiz CF": "Cadiz",
            "Elche CF": "Elche",
            "Granada CF": "Granada",
            "SD Huesca": "Huesca",
            "Levante UD": "Levante",
            "RCD Mallorca": "Mallorca",
            "Rayo Vallecano": "Vallecano",
            "Real Valladolid": "Valladolid",
            "Borussia Mönchengladbach": "Mgladbach",
            "Bayer Leverkusen": "Leverkusen",
            "RB Leipzig": "RB Leipzig",
            "Eintracht Frankfurt": "Ein Frankfurt",
            "VfL Wolfsburg": "Wolfsburg",
            "FC Union Berlin": "Union Berlin",
            "SC Freiburg": "Freiburg",
            "TSG Hoffenheim": "Hoffenheim",
            "FC Augsburg": "Augsburg",
            "Hertha Berlin": "Hertha",
            "1. FC Köln": "FC Koln",
            "VfB Stuttgart": "Stuttgart",
            "FSV Mainz 05": "Mainz",
            "FC Schalke 04": "Schalke",
            "Werder Bremen": "Werder Bremen",
            "Fortuna Düsseldorf": "Fortuna Dusseldorf",
            "SC Paderborn": "Paderborn",
            "1. FC Nürnberg": "Nurnberg",
            "Hannover 96": "Hannover",
            "Hamburger SV": "Hamburg",
            "FC St. Pauli": "St Pauli",
            "SV Darmstadt 98": "Darmstadt",
            "FC Ingolstadt": "Ingolstadt",
            "Karlsruher SC": "Karlsruhe",
            "SV Sandhausen": "Sandhausen",
            "SpVgg Greuther Fürth": "Greuther Furth",
            "FC Heidenheim": "Heidenheim",
            "SV Wehen Wiesbaden": "Wehen",
            "Ajax Amsterdam": "Ajax",
            "PSV Eindhoven": "PSV",
            "Feyenoord Rotterdam": "Feyenoord",
            "AZ Alkmaar": "AZ Alkmaar",
            "FC Utrecht": "Utrecht",
            "FC Twente": "Twente",
            "Vitesse Arnhem": "Vitesse",
            "FC Groningen": "Groningen",
            "PEC Zwolle": "Zwolle",
            "Willem II Tilburg": "Willem II",
            "Heracles Almelo": "Heracles",
            "ADO Den Haag": "Den Haag",
            "RKC Waalwijk": "Waalwijk",
            "Fortuna Sittard": "Sittard",
            "VVV Venlo": "Venlo",
            "FC Emmen": "Emmen",
            "Sparta Rotterdam": "Sparta",
            "SC Heerenveen": "Heerenveen",
            "FC Porto": "Porto",
            "SL Benfica": "Benfica",
            "Sporting CP": "Sporting",
            "SC Braga": "Braga",
            "Vitoria Guimaraes": "Guimaraes",
            "Boavista FC": "Boavista",
            "Rio Ave FC": "Rio Ave",
            "Moreirense FC": "Moreirense",
            "CD Santa Clara": "Santa Clara",
            "Pacos Ferreira": "Pacos Ferreira",
            "Belenenses SAD": "Belenenses",
            "CD Tondela": "Tondela",
            "Gil Vicente FC": "Gil Vicente",
            "FC Famalicao": "Famalicao",
            "CD Nacional": "Nacional",
            "Portimonense SC": "Portimonense",
            "Maritimo": "Maritimo",
            "CD Aves": "Aves",
            "Chaves": "Chaves",
            "Estoril": "Estoril",
            "Leixoes": "Leixoes",
            "Penafiel": "Penafiel",
            "Varzim": "Varzim",
            "Club Brugge": "Club Brugge",
            "KRC Genk": "Genk",
            "Royal Antwerp": "Antwerp",
            "Standard Liege": "Standard",
            "KAA Gent": "Gent",
            "RSC Anderlecht": "Anderlecht",
            "Sint-Truiden": "St Truiden",
            "KV Mechelen": "Mechelen",
            "Cercle Brugge": "Cercle Brugge",
            "KV Oostende": "Oostende",
            "Zulte Waregem": "Zulte",
            "Eupen": "Eupen",
            "Kortrijk": "Kortrijk",
            "Mouscron": "Mouscron",
            "Waasland-Beveren": "Beveren",
            "Charleroi": "Charleroi",
            "Seraing": "Seraing",
            "Beerschot": "Beerschot VA"
        }
        
        # Chargement des équipes de la base ELO
        self.elo_teams = set()
        self.load_elo_teams()
        
        # Cache pour éviter les calculs répétés
        self.mapping_cache = {}
    
    def load_elo_teams(self):
        """Charge la liste des équipes de la base ELO"""
        try:
            df = pd.read_csv("data/EloRatings.csv")
            self.elo_teams = set(df["club"].unique())
            print(f"✅ {len(self.elo_teams)} équipes chargées depuis la base ELO")
        except Exception as e:
            print(f"❌ Erreur lors du chargement des équipes ELO: {e}")
    
    def map_team_name(self, api_name):
        """Mappe un nom d'équipe de l'API vers le nom de la base ELO"""
        if not api_name:
            return None
        
        # Vérifier le cache
        if api_name in self.mapping_cache:
            return self.mapping_cache[api_name]
        
        # 1. Vérification directe
        if api_name in self.elo_teams:
            self.mapping_cache[api_name] = api_name
            return api_name
        
        # 2. Mapping manuel
        if api_name in self.manual_mapping:
            mapped_name = self.manual_mapping[api_name]
            self.mapping_cache[api_name] = mapped_name
            return mapped_name
        
        # 3. Recherche par similarité
        best_match = self.find_best_match(api_name)
        if best_match:
            self.mapping_cache[api_name] = best_match
            return best_match
        
        # 4. Aucune correspondance trouvée
        print(f"⚠️  Équipe non trouvée: '{api_name}' - ELO par défaut utilisé")
        self.mapping_cache[api_name] = api_name  # Garder le nom original
        return api_name
    
    def find_best_match(self, api_name, threshold=0.8):
        """Trouve la meilleure correspondance par similarité"""
        best_ratio = 0
        best_match = None
        
        # Nettoyer le nom pour la comparaison
        clean_api_name = self.clean_name(api_name)
        
        for elo_team in self.elo_teams:
            clean_elo_name = self.clean_name(elo_team)
            
            # Calculer la similarité
            ratio = SequenceMatcher(None, clean_api_name, clean_elo_name).ratio()
            
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = elo_team
        
        if best_match:
            print(f"🔍 Correspondance trouvée: '{api_name}' -> '{best_match}' ({best_ratio:.2f})")
        
        return best_match
    
    def clean_name(self, name):
        """Nettoie un nom d'équipe pour la comparaison"""
        if not name:
            return ""
        
        # Convertir en minuscules et supprimer les caractères spéciaux
        clean = name.lower()
        
        # Remplacements courants
        replacements = {
            "fc": "",
            "cf": "",
            "sc": "",
            "ac": "",
            "afc": "",
            "bfc": "",
            "rfc": "",
            "united": "utd",
            "city": "",
            "club": "",
            "football": "",
            "association": "",
            "sporting": "",
            "real": "",
            "atletico": "ath",
            "athletic": "ath",
            "borussia": "",
            "bayern": "",
            "eintracht": "ein",
            "fortuna": "",
            "hertha": "",
            "werder": "",
            "olympique": "",
            "saint": "st",
            "sankt": "st",
            "-": " ",
            "_": " ",
            ".": "",
            "'": "",
            "&": "and"
        }
        
        for old, new in replacements.items():
            clean = clean.replace(old, new)
        
        # Supprimer les espaces multiples
        clean = " ".join(clean.split())
        
        return clean.strip()
    
    def add_manual_mapping(self, api_name, elo_name):
        """Ajoute un mapping manuel"""
        self.manual_mapping[api_name] = elo_name
        self.mapping_cache[api_name] = elo_name
        print(f"✅ Mapping ajouté: '{api_name}' -> '{elo_name}'")
    
    def save_mapping_cache(self, filename="data/team_mapping_cache.json"):
        """Sauvegarde le cache de mapping"""
        try:
            with open(filename, "w") as f:
                json.dump(self.mapping_cache, f, indent=2)
            print(f"💾 Cache de mapping sauvegardé: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde cache: {e}")
    
    def load_mapping_cache(self, filename="data/team_mapping_cache.json"):
        """Charge le cache de mapping"""
        try:
            with open(filename, "r") as f:
                self.mapping_cache = json.load(f)
            print(f"📁 Cache de mapping chargé: {len(self.mapping_cache)} entrées")
        except FileNotFoundError:
            print("ℹ️  Aucun cache de mapping trouvé, création d'un nouveau")
        except Exception as e:
            print(f"❌ Erreur chargement cache: {e}")
    
    def get_mapping_stats(self):
        """Retourne les statistiques de mapping"""
        return {
            "total_elo_teams": len(self.elo_teams),
            "manual_mappings": len(self.manual_mapping),
            "cached_mappings": len(self.mapping_cache),
            "unmapped_teams": [k for k, v in self.mapping_cache.items() if k == v and k not in self.elo_teams]
        }
    
    def validate_mappings(self):
        """Valide tous les mappings manuels"""
        invalid_mappings = []
        
        for api_name, elo_name in self.manual_mapping.items():
            if elo_name not in self.elo_teams:
                invalid_mappings.append((api_name, elo_name))
        
        if invalid_mappings:
            print("⚠️  Mappings invalides trouvés:")
            for api_name, elo_name in invalid_mappings:
                print(f"   '{api_name}' -> '{elo_name}' (équipe ELO inexistante)")
        else:
            print("✅ Tous les mappings manuels sont valides")
        
        return invalid_mappings

def test_team_mapper():
    """Test du système de mapping"""
    mapper = TeamNameMapper()
    
    # Tests avec des noms courants de l'API
    test_names = [
        "Paris Saint Germain",
        "Manchester City",
        "FC Barcelona",
        "Real Madrid CF",
        "Bayern München",
        "Juventus FC",
        "Liverpool FC",
        "Arsenal FC",
        "Chelsea FC",
        "Tottenham Hotspur",
        "Atletico Madrid",
        "Borussia Dortmund",
        "AC Milan",
        "Inter Milan",
        "AS Roma",
        "SSC Napoli"
    ]
    
    print("🧪 Test du système de mapping:")
    print("-" * 50)
    
    for api_name in test_names:
        elo_name = mapper.map_team_name(api_name)
        status = "✅" if elo_name in mapper.elo_teams else "⚠️"
        print(f"{status} '{api_name}' -> '{elo_name}'")
    
    print("-" * 50)
    stats = mapper.get_mapping_stats()
    print(f"📊 Statistiques:")
    print(f"   Équipes ELO: {stats['total_elo_teams']}")
    print(f"   Mappings manuels: {stats['manual_mappings']}")
    print(f"   Cache: {stats['cached_mappings']}")
    
    # Sauvegarder le cache
    mapper.save_mapping_cache()
    
    return mapper

if __name__ == "__main__":
    mapper = test_team_mapper()

