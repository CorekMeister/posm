import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, LogOut, User, Settings } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import PlayerForm from './PlayerForm.jsx'
import PlayerCard from './PlayerCard.jsx'

const AdminPanel = ({ admin, token, onLogout }) => {
  const [players, setPlayers] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingPlayer, setEditingPlayer] = useState(null)
  const [loading, setLoading] = useState(true)

  // Przykładowe dane
  const mockPlayers = [
    {
      id: 1,
      nickname: "inary_",
      reason: "Tworzył serwer z pewną ekipą, w momencie gdy serwer zaczął generować przychód odciął całą ekipę od projektu, aby zyskać cały hajs dla siebie.",
      reported_by: "CorekL",
      created_at: "2024-01-15T10:30:00Z",
      is_active: true
    },
    {
      id: 2,
      nickname: "klakier0",
      reason: "Kolega inary_ uczestniczący w całym przedsięwzięciu jako wspólnik.",
      reported_by: "CorekL",
      created_at: "2024-01-15T10:35:00Z",
      is_active: true
    },
    {
      id: 3,
      nickname: "Cl4stk0_",
      reason: "Były administrator bagmc.pl i kilku innych serwerów, zdobywa pozycję poprzez bycie 'lizodupem'",
      reported_by: "CorekL",
      created_at: "2024-01-15T10:40:00Z",
      is_active: true
    }
  ]

  useEffect(() => {
    // Symulacja ładowania danych
    setTimeout(() => {
      setPlayers(mockPlayers)
      setLoading(false)
    }, 1000)
  }, [])

  const handleAddPlayer = () => {
    setEditingPlayer(null)
    setShowForm(true)
  }

  const handleEditPlayer = (player) => {
    setEditingPlayer(player)
    setShowForm(true)
  }

  const handleDeletePlayer = async (playerId) => {
    if (window.confirm('Czy na pewno chcesz usunąć tego gracza?')) {
      // Symulacja API call
      setPlayers(players.filter(p => p.id !== playerId))
    }
  }

  const handleFormSubmit = (playerData) => {
    if (editingPlayer) {
      // Edycja
      setPlayers(players.map(p => 
        p.id === editingPlayer.id 
          ? { ...p, ...playerData, updated_at: new Date().toISOString() }
          : p
      ))
    } else {
      // Dodawanie
      const newPlayer = {
        id: Date.now(),
        ...playerData,
        created_at: new Date().toISOString(),
        is_active: true
      }
      setPlayers([newPlayer, ...players])
    }
    setShowForm(false)
    setEditingPlayer(null)
  }

  const handleFormCancel = () => {
    setShowForm(false)
    setEditingPlayer(null)
  }

  if (showForm) {
    return (
      <PlayerForm
        player={editingPlayer}
        onSubmit={handleFormSubmit}
        onCancel={handleFormCancel}
      />
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header panelu */}
      <header className="bg-card border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-primary p-2 rounded-lg">
                <Settings className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">
                  Panel Administratora
                </h1>
                <p className="text-sm text-muted-foreground">
                  Zarządzanie czarną listą graczy
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm text-foreground">{admin.username}</span>
                {admin.is_super_admin && (
                  <Badge variant="secondary" className="text-xs">
                    Super Admin
                  </Badge>
                )}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={onLogout}
                className="border-border hover:bg-accent"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Wyloguj
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Główna zawartość */}
      <main className="container mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* Statystyki */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Łącznie graczy</p>
                    <p className="text-2xl font-bold text-foreground">{players.length}</p>
                  </div>
                  <div className="bg-primary/10 p-2 rounded-lg">
                    <User className="w-6 h-6 text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Aktywne wpisy</p>
                    <p className="text-2xl font-bold text-foreground">
                      {players.filter(p => p.is_active).length}
                    </p>
                  </div>
                  <div className="bg-green-500/10 p-2 rounded-lg">
                    <User className="w-6 h-6 text-green-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Dzisiaj dodano</p>
                    <p className="text-2xl font-bold text-foreground">0</p>
                  </div>
                  <div className="bg-blue-500/10 p-2 rounded-lg">
                    <Plus className="w-6 h-6 text-blue-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Akcje */}
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-foreground">
              Zarządzanie graczami
            </h2>
            <Button
              onClick={handleAddPlayer}
              className="bg-primary hover:bg-primary/90"
            >
              <Plus className="w-4 h-4 mr-2" />
              Dodaj gracza
            </Button>
          </div>

          {/* Lista graczy */}
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Ładowanie...</p>
              </div>
            ) : players.length === 0 ? (
              <Card className="bg-card border-border">
                <CardContent className="p-8 text-center">
                  <User className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">
                    Brak graczy na liście
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Dodaj pierwszego gracza do czarnej listy
                  </p>
                  <Button onClick={handleAddPlayer} className="bg-primary hover:bg-primary/90">
                    <Plus className="w-4 h-4 mr-2" />
                    Dodaj gracza
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                {players.map((player) => (
                  <Card key={player.id} className="bg-card border-border">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <img
                            src={`https://minotar.net/avatar/${player.nickname}/32`}
                            alt={`Avatar ${player.nickname}`}
                            className="w-8 h-8 rounded border border-border"
                            onError={(e) => {
                              e.target.src = `https://minotar.net/avatar/steve/32`;
                            }}
                          />
                          <div>
                            <h3 className="font-semibold text-foreground">
                              {player.nickname}
                            </h3>
                            <p className="text-xs text-muted-foreground">
                              ID: {player.id}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex space-x-1">
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => handleEditPlayer(player)}
                            className="h-8 w-8 border-border hover:bg-accent"
                          >
                            <Edit className="w-3 h-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => handleDeletePlayer(player.id)}
                            className="h-8 w-8 border-border hover:bg-destructive hover:text-destructive-foreground"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div>
                          <p className="text-xs text-muted-foreground">Powód:</p>
                          <p className="text-sm text-foreground line-clamp-3">
                            {player.reason}
                          </p>
                        </div>
                        
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Zgłosił: {player.reported_by}</span>
                          <span>
                            {new Date(player.created_at).toLocaleDateString('pl-PL')}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default AdminPanel

