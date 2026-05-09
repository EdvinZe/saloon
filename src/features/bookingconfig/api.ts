export interface BookingConfig {
  depositAmount: number
  currency: 'EUR'
  isDepositRequired: boolean
}

const MOCK_BOOKING_CONFIG: BookingConfig = {
  depositAmount: 10,
  currency: 'EUR',
  isDepositRequired: true,
}

export async function getBookingConfig(): Promise<BookingConfig> {
  // Later this will be replaced with FastAPI:
  // return api.get('/api/v1/booking/config').then(r => r.data)
  return Promise.resolve(MOCK_BOOKING_CONFIG)
}
