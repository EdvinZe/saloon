type ApiMasterService = {
  id: number
  name: string
}

type ApiMaster = {
  id: number
  name: string
  role: string
  bio: string
  initials: string
  services: ApiMasterService[]
}

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

export type MasterService = {
  id: number
  name: string
}

export type Master = {
  id: number
  name: string
  role: string
  bio: string
  initials: string
  services: MasterService[]
}

function mapMaster(apiMaster: ApiMaster): Master {
  return {
    id: apiMaster.id,
    name: apiMaster.name,
    role: apiMaster.role,
    bio: apiMaster.bio,
    initials: apiMaster.initials,
    services: apiMaster.services,
  }
}

export async function getMasters(): Promise<Master[]> {
  const response = await fetch(`${API_BASE_URL}/api/masters/public`)

  if (!response.ok) {
    throw new Error('Failed to fetch masters')
  }

  const data = await response.json() as ApiMaster[]

  return data.map(mapMaster)
}
