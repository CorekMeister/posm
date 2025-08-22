const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-card border-t border-border mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            © {currentYear} x Posmiewiska.pl - wszelkie prawa zastrzeżone
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Wykonanie: <span className="text-primary font-medium">Settings.lol</span> - <span className="text-primary font-medium">CorekL</span>
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer

