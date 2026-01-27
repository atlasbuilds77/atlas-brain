'use client'

import { useState } from 'react'
import { Card, CardHeader, EmptyStateCard, StatsCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Table } from '@/components/ui/Table'
import { 
  Users,
  Search,
  Filter,
  Plus,
  Mail,
  Phone,
  FileText,
  MessageSquare,
  MoreVertical,
  Download,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  DollarSign
} from 'lucide-react'
import { formatCurrency, formatDate } from '@/lib/utils'

const stats = [
  {
    title: 'Total Clients',
    value: '42',
    change: 12,
    changeLabel: 'vs last month',
    icon: <Users className="w-6 h-6" />,
    iconBg: 'bg-primary-100',
    trend: 'up' as const,
  },
  {
    title: 'Active This Month',
    value: '38',
    change: 5,
    changeLabel: 'vs last month',
    icon: <TrendingUp className="w-6 h-6" />,
    iconBg: 'bg-success-100',
    trend: 'up' as const,
  },
  {
    title: 'Total Revenue',
    value: formatCurrency(156800),
    change: 18,
    changeLabel: 'vs last year',
    icon: <DollarSign className="w-6 h-6" />,
    iconBg: 'bg-warning-100',
    trend: 'up' as const,
  },
  {
    title: 'Avg. Client Value',
    value: formatCurrency(3733),
    change: 8,
    changeLabel: 'vs last year',
    icon: <CheckCircle className="w-6 h-6" />,
    iconBg: 'bg-success-100',
    trend: 'up' as const,
  },
]

const clients = [
  {
    id: 1,
    name: 'Michael Chen',
    company: 'Chen Industries',
    email: 'michael@chen.com',
    phone: '(555) 111-2222',
    status: 'active',
    lastActivity: '2024-01-26',
    totalRevenue: 12500,
    servicesUsed: ['Individual Tax', 'Business Tax', 'Bookkeeping'],
    documentStatus: 'complete',
    taxYear: '2023',
    nextDeadline: '2024-04-15',
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    company: 'Johnson Consulting LLC',
    email: 'sarah@johnson.com',
    phone: '(555) 222-3333',
    status: 'active',
    lastActivity: '2024-01-25',
    totalRevenue: 8900,
    servicesUsed: ['S-Corp Tax', 'Payroll'],
    documentStatus: 'pending',
    taxYear: '2023',
    nextDeadline: '2024-03-15',
  },
  {
    id: 3,
    name: 'ABC Corporation',
    company: 'ABC Corp',
    email: 'finance@abccorp.com',
    phone: '(555) 333-4444',
    status: 'active',
    lastActivity: '2024-01-24',
    totalRevenue: 25000,
    servicesUsed: ['Corporate Tax', 'Audit Support', 'Planning'],
    documentStatus: 'in-progress',
    taxYear: '2023',
    nextDeadline: '2024-03-01',
  },
  {
    id: 4,
    name: 'David Wilson',
    company: 'Wilson & Associates',
    email: 'david@wilson.com',
    phone: '(555) 444-5555',
    status: 'inactive',
    lastActivity: '2023-12-15',
    totalRevenue: 5600,
    servicesUsed: ['Individual Tax'],
    documentStatus: 'complete',
    taxYear: '2022',
    nextDeadline: null,
  },
  {
    id: 5,
    name: 'Emily Rodriguez',
    company: 'Rodriguez Tech',
    email: 'emily@rodtech.com',
    phone: '(555) 555-6666',
    status: 'active',
    lastActivity: '2024-01-26',
    totalRevenue: 15300,
    servicesUsed: ['Business Tax', 'R&D Credits', 'Planning'],
    documentStatus: 'pending',
    taxYear: '2023',
    nextDeadline: '2024-02-28',
  },
]

export default function ClientsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')

  const hasClients = clients.length > 0
  const activeClients = clients.filter(c => c.status === 'active').length

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Client Management</h1>
          <p className="mt-2 text-slate-600">
            Manage your client relationships and track their progress
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="lg">
            <Download className="w-4 h-4" />
            Export
          </Button>
          <Button size="lg">
            <Plus className="w-5 h-5" />
            Add Client
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
              placeholder="Search clients by name, company, or email..."
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
              All ({clients.length})
            </button>
            <button
              onClick={() => setSelectedStatus('active')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedStatus === 'active'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Active ({activeClients})
            </button>
            <button
              onClick={() => setSelectedStatus('inactive')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedStatus === 'inactive'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Inactive ({clients.length - activeClients})
            </button>
          </div>

          <Button variant="secondary">
            <Filter className="w-4 h-4" />
            More Filters
          </Button>
        </div>
      </Card>

      {/* Clients List or Empty State */}
      {!hasClients ? (
        <EmptyStateCard
          title="No clients yet"
          description="Add your first client to start managing their tax documents, communications, and billing all in one place."
          icon={<Users className="w-12 h-12 text-slate-400" />}
          action={
            <Button size="lg">
              <Plus className="w-5 h-5" />
              Add Your First Client
            </Button>
          }
        />
      ) : (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Documents
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Next Deadline
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {clients.map((client) => (
                  <tr key={client.id} className="hover:bg-slate-50 transition-colors group">
                    {/* Client Info */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                          {client.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="min-w-0">
                          <p className="font-semibold text-slate-900 truncate">
                            {client.name}
                          </p>
                          <p className="text-sm text-slate-600 truncate">
                            {client.company}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* Contact */}
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-sm text-slate-600">
                          <Mail className="w-3.5 h-3.5 text-slate-400" />
                          <span className="truncate max-w-[200px]">{client.email}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-slate-600">
                          <Phone className="w-3.5 h-3.5 text-slate-400" />
                          <span>{client.phone}</span>
                        </div>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge 
                        variant={client.status === 'active' ? 'success' : 'default'}
                        className="capitalize"
                      >
                        {client.status}
                      </Badge>
                      <p className="text-xs text-slate-500 mt-1">
                        {formatDate(client.lastActivity)}
                      </p>
                    </td>

                    {/* Document Status */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {client.documentStatus === 'complete' && (
                          <>
                            <CheckCircle className="w-4 h-4 text-success-600" />
                            <span className="text-sm font-medium text-success-600">Complete</span>
                          </>
                        )}
                        {client.documentStatus === 'pending' && (
                          <>
                            <Clock className="w-4 h-4 text-warning-600" />
                            <span className="text-sm font-medium text-warning-600">Pending</span>
                          </>
                        )}
                        {client.documentStatus === 'in-progress' && (
                          <>
                            <AlertCircle className="w-4 h-4 text-primary-600" />
                            <span className="text-sm font-medium text-primary-600">In Progress</span>
                          </>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Tax Year {client.taxYear}
                      </p>
                    </td>

                    {/* Revenue */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="font-semibold text-slate-900">
                        {formatCurrency(client.totalRevenue)}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        {client.servicesUsed.length} services
                      </p>
                    </td>

                    {/* Next Deadline */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {client.nextDeadline ? (
                        <div>
                          <p className="text-sm font-medium text-slate-900">
                            {formatDate(client.nextDeadline)}
                          </p>
                          <p className="text-xs text-slate-500 mt-1">
                            {/* Calculate days until deadline */}
                            {Math.ceil((new Date(client.nextDeadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days
                          </p>
                        </div>
                      ) : (
                        <span className="text-sm text-slate-400">No deadline</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="sm">
                          <MessageSquare className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <FileText className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Pagination */}
      {hasClients && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-600">
            Showing {clients.length} of {clients.length} clients
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
