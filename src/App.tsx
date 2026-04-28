import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Navbar from './components/layout/Navbar'
import HomePage from './pages/HomePage'
import BookingPage from './pages/BookingPage'
import BookingSuccessPage from './pages/BookingSuccessPage'
import BookingErrorPage from './pages/BookingErrorPage'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/booking" element={<BookingPage />} />
            <Route path="/booking/success" element={<BookingSuccessPage />} />
            <Route path="/booking/error" element={<BookingErrorPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
