import { useState } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input.jsx'
import { Button } from '@/components/ui/button.jsx'

const SearchBar = ({ onSearch, placeholder = "Wyszukaj gracza..." }) => {
  const [searchTerm, setSearchTerm] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(searchTerm)
  }

  const handleClear = () => {
    setSearchTerm('')
    onSearch('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 w-full max-w-md">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 bg-card border-border focus:border-primary"
        />
      </div>
      <Button 
        type="submit" 
        variant="default"
        className="bg-primary hover:bg-primary/90"
      >
        Szukaj
      </Button>
      {searchTerm && (
        <Button 
          type="button" 
          variant="outline"
          onClick={handleClear}
          className="border-border hover:bg-accent"
        >
          Wyczyść
        </Button>
      )}
    </form>
  )
}

export default SearchBar

