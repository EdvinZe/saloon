import type { HomeMetrics } from '../api'

export type HomeStat = {
  num: string
  label: string
}

function getYearsOpen(openedAt: string, now = new Date()): number {
  const openedDate = new Date(openedAt)

  let years = now.getFullYear() - openedDate.getFullYear()

  const hasNotReachedAnniversary =
    now.getMonth() < openedDate.getMonth() ||
    (now.getMonth() === openedDate.getMonth() && now.getDate() < openedDate.getDate())

  if (hasNotReachedAnniversary) {
    years -= 1
  }

  return Math.max(years, 0)
}

function formatNumberWithSpaces(value: number): string {
  return new Intl.NumberFormat('fr-FR').format(value)
}

export function buildHomeStats(metrics: HomeMetrics): HomeStat[] {
  return [
    {
      num: `${getYearsOpen(metrics.openedAt)}+`,
      label: 'Years open',
    },
    {
      num: metrics.googleRating.toFixed(1),
      label: 'Google rating',
    },
    {
      num: formatNumberWithSpaces(metrics.happyClients),
      label: 'Happy clients',
    },
    {
      num: `${metrics.satisfactionPercent}%`,
      label: 'Satisfaction',
    },
  ]
}