import { useEffect, useRef, useState } from 'react'
import { ThemeToggle } from './ThemeToggle'

const NAV_LINKS = [
  { href: '#overview', label: 'Overview' },
  { href: '#charts', label: 'Charts' },
  { href: '#vintages', label: 'Vintages' },
]

export function NavBar() {
  const navRef = useRef<HTMLElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const indicatorRef = useRef<HTMLSpanElement>(null)
  const [activeHref, setActiveHref] = useState<string>('#overview')

  useEffect(() => {
    const updateIndicator = () => {
      const listEl = listRef.current
      const indicatorEl = indicatorRef.current
      if (!listEl || !indicatorEl) return
      const activeEl = listEl.querySelector(`a[href="${activeHref}"]`) as HTMLElement | null
      if (!activeEl) return
      indicatorEl.style.width = `${activeEl.offsetWidth}px`
      indicatorEl.style.transform = `translateX(${activeEl.offsetLeft}px)`
    }
    updateIndicator()
    window.addEventListener('resize', updateIndicator)
    return () => window.removeEventListener('resize', updateIndicator)
  }, [activeHref])

  useEffect(() => {
    const handleScroll = () => {
      const scrollPos = window.scrollY + 120
      for (let i = NAV_LINKS.length - 1; i >= 0; i--) {
        const href = NAV_LINKS[i].href
        const el = document.querySelector(href)
        if (el) {
          const rect = el.getBoundingClientRect()
          const top = window.scrollY + rect.top
          if (scrollPos >= top) {
            setActiveHref(href)
            break
          }
        }
      }
    }
    handleScroll()
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const openMethodology = () => {
    const dialog = document.getElementById('methodology') as HTMLDialogElement | null
    dialog?.showModal()
  }

  return (
    <header className="nav" ref={navRef}>
      <div className="nav-inner">
        <a className="brand" href="#top" aria-label="Windward home">
          <svg
            className="od-icon brand-mark"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M3 8h11a3 3 0 1 0-3-3" />
            <path d="M3 12h15a3 3 0 1 1-3 3" />
            <path d="M3 16h8a2.5 2.5 0 1 1-2.5 2.5" />
          </svg>
          <span>Windward</span>
        </a>
        <nav className="nav-links" aria-label="Sections">
          <div className="nav-links-list" ref={listRef}>
            <span className="nav-indicator" ref={indicatorRef} aria-hidden="true" />
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className={activeHref === link.href ? 'is-active' : undefined}
                onClick={(e) => {
                  setActiveHref(link.href)
                  const el = document.querySelector(link.href)
                  if (el) {
                    e.preventDefault()
                    const nav = navRef.current
                    const offset = nav ? nav.getBoundingClientRect().height + 8 : 64
                    const top = window.scrollY + el.getBoundingClientRect().top - offset
                    window.scrollTo({ top, behavior: 'smooth' })
                  }
                }}
              >
                {link.label}
              </a>
            ))}
          </div>
        </nav>
        <div className="nav-actions">
          <ThemeToggle />
          <button className="btn btn-secondary btn-compact nav-methodology" type="button" onClick={openMethodology}>
            Methodology
          </button>
        </div>
      </div>
    </header>
  )
}
