// ============================================
// KRONOS UI COMPONENTS - ENHANCED BADGE
// ============================================

import { clsx } from 'clsx';
import { ReactNode } from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'accent' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  dot?: boolean;
  icon?: React.ReactNode;
  className?: string;
}

export function Badge({ 
  children, 
  variant = 'default', 
  size = 'sm',
  rounded = 'full',
  dot = false,
  icon,
  className 
}: BadgeProps) {
  const variants = {
    default: 'badge-gray',
    primary: 'badge-primary',
    secondary: 'badge-secondary',
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
    accent: 'badge-accent',
    outline: 'badge bg-transparent border border-gray-300 text-gray-700',
  };

  const sizes = {
    xs: 'px-2 py-0.5 text-[10px]',
    sm: 'px-2.5 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const roundedStyles = {
    sm: 'rounded',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };

  return (
    <span className={clsx(
      'badge',
      variants[variant],
      sizes[size],
      roundedStyles[rounded],
      'inline-flex items-center gap-1.5',
      className
    )}>
      {dot && (
        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
      )}
      {icon && (
        <span className="flex-shrink-0">
          {icon}
        </span>
      )}
      <span className="truncate">
        {children}
      </span>
    </span>
  );
}

export interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'pending' | 'completed' | 'cancelled' | 'draft';
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const statusConfig = {
    active: {
      variant: 'success' as const,
      label: 'Active',
      dot: true,
    },
    inactive: {
      variant: 'default' as const,
      label: 'Inactive',
      dot: true,
    },
    pending: {
      variant: 'warning' as const,
      label: 'Pending',
      dot: true,
    },
    completed: {
      variant: 'success' as const,
      label: 'Completed',
      dot: false,
    },
    cancelled: {
      variant: 'danger' as const,
      label: 'Cancelled',
      dot: false,
    },
    draft: {
      variant: 'default' as const,
      label: 'Draft',
      dot: false,
    },
  };

  const config = statusConfig[status];

  return (
    <Badge 
      variant={config.variant} 
      dot={config.dot}
      className={className}
    >
      {config.label}
    </Badge>
  );
}

export interface PriorityBadgeProps {
  priority: 'low' | 'medium' | 'high' | 'urgent';
  className?: string;
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  const priorityConfig = {
    low: {
      variant: 'default' as const,
      label: 'Low',
    },
    medium: {
      variant: 'primary' as const,
      label: 'Medium',
    },
    high: {
      variant: 'warning' as const,
      label: 'High',
    },
    urgent: {
      variant: 'danger' as const,
      label: 'Urgent',
      dot: true,
    },
  };

  const config = priorityConfig[priority];

  return (
    <Badge 
      variant={config.variant} 
      dot={config.dot}
      className={className}
    >
      {config.label}
    </Badge>
  );
}

export interface CountBadgeProps {
  count: number;
  max?: number;
  variant?: BadgeProps['variant'];
  className?: string;
}

export function CountBadge({ 
  count, 
  max = 99, 
  variant = 'primary',
  className 
}: CountBadgeProps) {
  const displayCount = count > max ? `${max}+` : count;
  
  return (
    <Badge 
      variant={variant}
      size="xs"
      className={clsx('font-semibold', className)}
    >
      {displayCount}
    </Badge>
  );
}

export interface NotificationBadgeProps {
  count?: number;
  dot?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  children: React.ReactNode;
}

export function NotificationBadge({ 
  count, 
  dot = false,
  position = 'top-right',
  children 
}: NotificationBadgeProps) {
  const positionClasses = {
    'top-right': 'top-0 right-0 -mt-1 -mr-1',
    'top-left': 'top-0 left-0 -mt-1 -ml-1',
    'bottom-right': 'bottom-0 right-0 -mb-1 -mr-1',
    'bottom-left': 'bottom-0 left-0 -mb-1 -ml-1',
  };

  const showBadge = count !== undefined && count > 0;

  return (
    <div className="relative inline-flex">
      {children}
      {(showBadge || dot) && (
        <span className={clsx(
          'absolute',
          positionClasses[position],
          dot 
            ? 'w-2.5 h-2.5 bg-danger-500 rounded-full border-2 border-white'
            : 'px-1.5 min-w-[20px] h-5 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center font-semibold border-2 border-white'
        )}>
          {!dot && count}
        </span>
      )}
    </div>
  );
}