'use client'

import { useState } from 'react'
import { Card, CardHeader, EmptyStateCard, StatsCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  FileText,
  Search,
  Plus,
  Send,
  Download,
  Clock,
  CheckCircle,
  AlertCircle,
  Users,
  TrendingUp,
  Calendar,
  Eye,
  Mail,
  MoreVertical
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

const stats = [
  {
    title: 'Sent This Season',
    value: '38',
    change: 12,
    changeLabel: 'vs last year',
    icon: <Send className="w-6 h-6" />,
    iconBg: 'bg-primary-100',
    trend: 'up' as const,
  },
  {
    title: 'Completed',
    value: '24',
    change: 8,
    changeLabel: 'completion rate: 63%',
    icon: <CheckCircle className="w-6 h-6" />,
    iconBg: 'bg-success-100',
    trend: 'up' as const,
  },
  {
    title: 'In Progress',
    value: '10',
    change: -2,
    changeLabel: 'pending docs',
    icon: <Clock className="w-6 h-6" />,
    iconBg: 'bg-warning-100',
    trend: 'down' as const,
  },
  {
    title: 'Not Started',
    value: '4',
    change: -5,
    changeLabel: 'need follow-up',
    icon: <AlertCircle className="w-6 h-6" />,
    iconBg: 'bg-danger-100',
    trend: 'down' as const,
  },
]

const organizers = [
  {
    id: 1,
    clientName: 'Michael Chen',
    clientInitials: 'MC',
    taxYear: '2023',
    status: 'completed',
    progress: 100,
    sentDate: '2024-01-10',
    completedDate: '2024-01-24',
    documentsCollected: 15,
    totalDocuments: 15,
    lastActivity: '2024-01-24',
  },
  {
    id: 2,
    clientName: 'Sarah Johnson',
    clientInitials: 'SJ',
    taxYear: '2023',
    status: 'in-progress',
    progress: 60,
    sentDate: '2024-01-12',
    completedDate: null,
    documentsCollected: 9,
    totalDocuments: 15,
    lastActivity: '2024-01-25',
  },
  {
    id: 3,
    clientName: 'ABC Corporation',
    clientInitials: 'AC',
    taxYear: '2023',
    status: 'in-progress',
    progress: 80,
    sentDate: '2024-01-08',
    completedDate: null,
    documentsCollected: 12,
    totalDocuments: 15,
    lastActivity: '2024-01-26',
  },
  {
    id: 4,
    clientName: 'David Wilson',
    clientInitials: 'DW',
    taxYear: '2023',
    status: 'not-started',
    progress: 0,
    sentDate: '2024-01-15',
    completedDate: null,
    documentsCollected: 0,
    totalDocuments: 12,
    lastActivity: '2024-01-15',
  },
  {
    id: 5,
    clientName: 'Emily Rodriguez',
    clientInitials: 'ER',
    taxYear: '2023',
    status: 'in-progress',
    progress: 33,
    sentDate: '2024-01-20',
    completedDate: null,
    documentsCollected: 5,
    totalDocuments: 15,
    lastActivity: '2024-01-23',
  },
  {
    id: 6,
    clientName: 'Robert Thompson',
    clientInitials: 'RT',
    taxYear: '2023',
    status: 'overdue',
    progress: 20,
    sentDate: '2024-01-05',
    completedDate: null,
    documentsCollected: 3,
    totalDocuments: 15,
    lastActivity: '2024-01-10',
  },
]

export default function OrganizersPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')

  const hasOrganizers = organizers.length > 0
  const completedCount = organizers.filter(o => o.status === 'completed').length
  const inProgressCount = organizers.filter(o => o.status === 'in-progress').length
  const notStartedCount = organizers.filter(o => o.status === 'not-started').length
  const overdueCount = organizers.filter(o => o.status === 'overdue').length

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Tax Organizers</h1>
          <p className="mt-2 text-slate-600">
            Send, track, and manage document collection from clients
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="lg">
            <Download className="w-4 h-4" />
            Export Report
          </Button>
          <Button size="lg">
            <Send className="w-5 h-5" />
            Send Organizer
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Filters */}
      <Card>
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by client name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          {/* Status Filter */}
          <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setSelectedStatus('all')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedStatus === 'all'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All ({organizers.length})
            </button>
            <button
              onClick={() => setSelectedStatus('completed')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedStatus === 'completed'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Complete ({completedCount})
            </button>
            <button
              onClick={() => setSelectedStatus('in-progress')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedStatus === 'in-progress'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              In Progress ({inProgressCount})
            </button>
            <button
              onClick={() => setSelectedStatus('overdue')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedStatus === 'overdue'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Overdue ({overdueCount})
            </button>
          </div>
        </div>
      </Card>

      {!hasOrganizers ? (
        <EmptyStateCard
          title="No organizers sent yet"
          description="Start collecting documents from your clients by sending your first tax organizer. Track progress and get notified when documents are uploaded."
          icon={<FileText className="w-12 h-12 text-slate-400" />}
          action={
            <Button size="lg">
              <Send className="w-5 h-5" />
              Send Your First Organizer
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {organizers.map((organizer) => (
            <Card key={organizer.id} hover className="group">
              <div className="flex items-start gap-6">
                {/* Client Avatar */}
                <div className="flex-shrink-0">
                  <div className={`w-16 h-16 rounded-xl ${
                    organizer.status === 'completed' ? 'bg-gradient-to-br from-success-400 to-success-600' :
                    organizer.status === 'overdue' ? 'bg-gradient-to-br from-danger-400 to-danger-600' :
                    organizer.status === 'in-progress' ? 'bg-gradient-to-br from-primary-400 to-primary-600' :
                    'bg-gradient-to-br from-slate-400 to-slate-600'
                  } flex items-center justify-center text-white font-bold text-xl`}>
                    {organizer.clientInitials}
                  </div>
                </div>

                {/* Organizer Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900 group-hover:text-primary-600 transition-colors">
                        {organizer.clientName}
                      </h3>
                      <p className="text-sm text-slate-600 mt-0.5">
                        Tax Year {organizer.taxYear}
                      </p>
                    </div>
                    <Badge 
                      variant={
                        organizer.status === 'completed' ? 'success' :
                        organizer.status === 'overdue' ? 'danger' :
                        organizer.status === 'in-progress' ? 'primary' :
                        'default'
                      }
                      className="capitalize"
                    >
                      {organizer.status.replace('-', ' ')}
                    </Badge>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">
                        Document Collection Progress
                      </span>
                      <span className="text-sm font-semibold text-slate-900">
                        {organizer.documentsCollected} / {organizer.totalDocuments}
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all ${
                          organizer.status === 'completed' ? 'bg-gradient-to-r from-success-500 to-success-600' :
                          organizer.status === 'overdue' ? 'bg-gradient-to-r from-danger-500 to-danger-600' :
                          'bg-gradient-to-r from-primary-500 to-primary-600'
                        }`}
                        style={{ width: `${organizer.progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Details Grid */}
                  <div className="grid grid-cols-3 gap-6 p-4 bg-slate-50 rounded-lg">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Sent Date</p>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <span className="text-sm font-medium text-slate-900">
                          {formatDate(organizer.sentDate)}
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs text-slate-500 mb-1">
                        {organizer.completedDate ? 'Completed' : 'Last Activity'}
                      </p>
                      <div className="flex items-center gap-2">
                        {organizer.completedDate ? (
                          <>
                            <CheckCircle className="w-4 h-4 text-success-600" />
                            <span className="text-sm font-medium text-success-600">
                              {formatDate(organizer.completedDate)}
                            </span>
                          </>
                        ) : (
                          <>
                            <Clock className="w-4 h-4 text-slate-400" />
                            <span className="text-sm font-medium text-slate-900">
                              {formatDate(organizer.lastActivity)}
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs text-slate-500 mb-1">Status</p>
                      <div className="flex items-center gap-2">
                        {organizer.status === 'completed' ? (
                          <>
                            <CheckCircle className="w-4 h-4 text-success-600" />
                            <span className="text-sm font-medium text-success-600">All docs received</span>
                          </>
                        ) : organizer.status === 'overdue' ? (
                          <>
                            <AlertCircle className="w-4 h-4 text-danger-600" />
                            <span className="text-sm font-medium text-danger-600">Action required</span>
                          </>
                        ) : organizer.status === 'in-progress' ? (
                          <>
                            <Clock className="w-4 h-4 text-primary-600" />
                            <span className="text-sm font-medium text-primary-600">Awaiting docs</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-4 h-4 text-slate-400" />
                            <span className="text-sm font-medium text-slate-600">Not started</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="primary" size="sm">
                      <Eye className="w-4 h-4" />
                      View Details
                    </Button>
                    <Button variant="secondary" size="sm">
                      <Mail className="w-4 h-4" />
                      Send Reminder
                    </Button>
                    <Button variant="secondary" size="sm">
                      <Download className="w-4 h-4" />
                      Download
                    </Button>
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {hasOrganizers && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-600">
            Showing {organizers.length} of {organizers.length} organizers
          </p>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">Previous</Button>
            <Button variant="secondary" size="sm">Next</Button>
          </div>
        </div>
      )}
    </div>
  )
}
