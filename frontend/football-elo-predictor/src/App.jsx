import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Calendar, TrendingUp, Home, Plane, Target, BarChart3, RefreshCw, Clock, Wifi, WifiOff } from 'lucide-react'
import { LiveDataProvider, useLiveData } from './components/LiveDataProvider.jsx'
import './App.css'

function MatchesDisplay() {
  const { 
    matches, 
    loading, 
    error, 
    lastUpdate, 
    refreshData, 
    runDailyUpdate 
  } = useLiveData()

  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await refreshData()
    setIsRefreshing(false)
  }

  const handleDailyUpdate = async () => {
    setIsRefreshing(true)
    await runDailyUpdate()
    setIsRefreshing(false)
  }

  const formatPercentage = (value) => {
    return (value * 100).toFixed(1) + '%'
  }

  const getEloDiffColor = (diff) => {
    if (Math.abs(diff) < 50) return 'bg-green-100 text-green-800'
    if (Math.abs(diff) < 100) return 'bg-yellow-100 text-yellow-800'
    if (Math.abs(diff) < 200) return 'bg-orange-100 text-orange-800'
    return 'bg-red-100 text-red-800'
  }

  const getBestBet = (probabilities) => {
    if (!probabilities) return null
    
    const bets = [
      { name: 'Victoire Dom.', prob: probabilities.home_win, type: '1' },
      { name: 'Match Nul', prob: probabilities.draw, type: 'X' },
      { name: 'Victoire Ext.', prob: probabilities.away_win, type: '2' },
      { name: 'Plus 2.5', prob: probabilities.over_2_5, type: 'O2.5' },
      { name: 'Moins 2.5', prob: probabilities.under_2_5, type: 'U2.5' },
      { name: 'BTTS Oui', prob: probabilities.btts_yes, type: 'BTTS' }
    ]
    
    return bets.reduce((best, current) => 
      current.prob > best.prob ? current : best
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center justify-center gap-2">
            <Calendar className="h-8 w-8" />
            Analyse des Matchs du Jour
          </h1>
          <p className="text-gray-600">
            Probabilités de paris calculées selon les écarts ELO des équipes
          </p>
          
          {/* Indicateur de statut */}
          <div className="flex items-center justify-center gap-4 mt-4">
            <div className="flex items-center gap-2">
              {error ? (
                <WifiOff className="h-4 w-4 text-red-500" />
              ) : (
                <Wifi className="h-4 w-4 text-green-500" />
              )}
              <span className="text-sm text-gray-600">
                {error ? 'Mode hors ligne' : 'Données en direct'}
              </span>
            </div>
            
            {lastUpdate && (
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Mis à jour: {lastUpdate.toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            <span className="font-semibold">{matches.length} matchs analysés</span>
          </div>
          
          <div className="flex gap-2">
            <Button 
              onClick={handleRefresh} 
              disabled={isRefreshing}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Actualisation...' : 'Actualiser'}
            </Button>
            
            <Button 
              onClick={handleDailyUpdate} 
              disabled={isRefreshing}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              Mise à jour complète
            </Button>
          </div>
        </div>

        {error && (
          <Card className="mb-6 border-yellow-200 bg-yellow-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <WifiOff className="h-5 w-5 text-yellow-600" />
                <p className="text-yellow-800">
                  Connexion API indisponible. Affichage des données d'exemple.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {loading ? (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
              <p>Analyse des matchs en cours...</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {matches.map((match) => {
              const bestBet = getBestBet(match.probabilities)
              
              return (
                <Card key={match.id} className="overflow-hidden">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Home className="h-4 w-4" />
                          {match.home_team} vs {match.away_team}
                          <Plane className="h-4 w-4" />
                        </CardTitle>
                        <CardDescription>
                          {match.league} • {match.kickoff || 'TBD'}
                        </CardDescription>
                      </div>
                      <div className="text-right">
                        <Badge className={getEloDiffColor(match.elo_diff)}>
                          Écart: {match.elo_diff > 0 ? '+' : ''}{match.elo_diff}
                        </Badge>
                        <div className="text-sm text-gray-600 mt-1">
                          ELO: {Math.round(match.home_elo)} - {Math.round(match.away_elo)}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    {match.probabilities ? (
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        {/* Résultats du match */}
                        <div>
                          <h4 className="font-semibold mb-2 flex items-center gap-1">
                            <Target className="h-4 w-4" />
                            Résultat
                          </h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>Victoire Dom.</span>
                              <Badge variant="secondary">{formatPercentage(match.probabilities.home_win)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>Match Nul</span>
                              <Badge variant="secondary">{formatPercentage(match.probabilities.draw)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>Victoire Ext.</span>
                              <Badge variant="secondary">{formatPercentage(match.probabilities.away_win)}</Badge>
                            </div>
                          </div>
                        </div>

                        {/* Double Chance */}
                        <div>
                          <h4 className="font-semibold mb-2">Double Chance</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>1X</span>
                              <Badge variant="outline">{formatPercentage(match.probabilities.home_or_draw)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>X2</span>
                              <Badge variant="outline">{formatPercentage(match.probabilities.away_or_draw)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>12</span>
                              <Badge variant="outline">{formatPercentage(match.probabilities.home_or_away)}</Badge>
                            </div>
                          </div>
                        </div>

                        {/* Buts et BTTS */}
                        <div>
                          <h4 className="font-semibold mb-2">Buts & BTTS</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>Plus 2.5</span>
                              <Badge variant="destructive">{formatPercentage(match.probabilities.over_2_5)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>Moins 2.5</span>
                              <Badge variant="destructive">{formatPercentage(match.probabilities.under_2_5)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>BTTS Oui</span>
                              <Badge variant="destructive">{formatPercentage(match.probabilities.btts_yes)}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>BTTS Non</span>
                              <Badge variant="destructive">{formatPercentage(match.probabilities.btts_no)}</Badge>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-gray-500">Calcul des probabilités en cours...</p>
                      </div>
                    )}

                    {bestBet && (
                      <div className="mt-4 pt-3 border-t">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Meilleur pari suggéré:</span>
                          <Badge className="bg-green-600 text-white">
                            {bestBet.name} ({formatPercentage(bestBet.prob)})
                          </Badge>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}

        <Card className="mt-8">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 text-center">
              Les probabilités sont calculées en analysant l'historique des matchs avec des écarts ELO similaires.
              L'avantage du terrain (+100 ELO) est automatiquement pris en compte dans les calculs.
              {error && " Mode hors ligne - données d'exemple affichées."}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function App() {
  return (
    <LiveDataProvider>
      <MatchesDisplay />
    </LiveDataProvider>
  )
}

export default App

