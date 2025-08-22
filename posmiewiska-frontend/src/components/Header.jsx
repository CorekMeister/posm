import { Moon, Sun, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'

const Header = ({ darkMode, toggleDarkMode }) => {
  return (
    <header className="bg-card border-b border-border">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo i tytuł */}
          <div className="flex items-center space-x-3">
            <div className="bg-primary p-2 rounded-lg">
              <Shield className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Posmiewiska.pl
              </h1>
              <p className="text-sm text-muted-foreground">
                Czarna lista graczy Minecraft
              </p>
            </div>
          </div>

          {/* Przełącznik dark mode */}
          <Button
            variant="outline"
            size="icon"
            onClick={toggleDarkMode}
            className="border-border hover:bg-accent"
          >
            {darkMode ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </header>
  )
}

export default Header

