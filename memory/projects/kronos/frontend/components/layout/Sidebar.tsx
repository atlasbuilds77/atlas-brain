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
  HelpCircle,
  Zap,
  ArrowRight
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, badge: null },
  { name: 'Leads', href: '/leads', icon: UserPlus, badge: '8' },
  { name: 'Clients', href: '/clients', icon: Users, badge: null },
  { name: 'Messages', href: '/messages', icon: MessageSquare, badge: '3' },
  { name: 'Tax Organizers', href: '/organizers', icon: FileText, badge: null },
  { name: 'Analytics', href: '/analytics', icon: BarChart3, badge: null },
]

const secondaryNavigation = [
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Help & Support', href: '/help', icon: HelpCircle },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen bg-zinc-950 border-r border-zinc-800 w-64 flex-col fixed left-0 top-0">
      {/* Logo - BOLD */}
      <div className="flex items-center justify-between h-20 px-6 border-b border-zinc-800/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-600 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-900/50">
            <span className="text-white font-black text-xl">K</span>
          </div>
          <span className="text-2xl font-black text-white tracking-tight">Kronos</span>
        </div>
      </div>

      {/* Search - PREMIUM */}
      <div className="px-4 py-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full pl-11 pr-4 py-3 text-sm bg-zinc-900 border border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500 transition-all placeholder:text-zinc-600 text-white"
          />
        </div>
      </div>

      {/* Primary Navigation - BASKETBALL STYLE */}
      <nav className="flex-1 px-4 space-y-2 overflow-y-auto scrollbar-hide">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'group flex items-center gap-3 px-4 py-3.5 text-sm font-semibold rounded-xl transition-all relative overflow-hidden',
                isActive
                  ? 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-lg shadow-orange-900/50'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
              )}
            >
              <item.icon className={clsx(
                'w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110',
                isActive ? 'text-white' : 'text-zinc-500 group-hover:text-orange-500'
              )} />
              <span className="flex-1">{item.name}</span>
              {item.badge && (
                <span className={clsx(
                  'px-2 py-0.5 rounded-lg text-xs font-bold',
                  isActive 
                    ? 'bg-white/20 text-white'
                    : 'bg-orange-500/10 text-orange-500'
                )}>
                  {item.badge}
                </span>
              )}
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 animate-pulse"></div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* CTA Banner - PREMIUM UPGRADE */}
      <div className="mx-4 mb-6 p-5 rounded-2xl bg-gradient-to-br from-orange-900/30 via-orange-800/20 to-zinc-900 border border-orange-500/20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-5 h-5 text-orange-500" />
            <span className="text-xs font-bold text-orange-500 uppercase tracking-wider">Pro</span>
          </div>
          <h4 className="text-sm font-bold text-white mb-2">Unlock Premium Features</h4>
          <p className="text-xs text-zinc-400 mb-4">Advanced analytics, automation & more</p>
          <button className="w-full px-4 py-2.5 bg-orange-600 hover:bg-orange-500 text-white text-sm font-bold rounded-xl transition-all hover:scale-105 active:scale-95 flex items-center justify-center gap-2 shadow-lg shadow-orange-900/50">
            Upgrade Now
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Secondary Navigation */}
      <div className="px-4 py-4 border-t border-zinc-800/50 space-y-2">
        {secondaryNavigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all',
                isActive
                  ? 'bg-zinc-900 text-white'
                  : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50'
              )}
            >
              <item.icon className={clsx(
                'w-5 h-5 flex-shrink-0',
                isActive ? 'text-orange-500' : 'text-zinc-600'
              )} />
              {item.name}
            </Link>
          )
        })}
      </div>

      {/* User Profile - PREMIUM */}
      <div className="px-4 py-4 border-t border-zinc-800/50">
        <div className="group flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-zinc-900 cursor-pointer transition-all">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white font-bold shadow-lg">
              LP
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-500 border-2 border-zinc-950 rounded-full"></div>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-white truncate">
              Laura Peterson
            </p>
            <p className="text-xs text-zinc-500 truncate">
              CPA, Tax Practice
            </p>
          </div>
          <div className="relative">
            <Bell className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-orange-500 rounded-full animate-pulse"></span>
          </div>
        </div>
      </div>
    </div>
  )
}
