'use client'

import { Bell, Search, HelpCircle, Settings, User, ChevronDown, Moon, Sun } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { clsx } from 'clsx'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')
  const [darkMode, setDarkMode] = useState(false)
  const [notifications, setNotifications] = useState(3)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  // Initialize dark mode from localStorage
  useEffect(() => {
    const isDark = localStorage.getItem('darkMode') === 'true'
    setDarkMode(isDark)
    if (isDark) {
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode
    setDarkMode(newDarkMode)
    localStorage.setItem('darkMode', newDarkMode.toString())
    
    if (newDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const quickStats = [
    { label: 'Active Clients', value: '42', change: '+12%', trend: 'up' },
    { label: 'Pending Leads', value: '18', change: '+8%', trend: 'up' },
    { label: "Today's Revenue", value: '$2,850', change: '+15%', trend: 'up' },
  ]

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md supports-[backdrop-filter]:bg-white/60">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Left side - Search */}
          <div className="flex-1 max-w-2xl">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search clients, leads, messages..."
                className="w-full pl-10 pr-4 py-2.5 input text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-2 ml-6">
            {/* Quick Stats (Desktop only) */}
            <div className="hidden lg:flex items-center gap-6 mr-4">
              {quickStats.map((stat, index) => (
                <div key={index} className="text-right">
                  <p className="text-xs font-medium text-gray-500">
                    {stat.label}
                  </p>
                  <div className="flex items-center gap-1.5">
                    <p className="font-semibold text-gray-900">
                      {stat.value}
                    </p>
                    <span className={clsx(
                      'text-xs font-medium px-1.5 py-0.5 rounded-full',
                      stat.trend === 'up' 
                        ? 'bg-success-100 text-success-700'
                        : 'bg-danger-100 text-danger-700'
                    )}>
                      {stat.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Dark Mode Toggle */}
            <Button
              variant="ghost"
              size="sm"
              className="p-2"
              onClick={toggleDarkMode}
              aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? (
                <Sun className="w-4 h-4 text-gray-600" />
              ) : (
                <Moon className="w-4 h-4 text-gray-600" />
              )}
            </Button>

            {/* Notifications */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="p-2 relative"
                aria-label={`Notifications (${notifications} unread)`}
              >
                <Bell className="w-4 h-4 text-gray-600" />
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center border-2 border-white">
                    {notifications}
                  </span>
                )}
              </Button>
            </div>

            {/* Help */}
            <Button
              variant="ghost"
              size="sm"
              className="p-2"
              aria-label="Help"
            >
              <HelpCircle className="w-4 h-4 text-gray-600" />
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="sm"
              className="p-2"
              aria-label="Settings"
            >
              <Settings className="w-4 h-4 text-gray-600" />
            </Button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="User menu"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                  <span className="font-semibold text-white text-sm">L</span>
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-900">Laura</p>
                  <p className="text-xs text-gray-500">Tax Practitioner</p>
                </div>
                <ChevronDown className={clsx(
                  'w-4 h-4 text-gray-500 transition-transform',
                  userMenuOpen && 'transform rotate-180'
                )} />
              </button>

              {/* User Dropdown Menu */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-56 dropdown">
                  <div className="px-4 py-3 border-b border-gray-200">
                    <p className="text-sm font-medium text-gray-900">Laura</p>
                    <p className="text-xs text-gray-500 mt-0.5">laura@taxpractice.com</p>
                  </div>
                  
                  <div className="py-1">
                    <a href="/profile" className="dropdown-item">
                      <User className="w-4 h-4 mr-3" />
                      Your Profile
                    </a>
                    <a href="/settings" className="dropdown-item">
                      <Settings className="w-4 h-4 mr-3" />
                      Settings
                    </a>
                    <button 
                      onClick={toggleDarkMode}
                      className="dropdown-item w-full text-left"
                    >
                      {darkMode ? (
                        <>
                          <Sun className="w-4 h-4 mr-3" />
                          Light Mode
                        </>
                      ) : (
                        <>
                          <Moon className="w-4 h-4 mr-3" />
                          Dark Mode
                        </>
                      )}
                    </button>
                  </div>
                  
                  <div className="py-1 border-t border-gray-200">
                    <a href="/logout" className="dropdown-item text-danger-600">
                      Sign out
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Quick Stats */}
        <div className="lg:hidden mt-3">
          <div className="flex items-center justify-between">
            {quickStats.map((stat, index) => (
              <div key={index} className="text-center">
                <p className="text-xs font-medium text-gray-500">
                  {stat.label}
                </p>
                <div className="flex items-center justify-center gap-1">
                  <p className="font-semibold text-gray-900">
                    {stat.value}
                  </p>
                  <span className={clsx(
                    'text-xs font-medium',
                    stat.trend === 'up' 
                      ? 'text-success-600'
                      : 'text-danger-600'
                  )}>
                    {stat.change}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Notification Panel (would be implemented as a separate component) */}
      {false && (
        <div className="absolute right-4 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 z-50">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
              <button className="text-sm text-primary-600 hover:text-primary-700">
                Mark all as read
              </button>
            </div>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {/* Notification items would go here */}
          </div>
          <div className="p-4 border-t border-gray-200 text-center">
            <a href="/notifications" className="text-sm text-primary-600 hover:text-primary-700">
              View all notifications
            </a>
          </div>
        </div>
      )}
    </header>
  )
}