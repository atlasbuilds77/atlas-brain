# Kronos Design System Specification

## Brand Identity for Laura's Tax Practice

### Core Values
- **Trustworthy**: Professional, reliable, secure
- **Modern**: Clean, contemporary, efficient
- **Approachable**: Friendly, helpful, clear
- **Precise**: Accurate, detailed, organized

### Color Palette

#### Primary Colors (Tax Professional)
- **Primary**: Deep Blue (#2563EB) - Trust, stability, professionalism
- **Secondary**: Teal (#0D9488) - Growth, clarity, precision
- **Accent**: Coral (#F97316) - Attention, action, warmth
- **Success**: Emerald (#10B981) - Growth, completion, success
- **Warning**: Amber (#F59E0B) - Caution, attention needed
- **Danger**: Rose (#F43F5E) - Urgent, errors, alerts

#### Neutral Scale
- **White**: #FFFFFF
- **Gray 50**: #F9FAFB - Backgrounds
- **Gray 100**: #F3F4F6 - Subtle backgrounds
- **Gray 200**: #E5E7EB - Borders, dividers
- **Gray 300**: #D1D5DB - Disabled states
- **Gray 400**: #9CA3AF - Placeholder text
- **Gray 500**: #6B7280 - Secondary text
- **Gray 600**: #4B5563 - Body text
- **Gray 700**: #374151 - Headings
- **Gray 800**: #1F2937 - Dark mode text
- **Gray 900**: #111827 - Dark mode headings
- **Black**: #000000

### Typography

#### Font Family
- **Primary**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono (for code/numbers)

#### Type Scale
- **Display XL**: 72px / 80px (4.5rem / 5rem)
- **Display LG**: 60px / 68px (3.75rem / 4.25rem)
- **Display MD**: 48px / 56px (3rem / 3.5rem)
- **Display SM**: 36px / 44px (2.25rem / 2.75rem)
- **Heading XL**: 30px / 38px (1.875rem / 2.375rem)
- **Heading LG**: 24px / 32px (1.5rem / 2rem)
- **Heading MD**: 20px / 28px (1.25rem / 1.75rem)
- **Heading SM**: 18px / 26px (1.125rem / 1.625rem)
- **Body XL**: 20px / 30px (1.25rem / 1.875rem)
- **Body LG**: 18px / 28px (1.125rem / 1.75rem)
- **Body MD**: 16px / 24px (1rem / 1.5rem)
- **Body SM**: 14px / 20px (0.875rem / 1.25rem)
- **Body XS**: 12px / 16px (0.75rem / 1rem)
- **Label**: 12px / 16px (0.75rem / 1rem)
- **Caption**: 11px / 14px (0.6875rem / 0.875rem)

### Spacing Scale
- **0**: 0px
- **1**: 4px (0.25rem)
- **2**: 8px (0.5rem)
- **3**: 12px (0.75rem)
- **4**: 16px (1rem)
- **5**: 20px (1.25rem)
- **6**: 24px (1.5rem)
- **8**: 32px (2rem)
- **10**: 40px (2.5rem)
- **12**: 48px (3rem)
- **16**: 64px (4rem)
- **20**: 80px (5rem)
- **24**: 96px (6rem)

### Border Radius
- **None**: 0px
- **SM**: 4px (0.25rem)
- **MD**: 8px (0.5rem)
- **LG**: 12px (0.75rem)
- **XL**: 16px (1rem)
- **2XL**: 24px (1.5rem)
- **Full**: 9999px

### Shadows & Elevation

#### Light Mode
- **Shadow XS**: 0 1px 2px 0 rgb(0 0 0 / 0.05)
- **Shadow SM**: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
- **Shadow MD**: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
- **Shadow LG**: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
- **Shadow XL**: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
- **Shadow 2XL**: 0 25px 50px -12px rgb(0 0 0 / 0.25)

#### Glow Effects (for interactive elements)
- **Glow Primary**: 0 0 0 3px rgba(37, 99, 235, 0.1)
- **Glow Success**: 0 0 0 3px rgba(16, 185, 129, 0.1)
- **Glow Warning**: 0 0 0 3px rgba(245, 158, 11, 0.1)
- **Glow Danger**: 0 0 0 3px rgba(244, 63, 94, 0.1)

### Animation & Transitions

#### Timing Functions
- **Ease In Out**: cubic-bezier(0.4, 0, 0.2, 1)
- **Ease Out**: cubic-bezier(0, 0, 0.2, 1)
- **Ease In**: cubic-bezier(0.4, 0, 1, 1)

#### Durations
- **Instant**: 0ms
- **Fast**: 150ms
- **Normal**: 300ms
- **Slow**: 500ms
- **Very Slow**: 700ms

### Component Specifications

#### Buttons
- **Primary**: Solid background with hover/focus states
- **Secondary**: Outline with subtle background
- **Ghost**: Text-only with hover background
- **Danger**: Red variant for destructive actions
- **Loading States**: Spinner with disabled interaction
- **Icon Support**: Left/right positioning

#### Cards
- **Base**: White background with subtle shadow
- **Hover**: Elevation increase with smooth transition
- **Interactive**: Pointer cursor with active states
- **Variants**: Stats cards, data cards, action cards

#### Inputs
- **Base**: Clean borders with focus glow
- **Focus**: Primary glow effect
- **Error**: Red border with message
- **Success**: Green border for valid inputs
- **Disabled**: Grayed out with reduced opacity

#### Data Visualization
- **Charts**: Clean lines, subtle gradients
- **Stats**: Large numbers with clear labels
- **Progress**: Smooth animations with color coding
- **Trend Indicators**: Clear up/down arrows with colors

### Layout Grid System
- **Base Grid**: 12-column responsive grid
- **Gutters**: 24px on desktop, 16px on mobile
- **Breakpoints**: 
  - Mobile: 0-640px
  - Tablet: 641-1024px
  - Desktop: 1025px+
- **Container Widths**: 
  - Mobile: 100%
  - Tablet: 100%
  - Desktop: 1280px max

### Micro-interactions
- **Button Press**: Subtle scale transform
- **Card Hover**: Shadow elevation + slight scale
- **Menu Items**: Background fade-in
- **Form Focus**: Border glow animation
- **Loading**: Smooth spinner rotation
- **Toast Notifications**: Slide-in animation

### Accessibility Standards
- **Color Contrast**: Minimum 4.5:1 for normal text
- **Focus States**: Clear visible outlines
- **Keyboard Navigation**: Full support
- **Screen Readers**: ARIA labels and roles
- **Reduced Motion**: Respect user preferences

### Implementation Notes
1. All colors defined in Tailwind config
2. Typography scale mapped to Tailwind classes
3. Spacing system using Tailwind's default scale
4. Component variants using clsx for conditional classes
5. CSS transitions for smooth animations
6. Responsive design with mobile-first approach