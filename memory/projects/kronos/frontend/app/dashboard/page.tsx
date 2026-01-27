'use client'

import { Card, CardHeader, StatsCard, EmptyStateCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  Users, 
  UserPlus, 
  DollarSign, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  MessageSquare,
  FileText,
  ArrowRight,
  Calendar,
  Send,
  Plus,
  ChevronRight,
  Activity,
  Shield,
  Zap,
  Target
} from 'lucide-react'
import { formatCurrency, formatDate } from '@/lib/utils'

// Mock data - PREMIUM METRICS
const stats = [
  {
    title: 'Active Clients',
    value: '42',
    change: 12,
    changeLabel: 'vs last month',
    icon: <Users className="w-8 h-8" />,
    iconBg: 'bg-orange-500/10',
    iconColor: 'text-orange-500',
    trend: 'up' as const,
  },
  {
    title: 'Monthly Revenue',
    value: formatCurrency(28500),
    change: 15,
    changeLabel: 'vs last month',
    icon: <DollarSign className="w-8 h-8" />,
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-400',
    trend: 'up' as const,
  },
  {
    title: 'Retention Rate',
    value: '94%',
    change: 2,
    changeLabel: 'industry: 78%',
    icon: <TrendingUp className="w-8 h-8" />,
    iconBg: 'bg-blue-500/10',
    iconColor: 'text-blue-400',
    trend: 'up' as const,
  },
  {
    title: 'New Leads',
    value: '18',
    change: 8,
    changeLabel: 'this week',
    icon: <UserPlus className="w-8 h-8" />,
    iconBg: 'bg-purple-500/10',
    iconColor: 'text-purple-400',
    trend: 'up' as const,
  }
]

const urgentTasks = [
  { id: 1, client: 'John Smith', action: 'Follow up on missing W-2', priority: 'high', dueDate: '2024-01-28', icon: AlertCircle },
  { id: 2, client: 'ABC Corp', action: 'Review Q4 tax documents', priority: 'high', dueDate: '2024-01-28', icon: FileText },
  { id: 3, client: 'Sarah Johnson', action: 'Send tax organizer reminder', priority: 'medium', dueDate: '2024-01-29', icon: Send },
]

const recentMessages = [
  { id: 1, from: 'Michael Chen', subject: 'Tax planning consultation needed', date: '2024-01-26', unread: true, urgent: true },
  { id: 2, from: 'Sarah Johnson', subject: 'Documents uploaded ✓', date: '2024-01-25', unread: false, urgent: false },
  { id: 3, from: 'ABC Corporation', subject: 'Quarterly filing question', date: '2024-01-24', unread: true, urgent: false },
]

