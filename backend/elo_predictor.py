import pandas as pd
import numpy as np

def load_data(matches_path, elo_path):
    matches_df = pd.read_csv(matches_path, low_memory=False)
    elo_df = pd.read_csv(elo_path)
    return matches_df, elo_df

def get_k_factor(league_division, goal_difference, form_home, form_away):
    # Base K-factor
    K_factor = 30

    # Adjust K-factor based on goal difference
    if goal_difference >= 3:
        K_factor *= 1.5
    elif goal_difference == 2:
        K_factor *= 1.2

    # Adjust K-factor based on league importance (example values, can be refined)
    major_leagues = {
        'E0': 1.2, # Premier League
        'I1': 1.15, # Serie A
        'SP1': 1.15, # La Liga
        'D1': 1.1, # Bundesliga
        'F1': 1.05, # Ligue 1
        'P1': 1.0, # Liga Portugal
        'N1': 0.95, # Eredivisie
        'B1': 0.9, # Jupiler Pro League
        'T1': 0.85, # Süper Lig
        'SC0': 0.8, # Premiership écossaise
        'G1': 0.75, # Super League grecque
        'RUS': 0.7, # Premier Liga (Russia)
        'AUT': 0.65, # Bundesliga (Austria)
        'SUI': 0.6, # Super League (Switzerland)
        'DEN': 0.55, # Superliga (Denmark)
        'NOR': 0.5, # Eliteserien (Norway)
        'SWE': 0.45, # Allsvenskan (Sweden)
        # Add more leagues as needed
    }
    K_factor *= major_leagues.get(league_division, 1.0) # Default to 1.0 if not a major league

    # Adjust K-factor based on recent form (example: if both teams are in good/bad form, less/more volatile)
    # This is a simplified example, more complex logic can be applied
    if form_home >= 7 and form_away >= 7: # Both in good form
        K_factor *= 0.9
    elif form_home <= 3 and form_away <= 3: # Both in bad form
        K_factor *= 1.1

    return K_factor

def calculate_elo_change(elo_home, elo_away, score_home, score_away, K_factor, home_advantage=100):
    elo_home_adjusted = elo_home + home_advantage
    expected_home = 1 / (1 + 10**((elo_away - elo_home_adjusted) / 400))
    expected_away = 1 / (1 + 10**((elo_home_adjusted - elo_away) / 400))

    if score_home > score_away:
        S_home, S_away = 1, 0
    elif score_home < score_away:
        S_home, S_away = 0, 1
    else:
        S_home, S_away = 0.5, 0.5

    change_home = K_factor * (S_home - expected_home)
    change_away = K_factor * (S_away - expected_away)
    return change_home, change_away

def calculate_probabilities(elo_diff, historical_matches_df):
    elo_bin = round(elo_diff / 50) * 50
    
    matches_in_bin = historical_matches_df[
        (historical_matches_df["elo_diff"] >= elo_bin - 25) & 
        (historical_matches_df["elo_diff"] < elo_bin + 25)
    ].copy() # Use .copy() to avoid SettingWithCopyWarning
    
    if len(matches_in_bin) == 0:
        return None

    total_matches = len(matches_in_bin)
    prob_home_win = len(matches_in_bin[matches_in_bin["FTResult"] == "H"]) / total_matches
    prob_draw = len(matches_in_bin[matches_in_bin["FTResult"] == "D"]) / total_matches
    prob_away_win = len(matches_in_bin[matches_in_bin["FTResult"] == "A"]) / total_matches
    
    prob_home_or_draw = prob_home_win + prob_draw
    prob_away_or_draw = prob_away_win + prob_draw
    prob_home_or_away = prob_home_win + prob_away_win

    matches_in_bin["total_goals"] = matches_in_bin["FTHome"] + matches_in_bin["FTAway"]
    prob_over_2_5 = len(matches_in_bin[matches_in_bin["total_goals"] > 2.5]) / total_matches
    prob_under_2_5 = 1 - prob_over_2_5

    prob_btts_yes = len(matches_in_bin[(matches_in_bin["FTHome"] > 0) & (matches_in_bin["FTAway"] > 0)]) / total_matches
    prob_btts_no = 1 - prob_btts_yes

    return {
        "elo_diff_bin": elo_bin,
        "total_matches_in_bin": total_matches,
        "prob_home_win": prob_home_win,
        "prob_draw": prob_draw,
        "prob_away_win": prob_away_win,
        "prob_home_or_draw": prob_home_or_draw,
        "prob_away_or_draw": prob_away_or_draw,
        "prob_home_or_away": prob_home_or_away,
        "prob_over_2.5": prob_over_2_5,
        "prob_under_2.5": prob_under_2_5,
        "prob_btts_yes": prob_btts_yes,
        "prob_btts_no": prob_btts_no,
    }

