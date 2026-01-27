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
  Shield
} from 'lucide-react'
import { formatCurrency, formatDate } from '@/lib/utils'

// Mock data - ENHANCED FOR CONVERSION
const stats = [
  {
    title: 'Active Clients',
    value: '42',
    change: 12,
    changeLabel: 'vs last month',
    icon: <Users className="w-6 h-6" />,
    iconBg: 'bg-primary-100',
    trend: 'up' as const,
  },
  {
    title: 'New Leads',
    value: '18',
    change: 8,
    changeLabel: 'this week',
    icon: <UserPlus className="w-6 h-6" />,
    iconBg: 'bg-success-100',
    trend: 'up' as const,
  },
  {
    title: 'Monthly Revenue',
    value: formatCurrency(28500),
    change: 15,
    changeLabel: 'vs last month',
    icon: <DollarSign className="w-6 h-6" />,
    iconBg: 'bg-warning-100',
    trend: 'up' as const,
  },
  {
    title: 'Retention Rate',
    value: '94%',
    change: 2,
    changeLabel: 'vs last quarter',
    icon: <TrendingUp className="w-6 h-6" />,
    iconBg: 'bg-success-100',
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
  { title: 'Add New Lead', icon: UserPlus, href: '/leads/new', color: 'bg-primary-600 hover:bg-primary-700' },
  { title: 'Send Tax Organizer', icon: FileText, href: '/organizers/send', color: 'bg-success-600 hover:bg-success-700' },
  { title: 'Schedule Consultation', icon: Calendar, href: '/calendar/new', color: 'bg-purple-600 hover:bg-purple-700' },
  { title: 'View Analytics', icon: TrendingUp, href: '/analytics', color: 'bg-indigo-600 hover:bg-indigo-700' },
]

export default function DashboardPage() {
  return (
    <div className="space-y-8 max-w-[1600px]">
      {/* Header with context */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Welcome back, Laura</h1>
          <p className="mt-2 text-lg text-slate-600">
            Here's what needs your attention today
          </p>
          <div className="mt-3 flex items-center gap-4 text-sm text-slate-500">
            <div className="flex items-center gap-1.5">
              <Activity className="w-4 h-4" />
              <span>Last updated: Just now</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-success-600" />
              <span>All systems operational</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="lg">
            <Calendar className="w-4 h-4" />
            View Calendar
          </Button>
          <Button size="lg">
            <Plus className="w-4 h-4" />
            Add Client
          </Button>
        </div>
      </div>

      {/* KPI Stats Grid - ABOVE THE FOLD */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Urgent Actions Alert */}
      <Card className="border-l-4 border-l-danger-500 bg-danger-50/30">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-danger-100 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-danger-600" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900">
              3 urgent tasks need your attention today
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Address these items to stay on track with client deadlines
            </p>
          </div>
          <Button variant="danger">
            View All Tasks
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </Card>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Priority Tasks */}
        <div className="lg:col-span-2 space-y-6">
          {/* Urgent Tasks */}
          <Card>
            <CardHeader 
              title="Priority Tasks" 
              subtitle="Complete these to stay on schedule"
              badge={
                <Badge variant="danger" className="text-xs">
                  {urgentTasks.length} urgent
                </Badge>
              }
              action={
                <Button variant="ghost" size="sm">
                  View All
                  <ChevronRight className="w-4 h-4" />
                </Button>
              }
            />
            <div className="mt-6 space-y-3">
              {urgentTasks.map((task) => (
                <div 
                  key={task.id} 
                  className="group flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 rounded-xl transition-all cursor-pointer border border-transparent hover:border-slate-200"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${
                      task.priority === 'high' 
                        ? 'bg-danger-100 text-danger-600' 
                        : 'bg-warning-100 text-warning-600'
                    } flex items-center justify-center`}>
                      <task.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-slate-900">
                        {task.client}
                      </p>
                      <p className="text-sm text-slate-600 mt-0.5">
                        {task.action}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span className="text-xs text-slate-500">
                          Due {formatDate(task.dueDate)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={task.priority === 'high' ? 'danger' : 'warning'}
                      className="capitalize"
                    >
                      {task.priority}
                    </Badge>
                    <Button 
                      variant="primary" 
                      size="sm"
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      Complete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-slate-200">
              <button className="w-full text-center text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors">
                + Add New Task
              </button>
            </div>
          </Card>

          {/* Recent Messages */}
          <Card>
            <CardHeader 
              title="Recent Messages" 
              subtitle="Stay on top of client communications"
              badge={
                <Badge variant="primary" className="text-xs">
                  2 unread
                </Badge>
              }
              action={
                <Button variant="ghost" size="sm">
                  View All
                  <ChevronRight className="w-4 h-4" />
                </Button>
              }
            />
            <div className="mt-6 space-y-3">
              {recentMessages.map((message) => (
                <div 
                  key={message.id} 
                  className="group flex items-start gap-4 p-4 hover:bg-slate-50 rounded-xl transition-all cursor-pointer"
                >
                  <div className="flex-shrink-0">
                    <div className={`w-10 h-10 rounded-full ${
                      message.unread 
                        ? 'bg-primary-100 text-primary-700' 
                        : 'bg-slate-100 text-slate-600'
                    } flex items-center justify-center font-semibold text-sm`}>
                      {message.from.split(' ').map(n => n[0]).join('')}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className={`font-semibold ${
                        message.unread ? 'text-slate-900' : 'text-slate-600'
                      }`}>
                        {message.from}
                      </p>
                      {message.unread && (
                        <span className="w-2 h-2 bg-primary-600 rounded-full"></span>
                      )}
                      {message.urgent && (
                        <Badge variant="danger" className="text-xs">Urgent</Badge>
                      )}
                    </div>
                    <p className="text-sm text-slate-600">
                      {message.subject}
                    </p>
                    <p className="text-xs text-slate-400 mt-1.5">
                      {formatDate(message.date)}
                    </p>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Reply
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column - Quick Actions & Insights */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader 
              title="Quick Actions" 
              subtitle="Common tasks"
            />
            <div className="mt-6 grid grid-cols-2 gap-3">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className={`${action.color} text-white p-4 rounded-xl transition-all hover:scale-105 hover:shadow-lg active:scale-95 flex flex-col items-center gap-3 group`}
                >
                  <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center group-hover:bg-white/30 transition-colors">
                    <action.icon className="w-6 h-6" />
                  </div>
                  <span className="text-sm font-semibold text-center">
                    {action.title}
                  </span>
                </button>
              ))}
            </div>
          </Card>

          {/* Today's Appointments */}
          <Card>
            <CardHeader 
              title="Today's Schedule" 
              subtitle="Upcoming appointments"
              action={
                <Button variant="ghost" size="sm">
                  <Calendar className="w-4 h-4" />
                </Button>
              }
            />
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-gradient-to-r from-primary-50 to-primary-100/50 rounded-xl border border-primary-200">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-slate-900">Michael Chen</p>
                    <p className="text-sm text-slate-600 mt-0.5">
                      Tax Planning Consultation
                    </p>
                  </div>
                  <Badge variant="success" className="text-xs">
                    In 30 min
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-600">
                  <Clock className="w-4 h-4" />
                  <span>2:00 PM - 3:00 PM</span>
                </div>
                <div className="mt-3 pt-3 border-t border-primary-200">
                  <Button variant="primary" size="sm" fullWidth>
                    Join Meeting
                  </Button>
                </div>
              </div>
              
              <div className="p-4 hover:bg-slate-50 rounded-xl transition-colors border border-slate-200">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-slate-900">Sarah Johnson</p>
                    <p className="text-sm text-slate-600 mt-0.5">
                      Document Review
                    </p>
                  </div>
                  <Badge variant="default" className="text-xs">
                    4:30 PM
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-600">
                  <Clock className="w-4 h-4" />
                  <span>4:30 PM - 5:30 PM</span>
                </div>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-slate-200">
              <button className="w-full text-center text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors">
                View Full Calendar →
              </button>
            </div>
          </Card>

          {/* Performance Summary */}
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white">
            <CardHeader 
              title="This Month's Performance" 
              subtitle="Key metrics snapshot"
              className="text-white"
            />
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <span className="text-sm text-slate-300">Lead Conversion</span>
                <span className="text-lg font-bold text-success-400">68%</span>
              </div>
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <span className="text-sm text-slate-300">Client Satisfaction</span>
                <span className="text-lg font-bold text-success-400">4.8/5</span>
              </div>
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <span className="text-sm text-slate-300">On-time Filing</span>
                <span className="text-lg font-bold text-success-400">96%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-300">Revenue Growth</span>
                <span className="text-lg font-bold text-success-400">+15%</span>
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-white/10">
              <Button variant="secondary" fullWidth>
                View Detailed Analytics
                <TrendingUp className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