const quickActions = [
  { title: 'Add New Lead', icon: UserPlus, href: '/leads/new', gradient: 'from-orange-600 to-orange-500' },
  { title: 'Send Organizer', icon: FileText, href: '/organizers/send', gradient: 'from-zinc-800 to-zinc-700' },
  { title: 'Schedule Call', icon: Calendar, href: '/calendar/new', gradient: 'from-zinc-800 to-zinc-700' },
  { title: 'View Analytics', icon: TrendingUp, href: '/analytics', gradient: 'from-zinc-800 to-zinc-700' },
]

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-black">
      {/* HERO SECTION - MASSIVE HEADLINE */}
      <div className="relative overflow-hidden bg-gradient-to-b from-zinc-900 to-black border-b border-zinc-800/50">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-orange-900/10 via-black to-black"></div>
        
        <div className="relative max-w-[1600px] mx-auto px-8 py-20">
          {/* Status Bar */}
          <div className="flex items-center gap-6 mb-8">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-zinc-400">All systems operational</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">Updated just now</span>
            </div>
          </div>

          {/* BOLD HEADLINE */}
          <div className="space-y-6">
            <h1 className="text-7xl md:text-8xl font-black tracking-tight text-white leading-[0.9]">
              Welcome back,<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-zinc-400">Laura</span>
            </h1>
            <p className="text-2xl text-zinc-400 font-light max-w-2xl">
              Your tax practice command center. Everything you need, nothing you don't.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex items-center gap-4 mt-12">
            <button className="group px-8 py-4 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white font-bold rounded-2xl shadow-2xl shadow-orange-900/50 hover:shadow-orange-900/70 transition-all duration-300 hover:scale-105 active:scale-95 text-lg flex items-center gap-3">
              <Plus className="w-6 h-6" />
              Add Client
            </button>
            <button className="group px-8 py-4 bg-zinc-800/50 hover:bg-zinc-800 text-white font-semibold rounded-2xl border border-zinc-700 hover:border-zinc-600 transition-all duration-300 text-lg flex items-center gap-3 backdrop-blur-sm">
              <Calendar className="w-5 h-5 text-zinc-400 group-hover:text-white" />
              View Calendar
            </button>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="max-w-[1600px] mx-auto px-8 py-16 space-y-20">
        
        {/* MASSIVE STATS - ABOVE THE FOLD */}
        <div className="space-y-8">
          <div className="flex items-end justify-between">
            <div>
              <h2 className="text-5xl font-bold text-white mb-2">Performance</h2>
              <p className="text-xl text-zinc-500">Real-time business metrics</p>
            </div>
            <button className="text-zinc-400 hover:text-orange-500 transition-colors flex items-center gap-2 text-sm font-medium">
              View detailed analytics
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* STATS GRID - HUGE NUMBERS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div 
                key={index}
                className="group relative bg-gradient-to-b from-zinc-900/80 to-zinc-900/40 backdrop-blur-sm rounded-3xl p-8 border border-zinc-800 hover:border-zinc-700 transition-all duration-500 hover:shadow-2xl hover:shadow-orange-900/10"
              >
                {/* Icon */}
                <div className={`inline-flex p-4 rounded-2xl ${stat.iconBg} ${stat.iconColor} mb-6`}>
                  {stat.icon}
                </div>

                {/* Title */}
                <div className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-4">
                  {stat.title}
                </div>

                {/* HUGE Value */}
                <div className="text-6xl font-black text-white mb-4 tracking-tight">
                  {stat.value}
                </div>

                {/* Change Indicator */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-emerald-400">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm font-bold">+{stat.change}%</span>
                  </div>
                  <span className="text-sm text-zinc-600">{stat.changeLabel}</span>
                </div>

                {/* Hover Effect Border */}
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-orange-500/0 via-orange-500/0 to-orange-500/0 group-hover:from-orange-500/10 group-hover:via-orange-500/5 group-hover:to-orange-500/10 transition-all duration-500 pointer-events-none"></div>
              </div>
            ))}
          </div>
        </div>

        {/* QUICK ACTIONS - GENEROUS SPACING */}
        <div className="space-y-8">
          <h3 className="text-4xl font-bold text-white">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickActions.map((action, index) => (
              <button
                key={index}
                className={`group relative p-8 bg-gradient-to-br ${action.gradient} rounded-2xl transition-all duration-300 hover:scale-105 active:scale-95 overflow-hidden shadow-2xl`}
              >
                <div className="relative z-10 flex flex-col items-start gap-4">
                  <div className="p-3 bg-white/10 rounded-xl group-hover:bg-white/20 transition-colors">
                    <action.icon className="w-7 h-7 text-white" />
                  </div>
                  <span className="text-xl font-bold text-white text-left">
                    {action.title}
                  </span>
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </button>
            ))}
          </div>
        </div>

        {/* PRIORITY TASKS */}
        <div className="space-y-8">
          <div className="flex items-end justify-between">
            <div>
              <h3 className="text-4xl font-bold text-white mb-2">Priority Tasks</h3>
              <p className="text-lg text-zinc-500">{urgentTasks.length} items need attention</p>
            </div>
            <button className="text-orange-500 hover:text-orange-400 transition-colors flex items-center gap-2 font-semibold">
              View all
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-4">
            {urgentTasks.map((task) => (
              <div 
                key={task.id} 
                className="group flex items-center justify-between p-6 bg-zinc-900/50 hover:bg-zinc-900 rounded-2xl transition-all cursor-pointer border border-zinc-800 hover:border-zinc-700"
              >
                <div className="flex items-center gap-6 flex-1">
                  <div className={`flex-shrink-0 w-14 h-14 rounded-xl ${
                    task.priority === 'high' 
                      ? 'bg-orange-500/10 text-orange-500' 
                      : 'bg-yellow-500/10 text-yellow-500'
                  } flex items-center justify-center`}>
                    <task.icon className="w-7 h-7" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xl font-bold text-white mb-1">
                      {task.client}
                    </p>
                    <p className="text-base text-zinc-400">
                      {task.action}
                    </p>
                    <div className="flex items-center gap-3 mt-3">
                      <div className="flex items-center gap-2 text-sm text-zinc-600">
                        <Clock className="w-4 h-4" />
                        <span>Due {formatDate(task.dueDate)}</span>
                      </div>
                      <div className={`px-3 py-1 rounded-lg text-xs font-bold uppercase ${
                        task.priority === 'high' 
                          ? 'bg-orange-500/10 text-orange-500' 
                          : 'bg-yellow-500/10 text-yellow-500'
                      }`}>
                        {task.priority}
                      </div>
                    </div>
                  </div>
                </div>
                <button className="px-6 py-3 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-xl opacity-0 group-hover:opacity-100 transition-all hover:scale-105 active:scale-95">
                  Complete
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* RECENT MESSAGES */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <div className="flex items-end justify-between">
              <div>
                <h3 className="text-4xl font-bold text-white mb-2">Messages</h3>
                <p className="text-lg text-zinc-500">2 unread conversations</p>
              </div>
              <button className="text-orange-500 hover:text-orange-400 transition-colors flex items-center gap-2 font-semibold">
                View all
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {recentMessages.map((message) => (
                <div 
                  key={message.id} 
                  className="group flex items-start gap-5 p-6 hover:bg-zinc-900/50 rounded-2xl transition-all cursor-pointer border border-transparent hover:border-zinc-800"
                >
                  <div className={`flex-shrink-0 w-14 h-14 rounded-full ${
                    message.unread 
                      ? 'bg-gradient-to-br from-orange-600 to-orange-500 text-white' 
                      : 'bg-zinc-800 text-zinc-400'
                  } flex items-center justify-center font-bold text-lg shadow-xl`}>
                    {message.from.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <p className="text-lg font-bold text-white">
                        {message.from}
                      </p>
                      {message.unread && (
                        <span className="w-2.5 h-2.5 bg-orange-500 rounded-full animate-pulse"></span>
                      )}
                      {message.urgent && (
                        <span className="px-2 py-0.5 bg-orange-500/20 text-orange-500 text-xs font-bold rounded uppercase">
                          Urgent
                        </span>
                      )}
                    </div>
                    <p className="text-base text-zinc-300 mb-2">
                      {message.subject}
                    </p>
                    <p className="text-sm text-zinc-600">
                      {formatDate(message.date)}
                    </p>
                  </div>
                  <button className="px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold rounded-xl opacity-0 group-hover:opacity-100 transition-all text-sm">
                    Reply
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* PERFORMANCE SUMMARY - DARK CARD */}
          <div className="space-y-8">
            <div className="bg-gradient-to-br from-zinc-900 via-zinc-900 to-black rounded-3xl p-8 border border-zinc-800 shadow-2xl">
              <div className="flex items-center gap-3 mb-8">
                <div className="p-3 bg-orange-500/10 rounded-xl">
                  <Zap className="w-6 h-6 text-orange-500" />
                </div>
                <div>
                  <h4 className="text-2xl font-bold text-white">This Month</h4>
                  <p className="text-sm text-zinc-500">Performance snapshot</p>
                </div>
              </div>

              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-zinc-400">Lead Conversion</span>
                    <span className="text-2xl font-black text-emerald-400">68%</span>
                  </div>
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full w-[68%] bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full"></div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-zinc-400">Client Satisfaction</span>
                    <span className="text-2xl font-black text-blue-400">4.8/5</span>
                  </div>
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full w-[96%] bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"></div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-zinc-400">On-time Filing</span>
                    <span className="text-2xl font-black text-purple-400">96%</span>
                  </div>
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full w-[96%] bg-gradient-to-r from-purple-600 to-purple-400 rounded-full"></div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-zinc-400">Revenue Growth</span>
                    <span className="text-2xl font-black text-orange-400">+15%</span>
                  </div>
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full w-[75%] bg-gradient-to-r from-orange-600 to-orange-400 rounded-full"></div>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-zinc-800">
                <button className="w-full px-6 py-4 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white font-bold rounded-xl transition-all hover:scale-105 active:scale-95 shadow-lg shadow-orange-900/50 flex items-center justify-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Detailed Analytics
                </button>
              </div>
            </div>

            {/* TODAY'S SCHEDULE */}
            <div className="bg-zinc-900/50 backdrop-blur-sm rounded-3xl p-8 border border-zinc-800">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <Calendar className="w-5 h-5 text-blue-500" />
                </div>
                <h4 className="text-xl font-bold text-white">Today's Schedule</h4>
              </div>

              <div className="space-y-4">
                <div className="p-5 bg-gradient-to-r from-orange-500/10 to-orange-500/5 rounded-xl border border-orange-500/20">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-bold text-white mb-1">Michael Chen</p>
                      <p className="text-sm text-zinc-400">Tax Planning Call</p>
                    </div>
                    <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-lg uppercase">
                      In 30 min
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-zinc-500 mb-4">
                    <Clock className="w-4 h-4" />
                    <span>2:00 PM - 3:00 PM</span>
                  </div>
                  <button className="w-full px-4 py-2.5 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-lg transition-all text-sm">
                    Join Meeting
                  </button>
                </div>

                <div className="p-5 hover:bg-zinc-800/30 rounded-xl transition-colors border border-zinc-800">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-bold text-white mb-1">Sarah Johnson</p>
                      <p className="text-sm text-zinc-400">Document Review</p>
                    </div>
                    <span className="px-3 py-1 bg-zinc-700 text-zinc-300 text-xs font-semibold rounded-lg">
                      4:30 PM
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-zinc-500">
                    <Clock className="w-4 h-4" />
                    <span>4:30 PM - 5:30 PM</span>
                  </div>
                </div>
              </div>

              <button className="w-full mt-6 text-center text-sm font-semibold text-orange-500 hover:text-orange-400 transition-colors">
                View Full Calendar →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
