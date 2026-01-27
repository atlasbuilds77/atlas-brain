'use client'

import { useState } from 'react'
import { Card, CardHeader, EmptyStateCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  UserPlus,
  Search,
  Filter,
  Mail,
  Phone,
  Calendar,
  ChevronRight,
  TrendingUp,
  Users,
  Target,
  Clock,
  DollarSign,
  MoreHorizontal
} from 'lucide-react'
import { formatCurrency, formatDate } from '@/lib/utils'

// Lead pipeline stages
const pipelineStages = [
  { id: 'new', name: 'New', count: 8, color: 'bg-slate-500' },
  { id: 'contacted', name: 'Contacted', count: 5, color: 'bg-blue-500' },
  { id: 'qualified', name: 'Qualified', count: 3, color: 'bg-purple-500' },
  { id: 'proposal', name: 'Proposal Sent', count: 2, color: 'bg-orange-500' },
  { id: 'converting', name: 'Converting', count: 1, color: 'bg-success-500' },
]

// Mock leads data
const leads = [
  {
    id: 1,
    name: 'David Martinez',
    company: 'Martinez Consulting LLC',
    email: 'david@martinez.com',
    phone: '(555) 123-4567',
    status: 'new',
    source: 'Website',
    estimatedValue: 5000,
    lastContact: '2024-01-26',
    nextAction: 'Schedule initial consultation',
    tags: ['Individual', 'S-Corp'],
  },
  {
    id: 2,
    name: 'Emily Rodriguez',
    company: 'Rodriguez Tech Solutions',
    email: 'emily@rodtech.com',
    phone: '(555) 234-5678',
    status: 'contacted',
    source: 'Referral',
    estimatedValue: 8000,
    lastContact: '2024-01-25',
    nextAction: 'Send service proposal',
    tags: ['Business', 'Multi-state'],
  },
  {
    id: 3,
    name: 'James Wilson',
    company: 'Wilson & Associates',
    email: 'james@wilson.com',
    phone: '(555) 345-6789',
    status: 'qualified',
    source: 'LinkedIn',
    estimatedValue: 12000,
    lastContact: '2024-01-24',
    nextAction: 'Follow-up call scheduled',
    tags: ['Partnership', 'High-value'],
  },
  {
    id: 4,
    name: 'Lisa Anderson',
    company: 'Anderson Real Estate',
    email: 'lisa@anderson.com',
    phone: '(555) 456-7890',
    status: 'proposal',
    source: 'Google',
    estimatedValue: 6500,
    lastContact: '2024-01-23',
    nextAction: 'Review proposal feedback',
    tags: ['Real Estate', 'Individual'],
  },
]

// Pipeline stats
const pipelineStats = [
  {
    label: 'Conversion Rate',
    value: '68%',
    change: '+5%',
    icon: Target,
    color: 'text-success-600',
  },
  {
    label: 'Avg. Deal Value',
    value: formatCurrency(7875),
    change: '+$1,200',
    icon: DollarSign,
    color: 'text-primary-600',
  },
  {
    label: 'Avg. Close Time',
    value: '18 days',
    change: '-3 days',
    icon: Clock,
    color: 'text-purple-600',
  },
]

