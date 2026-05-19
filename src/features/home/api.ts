export type HomeMetrics = {
  openedAt: string
  googleRating: number
  happyClients: number
  satisfactionPercent: number
}

export async function getHomeMetrics(): Promise<HomeMetrics> {
  // Before change on FastAPI:
  // return _api.get('/api/v1/home/metrics').then(r => r.data)

  return Promise.resolve({
    openedAt: '2017-01-01',
    googleRating: 4.9,
    happyClients: 2400,
    satisfactionPercent: 100,
  })
}
