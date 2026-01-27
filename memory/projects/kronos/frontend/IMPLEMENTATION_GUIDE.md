# Kronos Design Upgrade - Implementation Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd memory/projects/kronos/frontend
npm install clsx lucide-react
```

### 2. Design System Files

All design system files are updated:
- ✅ `tailwind.config.js` - Complete design tokens
- ✅ `app/globals.css` - Enhanced CSS classes
- ✅ `DESIGN_SPECIFICATION.md` - Full documentation

### 3. Component Library

All UI components upgraded:
- ✅ `components/ui/Button.tsx`
- ✅ `components/ui/Card.tsx`
- ✅ `components/ui/Badge.tsx`
- ✅ `components/ui/Input.tsx`
- ✅ `components/ui/Table.tsx`

Layout components enhanced:
- ✅ `components/layout/Header.tsx`
- ✅ `components/layout/Sidebar.tsx`

---

## 📖 Usage Examples

### Button Component

```tsx
import { Button, IconButton, ButtonGroup } from '@/components/ui/Button'
import { Plus, Download, Settings } from 'lucide-react'

// Primary button with icon
<Button variant="primary" size="md" icon={<Plus />}>
  Add Client
</Button>

// Loading state
<Button loading variant="primary">
  Saving...
</Button>

// Icon-only button
<IconButton 
  icon={<Settings />} 
  label="Settings"
  variant="ghost"
/>

// Button group
<ButtonGroup>
  <Button variant="secondary">Week</Button>
  <Button variant="secondary">Month</Button>
  <Button variant="secondary">Year</Button>
</ButtonGroup>
```

### Card Component

```tsx
import { Card, CardHeader, StatsCard, MetricCard } from '@/components/ui/Card'
import { Users } from 'lucide-react'

// Basic card
<Card>
  <CardHeader 
    title="Recent Activity"
    subtitle="Last 30 days"
    action={<Button size="sm">View All</Button>}
  />
  <CardContent>
    {/* Content here */}
  </CardContent>
</Card>

// Stats card with trend
<StatsCard
  title="Active Clients"
  value={42}
  change={12}
  changeLabel="vs last month"
  trend="up"
  icon={<Users className="w-6 h-6" />}
  iconBg="bg-primary-100"
/>

// Gradient card
<Card gradient="primary" className="text-white">
  <h3>Premium Feature</h3>
  <p>Unlock advanced analytics</p>
</Card>

// Glass effect card
<Card glass className="backdrop-blur-md">
  <p>Content with glass morphism</p>
</Card>
```

### Badge Component

```tsx
import { Badge, StatusBadge, PriorityBadge, NotificationBadge } from '@/components/ui/Badge'
import { Bell } from 'lucide-react'

// Basic badges
<Badge variant="primary">New</Badge>
<Badge variant="success" dot>Active</Badge>
<Badge variant="warning" icon={<AlertCircle />}>Warning</Badge>

// Status badge
<StatusBadge status="active" />
<StatusBadge status="pending" />

// Priority badge
<PriorityBadge priority="high" />
<PriorityBadge priority="urgent" />

// Notification badge
<NotificationBadge count={5} position="top-right">
  <Bell className="w-5 h-5" />
</NotificationBadge>
```

### Input Component

```tsx
import { Input, SearchInput, Textarea, Select } from '@/components/ui/Input'
import { Mail, Lock } from 'lucide-react'

// Input with label and icon
<Input
  label="Email Address"
  type="email"
  placeholder="you@example.com"
  leftIcon={<Mail className="w-4 h-4" />}
  required
/>

// Password input (auto-toggles visibility)
<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>

// Success state
<Input
  label="Username"
  value="johndoe"
  success="Username is available"
/>

// Search input
<SearchInput
  placeholder="Search clients..."
  onClear={() => setQuery('')}
/>

// Textarea
<Textarea
  label="Notes"
  placeholder="Enter your notes..."
  rows={4}
  hint="Maximum 500 characters"
/>

// Select
<Select
  label="Client Status"
  options={[
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
  ]}
/>
```

### Table Component

```tsx
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell,
  TableLoadingState,
  TableEmptyState,
  Pagination
} from '@/components/ui/Table'

// Complete table example
<Table>
  <TableHeader>
    <TableRow>
      <TableHead sortable sortDirection="asc" onSort={() => sort('name')}>
        Name
      </TableHead>
      <TableHead>Email</TableHead>
      <TableHead>Status</TableHead>
      <TableHead align="right">Actions</TableHead>
    </TableRow>
  </TableHeader>
  
  <TableBody>
    {loading ? (
      <TableLoadingState rows={5} cols={4} />
    ) : data.length === 0 ? (
      <TableEmptyState
        title="No clients found"
        description="Get started by adding your first client"
        icon={<Users />}
        action={<Button>Add Client</Button>}
        colSpan={4}
      />
    ) : (
      data.map((row) => (
        <TableRow key={row.id} onClick={() => view(row.id)}>
          <TableCell>{row.name}</TableCell>
          <TableCell>{row.email}</TableCell>
          <TableCell>
            <StatusBadge status={row.status} />
          </TableCell>
          <TableCell>
            <TableActionCell
              onView={() => view(row.id)}
              onEdit={() => edit(row.id)}
              onDelete={() => delete(row.id)}
            />
          </TableCell>
        </TableRow>
      ))
    )}
  </TableBody>
</Table>

<Pagination
  currentPage={1}
  totalPages={10}
  onPageChange={setPage}
  itemsPerPage={20}
  totalItems={200}
