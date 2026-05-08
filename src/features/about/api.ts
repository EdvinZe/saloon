import type { ContactItem } from '../../shared/data/mockData'
import { CONTACT_ITEMS } from '../../shared/data/mockData'

export async function getAboutContactInfo(): Promise<ContactItem[]> {
  return Promise.resolve(
    CONTACT_ITEMS.filter(item => item.isActive)
  )
}