import type { ReactNode } from 'react'
import AdminHeader from './AdminHeader'
import AdminSidebar from './AdminSidebar'

type AdminLayoutProps = {
  children: ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <div className="min-h-screen bg-[#0f0f0f]">
      <AdminHeader />
      <div className="lg:flex">
        <AdminSidebar />
        <main className="min-w-0 flex-1 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  )
}
