import { useState, useEffect } from 'react'
import { AlertCircle, Loader2 } from 'lucide-react'
import PlayerCard from './PlayerCard.jsx'
import SearchBar from './SearchBar.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'

const PlayerGrid = () => {
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalPlayers, setTotalPlayers] = useState(0)

  // Przykładowe dane dla demonstracji
  const mockPlayers = [
    {
      id: 1,
      nickname: "inary_",
      reason: "Tworzył serwer z pewną ekipą, w momencie gdy serwer zaczął generować przychód odciął całą ekipę od projektu, aby zyskać cały hajs dla siebie.",
      reported_by: "CorekL",
      created_at: "2024-01-15T10:30:00Z",
      avatar_url: "https://minotar.net/avatar/inary_/64"
    },
    {
      id: 2,
      nickname: "klakier0",
      reason: "Kolega inary_ uczestniczący w całym przedsięwzięciu jako wspólnik.",
      reported_by: "CorekL",
      created_at: "2024-01-15T10:35:00Z",
      avatar_url: "https://minotar.net/avatar/klakier0/64"
    },
    {
      id: 3,
      nickname: "Cl4stk0_",
      reason: "Były administrator bagmc.pl i kilku innych serwerów, zdobywa pozycję poprzez bycie 'lizodupem'",
      reported_by: "CorekL",
      created_at: "2024-01-15T10:40:00Z",
      avatar_url: "https://minotar.net/avatar/Cl4stk0_/64"
    }
  ]

  const fetchPlayers = async (page = 1, search = '') => {
    setLoading(true)
    setError(null)
    
    try {
      // Symulacja API call - w rzeczywistości będzie to wywołanie do backendu
      await new Promise(resolve => setTimeout(resolve, 1000)) // Symulacja opóźnienia
      
      let filteredPlayers = mockPlayers
      
      if (search) {
        filteredPlayers = mockPlayers.filter(player =>
          player.nickname.toLowerCase().includes(search.toLowerCase()) ||
          player.reason.toLowerCase().includes(search.toLowerCase())
        )
      }
      
      setPlayers(filteredPlayers)
      setTotalPlayers(filteredPlayers.length)
      setTotalPages(Math.ceil(filteredPlayers.length / 20))
      setCurrentPage(page)
    } catch (err) {
      setError('Błąd podczas ładowania listy graczy')
      console.error('Error fetching players:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPlayers(1, searchTerm)
  }, [])

  const handleSearch = (term) => {
    setSearchTerm(term)
    setCurrentPage(1)
    fetchPlayers(1, term)
  }

  const handlePageChange = (page) => {
    fetchPlayers(page, searchTerm)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin text-primary" />
          <span className="text-muted-foreground">Ładowanie listy graczy...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert className="border-destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => fetchPlayers(currentPage, searchTerm)}
            className="ml-4"
          >
            Spróbuj ponownie
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Pasek wyszukiwania */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <SearchBar onSearch={handleSearch} />
        <div className="text-sm text-muted-foreground">
          Znaleziono {totalPlayers} graczy
        </div>
      </div>

      {/* Siatka graczy */}
      {players.length === 0 ? (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            Brak wyników
          </h3>
          <p className="text-muted-foreground">
            {searchTerm 
              ? `Nie znaleziono graczy pasujących do "${searchTerm}"`
              : "Lista graczy jest pusta"
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {players.map((player) => (
            <PlayerCard key={player.id} player={player} />
          ))}
        </div>
      )}

      {/* Paginacja */}
      {totalPages > 1 && (
        <div className="flex justify-center space-x-2 pt-6">
          <Button
            variant="outline"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="border-border hover:bg-accent"
          >
            Poprzednia
          </Button>
          
          <div className="flex items-center space-x-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page = i + 1
              return (
                <Button
                  key={page}
                  variant={currentPage === page ? "default" : "outline"}
                  onClick={() => handlePageChange(page)}
                  className={currentPage === page 
                    ? "bg-primary hover:bg-primary/90" 
                    : "border-border hover:bg-accent"
                  }
                >
                  {page}
                </Button>
              )
            })}
          </div>
          
          <Button
            variant="outline"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="border-border hover:bg-accent"
          >
            Następna
          </Button>
        </div>
      )}
    </div>
  )
}

export default PlayerGrid

