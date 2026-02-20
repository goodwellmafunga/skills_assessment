import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const location = useLocation()

  const navItem = (path, label) => {
    const active = location.pathname === path

    return (
      <Link
        to={path}
        className={`
          px-4 py-2 rounded-pill text-sm transition-all duration-200 ease-out
          ${active
            ? 'bg-primary-soft text-primary'
            : 'text-text-secondary hover:text-primary'}
        `}
      >
        {label}
      </Link>
    )
  }

  return (
    <div className="min-h-screen bg-background text-text-primary">

      {/* HEADER */}
      <header className="sticky top-0 z-20 bg-surface border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

          {/* Brand */}
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Skills Intelligence Workspace
            </h1>
            <p className="text-xs text-text-tertiary mt-1">
              Performance & Capability Analytics
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex items-center gap-4">
            {navItem('/dashboard', 'Dashboard')}
            {navItem('/questionnaire', 'Questionnaire')}

            <button
              className="btn-primary"
              onClick={() => {
                localStorage.clear()
                window.location.href = '/login'
              }}
            >
              Logout
            </button>
          </nav>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {children}
      </main>

    </div>
  )
}