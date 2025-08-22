import { useState, useEffect } from 'react'
import { Shield } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import Header from './components/Header.jsx'
import Footer from './components/Footer.jsx'
import PlayerGrid from './components/PlayerGrid.jsx'
import AdminLogin from './components/AdminLogin.jsx'
import AdminPanel from './components/AdminPanel.jsx'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [currentView, setCurrentView] = useState('public') // 'public', 'admin-login', 'admin-panel'
  const [admin, setAdmin] = useState(null)
  const [token, setToken] = useState(null)

  useEffect(() => {
    // Sprawdzenie preferencji użytkownika z localStorage
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      setDarkMode(savedTheme === 'dark')
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setDarkMode(prefersDark)
    }

    // Sprawdzenie czy admin jest zalogowany
    const savedToken = localStorage.getItem('admin_token')
    const savedAdmin = localStorage.getItem('admin_data')
    
    if (savedToken && savedAdmin) {
      try {
        setToken(savedToken)
        setAdmin(JSON.parse(savedAdmin))
        setCurrentView('admin-panel')
      } catch (error) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_data')
      }
    }
  }, [])

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  const handleAdminLogin = (adminData, authToken) => {
    setAdmin(adminData)
    setToken(authToken)
    setCurrentView('admin-panel')
    
    // Zapisanie w localStorage
    localStorage.setItem('admin_token', authToken)
    localStorage.setItem('admin_data', JSON.stringify(adminData))
  }

  const handleAdminLogout = () => {
    setAdmin(null)
    setToken(null)
    setCurrentView('public')
    
    // Usunięcie z localStorage
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_data')
  }

  const showAdminLogin = () => {
    setCurrentView('admin-login')
  }

  const showPublicView = () => {
    setCurrentView('public')
  }

  // Renderowanie panelu administratora
  if (currentView === 'admin-panel' && admin && token) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <AdminPanel 
          admin={admin} 
          token={token} 
          onLogout={handleAdminLogout} 
        />
      </div>
    )
  }

  // Renderowanie logowania administratora
  if (currentView === 'admin-login') {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <AdminLogin onLogin={handleAdminLogin} />
        <div className="fixed top-4 left-4">
          <Button
            variant="outline"
            onClick={showPublicView}
            className="border-border hover:bg-accent"
          >
            ← Powrót do strony głównej
          </Button>
        </div>
      </div>
    )
  }

  // Renderowanie widoku publicznego
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-foreground mb-2">
              Lista zgłoszonych graczy
            </h2>
            <p className="text-muted-foreground mb-4">
              Gracze zgłoszeni przez społeczność za nieodpowiednie zachowanie
            </p>
            
            {/* Przycisk dostępu do panelu admina */}
            <div className="flex justify-center">
              <Button
                variant="outline"
                onClick={showAdminLogin}
                className="border-border hover:bg-accent"
              >
                <Shield className="w-4 h-4 mr-2" />
                Panel Administratora
              </Button>
            </div>
          </div>
          
          <PlayerGrid />
        </div>
      </main>
      
      <Footer />
    </div>
  )
}

export default App