/>
```

---

## 🎨 Design Tokens Usage

### Colors

```tsx
// Background colors
className="bg-primary-600"      // Main primary
className="bg-success-100"      // Light success
className="bg-danger-50"        // Very light danger

// Text colors
className="text-gray-900"       // Primary text
className="text-gray-600"       // Secondary text
className="text-primary-700"    // Primary brand text

// Border colors
className="border-gray-200"     // Default border
className="border-primary-500"  // Primary border
```

### Typography

```tsx
// Headings
className="text-heading-xl"     // 30px, -0.02em
className="text-heading-lg"     // 24px, -0.02em
className="text-heading-md"     // 20px, -0.02em

// Body text
className="text-body-lg"        // 18px
className="text-body-md"        // 16px (default)
className="text-body-sm"        // 14px

// Labels
className="text-label"          // 12px, 0.05em
```

### Shadows

```tsx
// Cards
className="shadow-card"         // Default card shadow
className="hover:shadow-card-hover"  // Hover elevation

// Glow effects
className="focus:shadow-glow-primary"  // Focus glow

// Elevation
className="shadow-lg"           // Large shadow
className="shadow-xl"           // Extra large
```

### Animations

```tsx
// Fade effects
className="animate-fade-in"     // Fade in
className="animate-fade-out"    // Fade out

// Slide effects
className="animate-slide-up"    // Slide up
className="animate-slide-down"  // Slide down

// Scale
className="animate-scale-in"    // Scale in

// Duration
className="duration-fast"       // 150ms
className="duration-normal"     // 300ms
className="duration-slow"       // 500ms
```

---

## 🎯 Common Patterns

### Loading States

```tsx
// Button loading
<Button loading>Saving...</Button>

// Card loading (skeleton)
<StatsCard loading />

// Table loading
<TableLoadingState rows={5} cols={4} />

// Custom skeleton
<div className="space-y-3">
  <div className="skeleton h-4 w-3/4" />
  <div className="skeleton h-4 w-1/2" />
</div>
```

### Empty States

```tsx
// Table empty state
<TableEmptyState
  title="No data"
  description="Add your first item"
  icon={<Inbox />}
  action={<Button>Add Item</Button>}
/>

// Card empty state
<EmptyStateCard
  title="No messages"
  description="You're all caught up!"
  icon={<Mail />}
  action={<Button>Compose</Button>}
/>
```

### Form Patterns

```tsx
// Login form
<form className="space-y-4">
  <Input
    label="Email"
    type="email"
    leftIcon={<Mail />}
    required
  />
  <Input
    label="Password"
    type="password"
    required
  />
  <Button type="submit" fullWidth>
    Sign In
  </Button>
</form>

// Filter form
<div className="flex gap-3">
  <SearchInput 
    placeholder="Search..." 
    className="flex-1"
  />
  <Select
    options={statusOptions}
    className="w-40"
  />
  <Button variant="ghost">
    <Filter className="w-4 h-4" />
  </Button>
</div>
```

### Dashboard Cards

```tsx
// Stats grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {stats.map((stat) => (
    <StatsCard key={stat.title} {...stat} />
  ))}
</div>

// Action cards
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {actions.map((action) => (
    <Card hover className="cursor-pointer">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${action.color}`}>
          {action.icon}
        </div>
        <div>
          <h3 className="font-semibold">{action.title}</h3>
          <p className="text-sm text-gray-500">{action.description}</p>
        </div>
      </div>
    </Card>
  ))}
</div>
```

---

## 🔧 Utility Classes

### Layout

```tsx
className="container mx-auto px-6"  // Container
className="grid grid-cols-12 gap-6" // Grid
className="flex items-center gap-4" // Flexbox
className="space-y-6"                // Vertical spacing
```

### Responsive

```tsx
className="hidden md:block"         // Show on md+
className="grid-cols-1 md:grid-cols-2 lg:grid-cols-4"  // Responsive grid
className="text-sm md:text-base"    // Responsive text
```

### Interactive

```tsx
className="hover:bg-gray-100"       // Hover background
className="active:scale-95"         // Active scale
className="focus:ring-2 focus:ring-primary-500"  // Focus ring
className="cursor-pointer"          // Pointer cursor
```

---

## 📚 Best Practices

### 1. Consistency
- Always use design tokens (colors, spacing, shadows)
- Use component variants instead of custom classes
- Follow naming conventions

### 2. Accessibility
- Include ARIA labels on icon-only buttons
- Use proper heading hierarchy
- Maintain color contrast ratios
- Support keyboard navigation

### 3. Performance
- Use loading states for async operations
- Implement skeleton screens
- Optimize images and assets

### 4. Maintainability
- Use TypeScript for type safety
- Document component props
- Create reusable patterns

---

## 🐛 Troubleshooting

### Styles not applying
1. Rebuild Tailwind: `npm run dev`
2. Check class name spelling
3. Verify import paths

### Components not found
1. Check import path: `@/components/ui/...`
2. Verify file exists
3. Check TypeScript errors

### Icons not showing
1. Install lucide-react: `npm install lucide-react`
2. Import icons: `import { Icon } from 'lucide-react'`

---

## 📞 Support

For questions or issues:
1. Check `DESIGN_SPECIFICATION.md`
2. Review `BEFORE_AFTER_COMPARISON.md`
3. Inspect component source code
4. Check Tailwind docs: https://tailwindcss.com

---

## 🎉 You're Ready!

The design system is complete and ready to use. Start building beautiful interfaces with confidence! 🚀