if __name__ == "__main__":
    matches_path = "/home/ubuntu/data/Matches.csv"
    elo_path = "/home/ubuntu/data/EloRatings.csv"
    matches_df, elo_df = load_data(matches_path, elo_path)

    current_elos = {}
    all_teams = pd.concat([matches_df["HomeTeam"], matches_df["AwayTeam"]]).unique()
    for team in all_teams:
        current_elos[team] = elo_df[elo_df["club"] == team]["elo"].iloc[0] if team in elo_df["club"].values else 1500

    HOME_ADVANTAGE = 100

    matches_df_filtered = matches_df[matches_df["HomeTeam"].isin(current_elos.keys()) & 
                                     matches_df["AwayTeam"].isin(current_elos.keys())].copy()

    matches_df_filtered["MatchDate"] = pd.to_datetime(matches_df_filtered["MatchDate"])
    matches_df_filtered = matches_df_filtered.sort_values(by="MatchDate")

    updated_elos_history = []

    # Calculate form for each team before processing matches
    team_form = {}
    for team in all_teams:
        team_form[team] = {"last_3": 0, "last_5": 0}

    for index, row in matches_df_filtered.iterrows():
        home_team = row["HomeTeam"]
        away_team = row["AwayTeam"]
        ft_home_goals = row["FTHome"]
        ft_away_goals = row["FTAway"]
        division = row["Division"]

        elo_home = current_elos.get(home_team, 1500)
        elo_away = current_elos.get(away_team, 1500)

        # Get form for current match
        form_home = row["Form5Home"] if pd.notna(row["Form5Home"]) else 0
        form_away = row["Form5Away"] if pd.notna(row["Form5Away"]) else 0

        K_FACTOR_DYNAMIC = get_k_factor(division, abs(ft_home_goals - ft_away_goals), form_home, form_away)

        change_home, change_away = calculate_elo_change(
            elo_home, elo_away, ft_home_goals, ft_away_goals, K_FACTOR_DYNAMIC, HOME_ADVANTAGE
        )

        current_elos[home_team] = elo_home + change_home
        current_elos[away_team] = elo_away + change_away

        updated_elos_history.append({
            "date": row["MatchDate"],
            "home_team": home_team,
            "away_team": away_team,
            "home_elo_before": elo_home,
            "away_elo_before": elo_away,
            "home_elo_after": current_elos[home_team],
            "away_elo_after": current_elos[away_team],
            "FTHome": ft_home_goals, 
            "FTAway": ft_away_goals, 
            "FTResult": row["FTResult"] 
        })

    updated_elos_df = pd.DataFrame(updated_elos_history)
    updated_elos_df["elo_diff"] = updated_elos_df["home_elo_before"] - updated_elos_df["away_elo_before"]

    elo_difference_to_predict = 150
    probabilities = calculate_probabilities(elo_difference_to_predict, updated_elos_df)

    if probabilities:
        print(f"\nProbabilities for ELO difference around {elo_difference_to_predict}:")
        for key, value in probabilities.items():
            print(f"{key}: {value:.4f}")

    print("\nFinal ELOs for a few teams:")
    print(f'Real Madrid ELO: {current_elos.get("Real Madrid", "N/A")}')
    print(f'Barcelona ELO: {current_elos.get("Barcelona", "N/A")}')
    print(f'Bayern Munich ELO: {current_elos.get("Bayern Munich", "N/A")}')
    print(f'Manchester United ELO: {current_elos.get("Manchester United", "N/A")}')


