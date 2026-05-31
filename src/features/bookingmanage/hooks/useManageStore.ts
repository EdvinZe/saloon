import { create } from 'zustand'
import type { Master } from '../../masters/api'
import type { Service } from '../../services/api'
import type { ManagedBooking } from '../../booking/api'

interface ManageState {
  token: string | null
  booking: ManagedBooking | null
  newService: Service | null
  newSlot: { date: string; time: string } | null
  newMaster: Master | null
  step: number  // 1 = service, 2 = time, 3 = master/confirm
}

interface ManageActions {
  setToken: (t: string) => void
  setBooking: (b: ManagedBooking) => void
  setNewService: (s: Service) => void
  setNewSlot: (date: string, time: string) => void
  setNewMaster: (m: Master | null) => void
  reset: () => void
}

export type ManageStore = ManageState & ManageActions

export const useManageStore = create<ManageStore>((set) => ({
  token: null,
  booking: null,
  newService: null,
  newSlot: null,
  newMaster: null,
  step: 1,

  setToken: (token) => set({ token }),
  setBooking: (booking) => set({ booking }),
  setNewService: (newService) => set((s) => ({
    newService,
    step: Math.max(s.step, 2),
    newSlot: null,
    newMaster: null,
  })),
  setNewSlot: (date, time) => set((s) => ({
    newSlot: { date, time },
    step: Math.max(s.step, 3),
    newMaster: null,
  })),
  setNewMaster: (newMaster) => set({ newMaster }),
  reset: () => set({ newService: null, newSlot: null, newMaster: null, step: 1 }),
}))
