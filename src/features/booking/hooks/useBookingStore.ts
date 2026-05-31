import { create } from 'zustand'
import type { Master } from '../../masters/api'
import type { Service } from '../../services/api'

interface BookingState {
  step: number
  service: Service | null
  date: string | null
  time: string | null
  master: Master | null
  customerFirstName: string
  customerLastName: string
  customerPhone: string
  customerEmail: string
}

interface BookingActions {
  setService: (s: Service) => void
  setDateTime: (date: string, time: string) => void
  setMaster: (m: Master) => void
  setCustomerFirstName: (firstName: string) => void
  setCustomerLastName: (lastName: string) => void
  setCustomerPhone: (phone: string) => void
  setCustomerEmail: (email: string) => void
  clearSelectedTimeAndMaster: () => void
}

export type BookingStore = BookingState & BookingActions

export const useBookingStore = create<BookingStore>((set) => ({
  step: 1,
  service: null,
  date: null,
  time: null,
  master: null,
  customerFirstName: '',
  customerLastName: '',
  customerPhone: '',
  customerEmail: '',

  setService: (service) => set((state) => {
    if (state.service?.id === service.id) {
      return { service, step: Math.max(state.step, 2) }
    }

    return {
      service,
      date: null,
      time: null,
      master: null,
      step: 2,
    }
  }),
  setDateTime: (date, time) => set((state) => ({ date, time, step: Math.max(state.step, 3) })),
  setMaster: (master) => set((state) => ({ master, step: Math.max(state.step, 4) })),
  setCustomerFirstName: (customerFirstName) => set({ customerFirstName }),
  setCustomerLastName: (customerLastName) => set({ customerLastName }),
  setCustomerPhone: (customerPhone) => set({ customerPhone }),
  setCustomerEmail: (customerEmail) => set({ customerEmail }),
  clearSelectedTimeAndMaster: () => set({ time: null, master: null, step: 2 }),
}))
