import { create } from 'zustand'
import type { Service, Master } from '../../../shared/data/mockData'

interface BookingState {
  step: number
  service: Service | null
  date: string | null
  time: string | null
  master: Master | null
  clientName: string
  clientPhone: string
}

interface BookingActions {
  setService: (s: Service) => void
  setDateTime: (date: string, time: string) => void
  setMaster: (m: Master) => void
  setClientName: (name: string) => void
  setClientPhone: (phone: string) => void
}

export type BookingStore = BookingState & BookingActions

export const useBookingStore = create<BookingStore>((set) => ({
  step: 1,
  service: null,
  date: null,
  time: null,
  master: null,
  clientName: '',
  clientPhone: '',

  // Step advances forward only — re-selecting a service on step 4 keeps step 4 visible
  setService: (service) => set((state) => ({ service, step: Math.max(state.step, 2) })),
  setDateTime: (date, time) => set((state) => ({ date, time, step: Math.max(state.step, 3) })),
  setMaster: (master) => set((state) => ({ master, step: Math.max(state.step, 4) })),
  setClientName: (clientName) => set({ clientName }),
  setClientPhone: (clientPhone) => set({ clientPhone }),
}))
