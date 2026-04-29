export type NavItem =
  | { label: string; kind: 'section'; sectionId: string }
  | { label: string; kind: 'link'; to: string }

export const NAV_ITEMS: NavItem[] = [
  { label: 'Services', kind: 'section', sectionId: 'services' },
  { label: 'Our Team', kind: 'section', sectionId: 'team' },
  { label: 'Works',    kind: 'link',    to: '/works' },
  { label: 'About',   kind: 'link',    to: '/about' },
  { label: 'Contact', kind: 'section', sectionId: 'contact' },
]
