export type BookingSuccessData = {
  service: string
  duration: string
  date: string
  time: string
  barber: string
  deposit: string
}

// before change
export async function getBookingSuccess(bookingId: string): Promise<BookingSuccessData> {
  void bookingId

  return Promise.resolve({
    service: 'Haircut',
    duration: '45 min',
    date: 'Tuesday, Apr 28',
    time: '09:30',
    barber: 'Alex Kravtsov',
    deposit: '€8',
  })
}