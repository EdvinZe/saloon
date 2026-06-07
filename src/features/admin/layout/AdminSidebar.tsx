import { NavLink } from 'react-router-dom'

export default function AdminSidebar() {
  return (
    <aside className="border-r border-[#2a2218] bg-[#0a0a08] p-4 lg:min-h-[calc(100vh-80px)] lg:w-64">
      <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Manager</p>
      <nav className="mt-6 grid gap-2">
        <NavLink
          to="/admin/services"
          className={({ isActive }) =>
            `border px-3 py-2 text-sm ${
              isActive
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] text-[#7a7060] hover:text-[#e8e0d0]'
            }`
          }
        >
          Services
        </NavLink>
        <NavLink
          to="/admin/masters"
          className={({ isActive }) =>
            `border px-3 py-2 text-sm ${
              isActive
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] text-[#7a7060] hover:text-[#e8e0d0]'
            }`
          }
        >
          Masters
        </NavLink>
        <NavLink
          to="/admin/bookings"
          className={({ isActive }) =>
            `border px-3 py-2 text-sm ${
              isActive
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] text-[#7a7060] hover:text-[#e8e0d0]'
            }`
          }
        >
          Bookings
        </NavLink>
        <NavLink
          to="/admin/schedule"
          className={({ isActive }) =>
            `border px-3 py-2 text-sm ${
              isActive
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] text-[#7a7060] hover:text-[#e8e0d0]'
            }`
          }
        >
          Schedule
        </NavLink>
        <NavLink
          to="/admin/reports"
          className={({ isActive }) =>
            `border px-3 py-2 text-sm ${
              isActive
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] text-[#7a7060] hover:text-[#e8e0d0]'
            }`
          }
        >
          Reports
        </NavLink>
        <NavLink
          to="/admin/telegram-accounts"
          className={({ isActive }) =>
            `border px-3 py-2 text-sm ${
              isActive
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] text-[#7a7060] hover:text-[#e8e0d0]'
            }`
          }
        >
          Telegram Accounts
        </NavLink>
      </nav>
    </aside>
  )
}
