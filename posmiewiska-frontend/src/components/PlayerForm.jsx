import { useState } from 'react'
import { ArrowLeft, Save, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'

const PlayerForm = ({ player, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    nickname: player?.nickname || '',
    reason: player?.reason || '',
    reported_by: player?.reported_by || ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const validateForm = () => {
    const newErrors = {}

    // Walidacja nicku
    if (!formData.nickname.trim()) {
      newErrors.nickname = 'Nick gracza jest wymagany'
    } else if (formData.nickname.length < 3 || formData.nickname.length > 16) {
      newErrors.nickname = 'Nick musi mieć 3-16 znaków'
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.nickname)) {
      newErrors.nickname = 'Nick może zawierać tylko litery, cyfry i podkreślniki'
    }

    // Walidacja powodu
    if (!formData.reason.trim()) {
      newErrors.reason = 'Powód zgłoszenia jest wymagany'
    } else if (formData.reason.length < 10) {
      newErrors.reason = 'Powód musi mieć co najmniej 10 znaków'
    }

    // Walidacja zgłaszającego
    if (!formData.reported_by.trim()) {
      newErrors.reported_by = 'Pole "zgłaszający" jest wymagane'
    } else if (formData.reported_by.length < 3) {
      newErrors.reported_by = 'Nazwa zgłaszającego musi mieć co najmniej 3 znaki'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    
    try {
      // Symulacja API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      onSubmit(formData)
    } catch (error) {
      console.error('Error submitting form:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
    
    // Usuwanie błędu po zmianie wartości
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      })
    }
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto max-w-2xl">
        <div className="mb-6">
          <Button
            variant="outline"
            onClick={onCancel}
            className="border-border hover:bg-accent"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Powrót do panelu
          </Button>
        </div>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-foreground">
              {player ? 'Edytuj gracza' : 'Dodaj nowego gracza'}
            </CardTitle>
            <p className="text-muted-foreground">
              {player 
                ? 'Zaktualizuj informacje o graczu na czarnej liście'
                : 'Dodaj gracza do czarnej listy'
              }
            </p>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Nick gracza */}
              <div className="space-y-2">
                <label htmlFor="nickname" className="text-sm font-medium text-foreground">
                  Nick gracza *
                </label>
                <Input
                  id="nickname"
                  name="nickname"
                  type="text"
                  value={formData.nickname}
                  onChange={handleChange}
                  placeholder="np. Steve123"
                  className={`bg-card border-border focus:border-primary ${
                    errors.nickname ? 'border-destructive' : ''
                  }`}
                  maxLength={16}
                />
                {errors.nickname && (
                  <Alert className="border-destructive">
                    <AlertDescription className="text-destructive text-sm">
                      {errors.nickname}
                    </AlertDescription>
                  </Alert>
                )}
                <p className="text-xs text-muted-foreground">
                  3-16 znaków, tylko litery, cyfry i podkreślniki
                </p>
              </div>

              {/* Powód zgłoszenia */}
              <div className="space-y-2">
                <label htmlFor="reason" className="text-sm font-medium text-foreground">
                  Powód zgłoszenia *
                </label>
                <Textarea
                  id="reason"
                  name="reason"
                  value={formData.reason}
                  onChange={handleChange}
                  placeholder="Opisz szczegółowo powód dodania gracza do czarnej listy..."
                  className={`bg-card border-border focus:border-primary min-h-[120px] ${
                    errors.reason ? 'border-destructive' : ''
                  }`}
                  maxLength={1000}
                />
                {errors.reason && (
                  <Alert className="border-destructive">
                    <AlertDescription className="text-destructive text-sm">
                      {errors.reason}
                    </AlertDescription>
                  </Alert>
                )}
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Minimum 10 znaków</span>
                  <span>{formData.reason.length}/1000</span>
                </div>
              </div>

              {/* Zgłaszający */}
              <div className="space-y-2">
                <label htmlFor="reported_by" className="text-sm font-medium text-foreground">
                  Zgłaszający *
                </label>
                <Input
                  id="reported_by"
                  name="reported_by"
                  type="text"
                  value={formData.reported_by}
                  onChange={handleChange}
                  placeholder="Kto zgłasza tego gracza"
                  className={`bg-card border-border focus:border-primary ${
                    errors.reported_by ? 'border-destructive' : ''
                  }`}
                  maxLength={100}
                />
                {errors.reported_by && (
                  <Alert className="border-destructive">
                    <AlertDescription className="text-destructive text-sm">
                      {errors.reported_by}
                    </AlertDescription>
                  </Alert>
                )}
                <p className="text-xs text-muted-foreground">
                  Nazwa osoby lub organizacji zgłaszającej
                </p>
              </div>

              {/* Podgląd awatara */}
              {formData.nickname && formData.nickname.length >= 3 && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Podgląd awatara
                  </label>
                  <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
                    <img
                      src={`https://minotar.net/avatar/${formData.nickname}/64`}
                      alt={`Avatar ${formData.nickname}`}
                      className="w-16 h-16 rounded border border-border"
                      onError={(e) => {
                        e.target.src = `https://minotar.net/avatar/steve/64`;
                      }}
                    />
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        {formData.nickname}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Avatar z Minotar.net
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Przyciski */}
              <div className="flex space-x-3 pt-4">
                <Button
                  type="submit"
                  className="flex-1 bg-primary hover:bg-primary/90"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      {player ? 'Aktualizowanie...' : 'Dodawanie...'}
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      {player ? 'Zaktualizuj' : 'Dodaj gracza'}
                    </>
                  )}
                </Button>
                
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                  className="border-border hover:bg-accent"
                  disabled={loading}
                >
                  <X className="w-4 h-4 mr-2" />
                  Anuluj
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default PlayerForm

