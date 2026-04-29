import type { NavigateFunction } from 'react-router-dom'

const SECTION_PAGE: Record<string, string> = {
  services: '/',
  team:     '/about',
  contact:  '/about',
}

export function scrollToSection(sectionId: string, pathname: string, navigate: NavigateFunction) {
  const targetPage = SECTION_PAGE[sectionId] ?? '/'

  if (pathname === targetPage) {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' })
  } else {
    navigate(targetPage)
    setTimeout(() => {
      document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' })
    }, 300)
  }
}
