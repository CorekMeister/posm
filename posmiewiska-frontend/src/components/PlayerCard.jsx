import { Card, CardContent } from '@/components/ui/card.jsx'

const PlayerCard = ({ player }) => {
  return (
    <Card className="bg-card border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/20">
      <CardContent className="p-6">
        <div className="flex flex-col items-center text-center space-y-4">
          {/* Avatar gracza z Minotar */}
          <div className="relative">
            <img
              src={player.avatar_url || `https://minotar.net/avatar/${player.nickname}/64`}
              alt={`Avatar ${player.nickname}`}
              className="w-16 h-16 rounded-lg border-2 border-primary/30"
              onError={(e) => {
                e.target.src = `https://minotar.net/avatar/steve/64`;
              }}
            />
          </div>
          
          {/* Nick gracza */}
          <h3 className="text-xl font-bold text-primary">
            {player.nickname}
          </h3>
          
          {/* Powód zgłoszenia */}
          <p className="text-sm text-muted-foreground leading-relaxed">
            {player.reason}
          </p>
          
          {/* Informacje o zgłoszeniu */}
          <div className="w-full pt-4 border-t border-border">
            <p className="text-xs text-muted-foreground">
              <span className="text-primary font-medium">Dodany przez:</span> {player.reported_by}
            </p>
            {player.created_at && (
              <p className="text-xs text-muted-foreground mt-1">
                <span className="text-primary font-medium">Data:</span>{' '}
                {new Date(player.created_at).toLocaleDateString('pl-PL')}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default PlayerCard

