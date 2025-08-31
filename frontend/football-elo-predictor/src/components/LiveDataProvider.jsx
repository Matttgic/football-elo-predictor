import { useState, useEffect, createContext, useContext } from 'react'

const LiveDataContext = createContext()

export const useLiveData = () => {
  const context = useContext(LiveDataContext)
  if (!context) {
    throw new Error('useLiveData must be used within a LiveDataProvider')
  }
  return context
}

export const LiveDataProvider = ({ children }) => {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)

  // Configuration de l'API backend
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'

  const fetchTodayMatches = async (date = null) => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL(`${API_BASE_URL}/api/today-matches`)
      if (date) {
        url.searchParams.append('date', date)
      }

      const response = await fetch(url)
      const data = await response.json()

      if (data.success) {
        setMatches(data.matches)
        setLastUpdate(new Date())
        console.log(`✅ ${data.matches.length} matchs chargés depuis ${data.source}`)
      } else {
        throw new Error(data.error || 'Erreur lors du chargement des matchs')
      }
    } catch (err) {
      console.error('Erreur API:', err)
      setError(err.message)
      
      // Fallback vers des données d'exemple
      setMatches(generateFallbackMatches())
      setLastUpdate(new Date())
    } finally {
      setLoading(false)
    }
  }

  const updateElos = async (date = null) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/update-elos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ date })
      })

      const data = await response.json()
      
      if (data.success) {
        console.log(`✅ ${data.elos_updated} ELO mis à jour`)
        // Recharger les matchs pour avoir les nouveaux ELO
        await fetchTodayMatches()
        return data
      } else {
        throw new Error(data.error)
      }
    } catch (err) {
      console.error('Erreur mise à jour ELO:', err)
      setError(err.message)
      return null
    }
  }

  const runDailyUpdate = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/daily-update`, {
        method: 'POST'
      })

      const data = await response.json()
      
      if (data.success) {
        console.log(`✅ Mise à jour quotidienne: ${data.predictions_count} prédictions`)
        await fetchTodayMatches()
        return data
      } else {
        throw new Error(data.error)
      }
    } catch (err) {
      console.error('Erreur mise à jour quotidienne:', err)
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }

  const getTeamElo = async (teamName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/team-elo/${encodeURIComponent(teamName)}`)
      const data = await response.json()
      
      if (data.success) {
        return data.elo
      } else {
        throw new Error(data.error)
      }
    } catch (err) {
      console.error('Erreur récupération ELO:', err)
      return null
    }
  }

  const getTopTeams = async (limit = 20) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/top-teams?limit=${limit}`)
      const data = await response.json()
      
      if (data.success) {
        return data.top_teams
      } else {
        throw new Error(data.error)
      }
    } catch (err) {
      console.error('Erreur top équipes:', err)
      return []
    }
  }

  const generateFallbackMatches = () => {
    // Données d'exemple en cas d'erreur API
    return [
      {
        id: 1,
        date: new Date().toISOString(),
        status: "NS",
        league: "Premier League",
        league_id: 39,
        home_team: "Manchester City",
        away_team: "Arsenal",
        home_elo: 2045,
        away_elo: 1987,
        elo_diff: 58,
        kickoff: "17:30",
        finished: false,
        probabilities: {
          home_win: 0.58,
          draw: 0.24,
          away_win: 0.18,
          home_or_draw: 0.82,
          away_or_draw: 0.42,
          home_or_away: 0.76,
          over_2_5: 0.54,
          under_2_5: 0.46,
          btts_yes: 0.51,
          btts_no: 0.49
        },
        best_bet: {
          name: "Victoire Dom.",
          prob: 0.58,
          type: "1"
        }
      },
      {
        id: 2,
        date: new Date().toISOString(),
        status: "NS",
        league: "La Liga",
        league_id: 140,
        home_team: "Real Madrid",
        away_team: "Barcelona",
        home_elo: 2063,
        away_elo: 2095,
        elo_diff: -32,
        kickoff: "21:00",
        finished: false,
        probabilities: {
          home_win: 0.48,
          draw: 0.27,
          away_win: 0.25,
          home_or_draw: 0.75,
          away_or_draw: 0.52,
          home_or_away: 0.73,
          over_2_5: 0.51,
          under_2_5: 0.49,
          btts_yes: 0.53,
          btts_no: 0.47
        },
        best_bet: {
          name: "BTTS Oui",
          prob: 0.53,
          type: "BTTS"
        }
      }
    ]
  }

  // Auto-refresh toutes les 30 minutes
  useEffect(() => {
    fetchTodayMatches()
    
    const interval = setInterval(() => {
      fetchTodayMatches()
    }, 30 * 60 * 1000) // 30 minutes

    return () => clearInterval(interval)
  }, [])

  const value = {
    matches,
    loading,
    error,
    lastUpdate,
    fetchTodayMatches,
    updateElos,
    runDailyUpdate,
    getTeamElo,
    getTopTeams,
    refreshData: fetchTodayMatches
  }

  return (
    <LiveDataContext.Provider value={value}>
      {children}
    </LiveDataContext.Provider>
  )
}

