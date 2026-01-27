// Design System Showcase Page
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';

export default function ShowcasePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-display-lg font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Kronos Design System
          </h1>
          <p className="text-body-lg text-gray-600">
            Stripe-inspired components for Laura's Tax Practice
          </p>
        </div>

        {/* Color Palette */}
        <Card className="p-8">
          <h2 className="text-heading-lg font-bold mb-6">Color Palette</h2>
          <div className="grid grid-cols-3 gap-8">
            <div>
              <p className="text-sm font-semibold mb-3">Primary (Deep Blue)</p>
              <div className="space-y-2">
                <div className="h-12 bg-primary-600 rounded-lg flex items-center justify-center text-white font-mono text-sm">#2563EB</div>
                <div className="h-12 bg-primary-700 rounded-lg flex items-center justify-center text-white font-mono text-sm">#1D4ED8</div>
                <div className="h-12 bg-primary-100 rounded-lg flex items-center justify-center text-primary-700 font-mono text-sm">#DBEAFE</div>
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold mb-3">Secondary (Teal)</p>
              <div className="space-y-2">
                <div className="h-12 bg-secondary-600 rounded-lg flex items-center justify-center text-white font-mono text-sm">#0D9488</div>
                <div className="h-12 bg-secondary-700 rounded-lg flex items-center justify-center text-white font-mono text-sm">#0F766E</div>
                <div className="h-12 bg-secondary-100 rounded-lg flex items-center justify-center text-secondary-700 font-mono text-sm">#CCFBF1</div>
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold mb-3">Accent (Coral)</p>
              <div className="space-y-2">
                <div className="h-12 bg-accent-500 rounded-lg flex items-center justify-center text-white font-mono text-sm">#F97316</div>
                <div className="h-12 bg-accent-600 rounded-lg flex items-center justify-center text-white font-mono text-sm">#EA580C</div>
                <div className="h-12 bg-accent-100 rounded-lg flex items-center justify-center text-accent-700 font-mono text-sm">#FFEDD5</div>
              </div>
            </div>
          </div>
        </Card>

        {/* Buttons */}
        <Card className="p-8">
          <h2 className="text-heading-lg font-bold mb-6">Buttons</h2>
          <div className="space-y-6">
            <div className="flex items-center gap-4 flex-wrap">
              <Button variant="primary" size="lg">Primary Button</Button>
              <Button variant="secondary" size="lg">Secondary Button</Button>
              <Button variant="accent" size="lg">Accent Button</Button>
              <Button variant="success" size="lg">Success Button</Button>
              <Button variant="danger" size="lg">Danger Button</Button>
            </div>
            <div className="flex items-center gap-4 flex-wrap">
              <Button variant="primary" size="md">Medium</Button>
              <Button variant="primary" size="sm">Small</Button>
              <Button variant="primary" size="xs">Tiny</Button>
            </div>
            <div className="flex items-center gap-4 flex-wrap">
              <Button variant="primary" loading>Loading...</Button>
              <Button variant="primary" disabled>Disabled</Button>
            </div>
          </div>
        </Card>

        {/* Cards */}
        <div className="grid grid-cols-3 gap-6">
          <Card variant="default" className="p-6">
            <div className="text-heading-md font-bold mb-2">Basic Card</div>
            <p className="text-body-sm text-gray-600">Clean white card with subtle shadow</p>
          </Card>
          
          <Card variant="gradient" className="p-6">
            <div className="text-heading-md font-bold mb-2 text-white">Gradient Card</div>
            <p className="text-body-sm text-white/90">Eye-catching gradient background</p>
          </Card>
          
          <Card variant="glass" className="p-6">
            <div className="text-heading-md font-bold mb-2">Glass Card</div>
            <p className="text-body-sm text-gray-600">Glassmorphism effect</p>
          </Card>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-6">
          <Card variant="stats" className="p-6">
            <div className="text-4xl mb-2">👥</div>
            <div className="text-heading-sm font-semibold text-gray-600">Active Clients</div>
            <div className="text-display-sm font-bold mt-2">42</div>
            <div className="text-sm text-success-600 mt-1">↗ +12%</div>
          </Card>
          
          <Card variant="stats" className="p-6">
            <div className="text-4xl mb-2">🎯</div>
            <div className="text-heading-sm font-semibold text-gray-600">New Leads</div>
            <div className="text-display-sm font-bold mt-2">18</div>
            <div className="text-sm text-success-600 mt-1">↗ +8%</div>
          </Card>
          
          <Card variant="stats" className="p-6">
            <div className="text-4xl mb-2">💰</div>
            <div className="text-heading-sm font-semibold text-gray-600">Revenue</div>
            <div className="text-display-sm font-bold mt-2">$28.5K</div>
            <div className="text-sm text-success-600 mt-1">↗ +15%</div>
          </Card>
          
          <Card variant="stats" className="p-6">
            <div className="text-4xl mb-2">📈</div>
            <div className="text-heading-sm font-semibold text-gray-600">Retention</div>
            <div className="text-display-sm font-bold mt-2">94%</div>
            <div className="text-sm text-success-600 mt-1">↗ +2%</div>
          </Card>
        </div>

        {/* Badges */}
        <Card className="p-8">
          <h2 className="text-heading-lg font-bold mb-6">Badges</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Badge variant="success">Active</Badge>
              <Badge variant="warning">Pending</Badge>
              <Badge variant="danger">Cancelled</Badge>
              <Badge variant="primary">In Progress</Badge>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="gray" size="sm">Low Priority</Badge>
              <Badge variant="primary" size="sm">Medium Priority</Badge>
              <Badge variant="warning" size="sm">High Priority</Badge>
              <Badge variant="danger" size="sm">Urgent</Badge>
            </div>
          </div>
        </Card>

        {/* Inputs */}
        <Card className="p-8">
          <h2 className="text-heading-lg font-bold mb-6">Form Inputs</h2>
          <div className="space-y-6 max-w-md">
            <Input
              label="Email Address"
              type="email"
              placeholder="you@example.com"
              required
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              required
            />
            <Input
              label="Phone Number"
              type="tel"
              placeholder="(555) 123-4567"
              helperText="We'll never share your number"
            />
            <Input
              label="Error State"
              type="text"
              error="This field is required"
            />
          </div>
        </Card>

        {/* Typography */}
        <Card className="p-8">
          <h2 className="text-heading-lg font-bold mb-6">Typography Scale</h2>
          <div className="space-y-4">
            <div className="text-display-lg font-bold">Display Large (60px)</div>
            <div className="text-display-md font-bold">Display Medium (48px)</div>
            <div className="text-heading-xl font-bold">Heading XL (30px)</div>
            <div className="text-heading-lg font-semibold">Heading Large (24px)</div>
            <div className="text-heading-md font-medium">Heading Medium (20px)</div>
            <div className="text-body-lg">Body Large (18px) - Important text</div>
            <div className="text-body-md">Body Medium (16px) - Default body text</div>
            <div className="text-body-sm text-gray-600">Body Small (14px) - Secondary information</div>
          </div>
        </Card>

      </div>
    </div>
  );
}
