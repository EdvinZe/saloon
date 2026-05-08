import type { Master } from '../../shared/data/mockData'
import { MOCK_MASTERS } from '../../shared/data/mockData'

export async function getMasters(): Promise<Master[]> {
  return Promise.resolve(
    MOCK_MASTERS.filter(master => master.isActive)
  )
}
