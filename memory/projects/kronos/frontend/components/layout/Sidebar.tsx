'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import { 
  LayoutDashboard, 
  UserPlus, 
  Users, 
  MessageSquare, 
  FileText, 
  BarChart3,
  Settings,
  Bell,
  Search,
  HelpCircle
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: UserPlus },
  { name: 'Clients', href: '/clients', icon: Users },
  { name: 'Messages', href: '/messages', icon: MessageSquare },
  { name: 'Tax Organizers', href: '/organizers', icon: FileText },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
]

const secondaryNavigation = [
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Help & Support', href: '/help', icon: HelpCircle },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen bg-white border-r border-gray-200 w-64 flex-col fixed left-0 top-0">
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center">
            <span className="text-white font-bold text-sm">K</span>
          </div>
          <span className="text-lg font-semibold text-gray-900">Kronos</span>
        </div>
      </div>

      {/* Search */}
      <div className="px-4 py-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Primary Navigation */}
      <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <item.icon className={clsx(
                'w-5 h-5 flex-shrink-0',
                isActive ? 'text-primary-600' : 'text-gray-400'
              )} />
              {item.name}
              {item.name === 'Messages' && (
                <span className="ml-auto bg-danger-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-semibold">
                  3
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Secondary Navigation */}
      <div className="px-4 py-4 border-t border-gray-200 space-y-1">
        {secondaryNavigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <item.icon className={clsx(
                'w-5 h-5 flex-shrink-0',
                isActive ? 'text-primary-600' : 'text-gray-400'
              )} />
              {item.name}
            </Link>
          )
        })}
      </div>

      {/* User Profile */}
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold">
            LP
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              Laura Peterson
            </p>
            <p className="text-xs text-gray-500 truncate">
              CPA, Tax Practice
            </p>
          </div>
          <Bell className="w-4 h-4 text-gray-400" />
        </div>
      </div>
    </div>
  )
}
