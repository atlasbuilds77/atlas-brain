'use client'

import { useState } from 'react'
import { Card, CardHeader, StatsCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { 
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  UserPlus,
  Target,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

const stats = [
  {
    title: 'Total Revenue',
    value: formatCurrency(156800),
    change: 18,
    changeLabel: 'vs last year',
    icon: <DollarSign className="w-6 h-6" />,
    iconBg: 'bg-success-100',
    trend: 'up' as const,
  },
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
    title: 'Lead Conversion',
    value: '68%',
    change: 5,
    changeLabel: 'vs last quarter',
    icon: <Target className="w-6 h-6" />,
    iconBg: 'bg-purple-100',
    trend: 'up' as const,
  },
  {
    title: 'Avg Client Value',
    value: formatCurrency(3733),
    change: 8,
    changeLabel: 'vs last year',
    icon: <TrendingUp className="w-6 h-6" />,
    iconBg: 'bg-warning-100',
    trend: 'up' as const,
  },
]

// Revenue data (mock)
const revenueByMonth = [
  { month: 'Jan', revenue: 8500, clients: 38 },
  { month: 'Feb', revenue: 12300, clients: 39 },
  { month: 'Mar', revenue: 15600, clients: 40 },
  { month: 'Apr', revenue: 22400, clients: 41 },
  { month: 'May', revenue: 18200, clients: 42 },
  { month: 'Jun', revenue: 16800, clients: 42 },
]

const serviceRevenue = [
  { service: 'Individual Tax', revenue: 48500, percentage: 31, clients: 28 },
  { service: 'Business Tax', revenue: 42300, percentage: 27, clients: 12 },
  { service: 'Bookkeeping', revenue: 28900, percentage: 18, clients: 15 },
  { service: 'Tax Planning', revenue: 22400, percentage: 14, clients: 8 },
  { service: 'Audit Support', revenue: 14700, percentage: 10, clients: 5 },
]

const leadSources = [
  { source: 'Referrals', count: 24, percentage: 42 },
  { source: 'Website', count: 16, percentage: 28 },
  { source: 'LinkedIn', count: 10, percentage: 18 },
  { source: 'Google', count: 7, percentage: 12 },
]

const topClients = [
  { name: 'ABC Corporation', revenue: 25000, services: 3, growth: 15 },
  { name: 'Emily Rodriguez', revenue: 15300, services: 3, growth: 22 },
  { name: 'Michael Chen', revenue: 12500, services: 3, growth: 8 },
  { name: 'Sarah Johnson', revenue: 8900, services: 2, growth: -5 },
  { name: 'David Wilson', revenue: 5600, services: 1, growth: 0 },
]

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('year')
  const maxRevenue = Math.max(...revenueByMonth.map(m => m.revenue))

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics & Insights</h1>
          <p className="mt-2 text-slate-600">
            Track your practice performance and make data-driven decisions
          </p>
          <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
            <Activity className="w-4 h-4" />
            <span>Last updated: Just now</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="lg">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <Button variant="secondary" size="lg">
            <Download className="w-4 h-4" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Time Range Selector */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-slate-600" />
            <span className="font-semibold text-slate-900">Time Period:</span>
          </div>
          <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-1">
            {['week', 'month', 'quarter', 'year'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors capitalize ${
                  timeRange === range
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Trend */}
        <Card className="lg:col-span-2">
          <CardHeader 
            title="Revenue Trend" 
            subtitle="Monthly revenue over time"
            icon={<BarChart3 className="w-5 h-5 text-primary-600" />}
            action={
              <Button variant="ghost" size="sm">
                <Filter className="w-4 h-4" />
              </Button>
            }
          />
          
          <div className="mt-6 space-y-4">
            {revenueByMonth.map((month, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-700">{month.month}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-slate-600">{month.clients} clients</span>
                    <span className="font-semibold text-slate-900">
                      {formatCurrency(month.revenue)}
                    </span>
                  </div>
                </div>
                <div className="relative w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                  <div 
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all"
                    style={{ width: `${(month.revenue / maxRevenue) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-200 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-slate-600 mb-1">Avg. Monthly</p>
              <p className="text-lg font-bold text-slate-900">
                {formatCurrency(revenueByMonth.reduce((sum, m) => sum + m.revenue, 0) / revenueByMonth.length)}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-600 mb-1">Highest Month</p>
              <p className="text-lg font-bold text-success-600">
                {formatCurrency(maxRevenue)}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-600 mb-1">Growth Rate</p>
              <p className="text-lg font-bold text-success-600">+18%</p>
            </div>
          </div>
        </Card>

        {/* Lead Sources */}
        <Card>
          <CardHeader 
            title="Lead Sources" 
            subtitle="Where clients come from"
            icon={<PieChart className="w-5 h-5 text-primary-600" />}
          />
          
          <div className="mt-6 space-y-4">
            {leadSources.map((source, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-700">{source.source}</span>
                  <span className="font-semibold text-slate-900">{source.count}</span>
                </div>
                <div className="relative w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className={`absolute inset-y-0 left-0 rounded-full ${
                      index === 0 ? 'bg-primary-500' :
                      index === 1 ? 'bg-success-500' :
                      index === 2 ? 'bg-purple-500' :
                      'bg-warning-500'
                    }`}
                    style={{ width: `${source.percentage}%` }}
                  />
                </div>
                <p className="text-xs text-slate-500">{source.percentage}% of total leads</p>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Total Leads</span>
              <span className="text-lg font-bold text-slate-900">
                {leadSources.reduce((sum, s) => sum + s.count, 0)}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Service Revenue Breakdown */}
      <Card>
        <CardHeader 
          title="Revenue by Service" 
          subtitle="Which services generate the most revenue"
          icon={<DollarSign className="w-5 h-5 text-success-600" />}
        />
        
        <div className="mt-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Service
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Clients
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    % of Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Distribution
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {serviceRevenue.map((service, index) => (
                  <tr key={index} className="hover:bg-slate-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-medium text-slate-900">{service.service}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-semibold text-slate-900">
                        {formatCurrency(service.revenue)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-slate-600">{service.clients}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant="default">{service.percentage}%</Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-success-500 to-success-600 rounded-full"
                          style={{ width: `${service.percentage}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Card>

      {/* Top Clients */}
      <Card>
        <CardHeader 
          title="Top Clients by Revenue" 
          subtitle="Your most valuable client relationships"
          icon={<Users className="w-5 h-5 text-primary-600" />}
          action={
            <Button variant="secondary" size="sm">View All</Button>
          }
        />
        
        <div className="mt-6 space-y-3">
          {topClients.map((client, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 text-white font-bold">
                  #{index + 1}
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{client.name}</p>
                  <p className="text-sm text-slate-600">{client.services} services</p>
                </div>
              </div>
              
              <div className="flex items-center gap-8">
                <div className="text-right">
                  <p className="text-sm text-slate-600">Revenue</p>
                  <p className="font-bold text-slate-900">{formatCurrency(client.revenue)}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-slate-600">Growth</p>
                  <div className="flex items-center gap-1">
                    {client.growth > 0 ? (
                      <>
                        <TrendingUp className="w-4 h-4 text-success-600" />
                        <span className="font-bold text-success-600">+{client.growth}%</span>
                      </>
                    ) : client.growth < 0 ? (
                      <>
                        <TrendingDown className="w-4 h-4 text-danger-600" />
                        <span className="font-bold text-danger-600">{client.growth}%</span>
                      </>
                    ) : (
                      <span className="font-bold text-slate-600">0%</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Performance Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gradient-to-br from-primary-500 to-primary-600 text-white">
          <div className="flex items-center justify-between mb-4">
            <Target className="w-8 h-8 opacity-80" />
            <Badge variant="success" className="bg-white/20 text-white border-white/30">
              Excellent
            </Badge>
          </div>
          <h3 className="text-2xl font-bold mb-1">68%</h3>
          <p className="text-sm opacity-90">Lead Conversion Rate</p>
          <p className="text-xs opacity-70 mt-2">+5% from last quarter</p>
        </Card>

        <Card className="bg-gradient-to-br from-success-500 to-success-600 text-white">
          <div className="flex items-center justify-between mb-4">
            <Users className="w-8 h-8 opacity-80" />
            <Badge variant="success" className="bg-white/20 text-white border-white/30">
              Growing
            </Badge>
          </div>
          <h3 className="text-2xl font-bold mb-1">94%</h3>
          <p className="text-sm opacity-90">Client Retention Rate</p>
          <p className="text-xs opacity-70 mt-2">+2% from last quarter</p>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="w-8 h-8 opacity-80" />
            <Badge variant="warning" className="bg-white/20 text-white border-white/30">
              Strong
            </Badge>
          </div>
          <h3 className="text-2xl font-bold mb-1">{formatCurrency(3733)}</h3>
          <p className="text-sm opacity-90">Avg. Client Lifetime Value</p>
          <p className="text-xs opacity-70 mt-2">+8% from last year</p>
        </Card>
      </div>
    </div>
  )
}