export default function LeadsPage() {
  const [selectedStage, setSelectedStage] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const totalLeads = leads.length
  const hasLeads = leads.length > 0

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Lead Management</h1>
          <p className="mt-2 text-slate-600">
            Track and convert leads into loyal clients
          </p>
        </div>
        <Button size="lg">
          <UserPlus className="w-5 h-5" />
          Add New Lead
        </Button>
      </div>

      {/* Pipeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {pipelineStats.map((stat, index) => (
          <Card key={index} hover>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 font-medium">{stat.label}</p>
                <div className="flex items-baseline gap-2 mt-2">
                  <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
                  <span className={`text-sm font-semibold ${stat.color}`}>
                    {stat.change}
                  </span>
                </div>
              </div>
              <div className={`w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Pipeline Stages */}
      <Card>
        <CardHeader 
          title="Lead Pipeline" 
          subtitle={`${totalLeads} total leads across all stages`}
          icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
        />
        
        <div className="mt-6 grid grid-cols-5 gap-4">
          {pipelineStages.map((stage) => (
            <button
              key={stage.id}
              onClick={() => setSelectedStage(stage.id)}
              className={`p-4 rounded-xl border-2 transition-all hover:shadow-md ${
                selectedStage === stage.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className={`w-8 h-8 rounded-lg ${stage.color} flex items-center justify-center`}>
                  <span className="text-white font-bold text-sm">{stage.count}</span>
                </div>
                <ChevronRight className={`w-4 h-4 ${
                  selectedStage === stage.id ? 'text-primary-600' : 'text-slate-400'
                }`} />
              </div>
              <p className={`font-semibold ${
                selectedStage === stage.id ? 'text-slate-900' : 'text-slate-700'
              }`}>
                {stage.name}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {stage.count} {stage.count === 1 ? 'lead' : 'leads'}
              </p>
            </button>
          ))}
        </div>
      </Card>

      {/* Filters and Search */}
      <Card>
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search leads by name, company, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <Button variant="secondary">
            <Filter className="w-4 h-4" />
            Filters
          </Button>
          <Button variant="secondary">
            Export
          </Button>
        </div>
      </Card>

      {/* Leads List or Empty State */}
      {!hasLeads ? (
        <EmptyStateCard
          title="No leads yet"
          description="Start building your client pipeline by adding your first lead. Track prospects, manage communications, and convert them into clients."
          icon={<UserPlus className="w-12 h-12 text-slate-400" />}
          action={
            <Button size="lg">
              <UserPlus className="w-5 h-5" />
              Add Your First Lead
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          {leads.map((lead) => (
            <Card key={lead.id} hover className="group cursor-pointer">
              <div className="flex items-start gap-6">
                {/* Lead Avatar */}
                <div className="flex-shrink-0">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-lg">
                    {lead.name.split(' ').map(n => n[0]).join('')}
                  </div>
                </div>

                {/* Lead Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900 group-hover:text-primary-600 transition-colors">
                        {lead.name}
                      </h3>
                      <p className="text-sm text-slate-600 mt-0.5">
                        {lead.company}
                      </p>
                    </div>
                    <Badge 
                      variant={
                        lead.status === 'new' ? 'default' :
                        lead.status === 'contacted' ? 'primary' :
                        lead.status === 'qualified' ? 'accent' :
                        lead.status === 'proposal' ? 'warning' :
                        'success'
                      }
                      className="capitalize"
                    >
                      {lead.status}
                    </Badge>
                  </div>

                  {/* Contact Info */}
                  <div className="flex items-center gap-6 mb-4 text-sm text-slate-600">
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4 text-slate-400" />
                      <span>{lead.email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-slate-400" />
                      <span>{lead.phone}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-slate-400" />
                      <span>{lead.source}</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex items-center gap-2 mb-4">
                    {lead.tags.map((tag, index) => (
                      <span 
                        key={index}
                        className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Next Action & Details */}
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-8">
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Next Action</p>
                        <p className="text-sm font-semibold text-slate-900">
                          {lead.nextAction}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Estimated Value</p>
                        <p className="text-sm font-semibold text-success-600">
                          {formatCurrency(lead.estimatedValue)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Last Contact</p>
                        <p className="text-sm font-semibold text-slate-900">
                          {formatDate(lead.lastContact)}
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button variant="secondary" size="sm">
                        <Mail className="w-4 h-4" />
                        Email
                      </Button>
                      <Button variant="secondary" size="sm">
                        <Phone className="w-4 h-4" />
                        Call
                      </Button>
                      <Button variant="primary" size="sm">
                        <Calendar className="w-4 h-4" />
                        Schedule
                      </Button>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Show pagination if there are leads */}
      {hasLeads && (
        <div className="flex items-center justify-between pt-4">
          <p className="text-sm text-slate-600">
            Showing {leads.length} of {totalLeads} leads
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
