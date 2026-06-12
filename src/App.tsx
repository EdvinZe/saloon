import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Navbar from './components/layout/Navbar'
import HomePage from './pages/HomePage'
import BookingPage from './pages/BookingPage'
import BookingSuccessPage from './pages/BookingSuccessPage'
import BookingErrorPage from './pages/BookingErrorPage'
import BookingManagePage from './pages/BookingManagePage'
import WorksPage from './pages/WorksPage'
import AboutPage from './pages/AboutPage'
import AdminSchedulePage from './pages/admin/AdminSchedulePage'
import AdminServicesPage from './pages/admin/AdminServicesPage'
import AdminMastersPage from './pages/admin/AdminMastersPage'
import AdminBookingsPage from './pages/admin/AdminBookingsPage'
import AdminReportsPage from './pages/admin/AdminReportsPage'
import AdminTelegramAccountsPage from './pages/admin/AdminTelegramAccountsPage'
import AdminLoginPage from './pages/admin/AdminLoginPage'
import ProtectedAdminRoute from './features/admin/auth/components/ProtectedAdminRoute'

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
            <Route path="/booking/manage" element={<BookingManagePage />} />
            <Route path="/works" element={<WorksPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route
              path="/admin"
              element={(
                <ProtectedAdminRoute>
                  <Navigate replace to="/admin/services" />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="/admin/services"
              element={(
                <ProtectedAdminRoute>
                  <AdminServicesPage />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="/admin/masters"
              element={(
                <ProtectedAdminRoute>
                  <AdminMastersPage />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="/admin/bookings"
              element={(
                <ProtectedAdminRoute>
                  <AdminBookingsPage />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="/admin/schedule"
              element={(
                <ProtectedAdminRoute>
                  <AdminSchedulePage />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="/admin/reports"
              element={(
                <ProtectedAdminRoute>
                  <AdminReportsPage />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="/admin/telegram-accounts"
              element={(
                <ProtectedAdminRoute>
                  <AdminTelegramAccountsPage />
                </ProtectedAdminRoute>
              )}
            />
            <Route
              path="*"
              element={<BookingErrorPage forcedType="page" forcedReason="not_found" />}
            />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
