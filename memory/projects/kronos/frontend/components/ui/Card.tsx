// ============================================
// KRONOS UI COMPONENTS - ENHANCED CARD
// ============================================

import { clsx } from 'clsx';
import { ReactNode } from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  border?: boolean;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  gradient?: 'primary' | 'success' | 'warning' | 'danger' | 'accent';
  glass?: boolean;
}

export function Card({ 
  children, 
  className, 
  hover = true, 
  padding = 'md',
  shadow = 'md',
  border = true,
  rounded = 'xl',
  gradient,
  glass = false,
}: CardProps) {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-10',
  };

  const shadows = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  };

  const roundedStyles = {
    none: 'rounded-none',
    sm: 'rounded-lg',
    md: 'rounded-xl',
    lg: 'rounded-2xl',
    xl: 'rounded-3xl',
    '2xl': 'rounded-[2rem]',
  };

  const gradients = {
    primary: 'gradient-primary',
    success: 'gradient-success',
    warning: 'gradient-warning',
    danger: 'gradient-danger',
    accent: 'gradient-accent',
  };

  return (
    <div
      className={clsx(
        'card',
        paddings[padding],
        shadows[shadow],
        roundedStyles[rounded],
        border && 'border border-gray-200',
        hover && 'card-hover',
        gradient && gradients[gradient],
        glass && 'glass',
        gradient && 'text-white',
        className
      )}
    >
      {children}
    </div>
  );
}

export interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
}

export function CardHeader({ 
  title, 
  subtitle, 
  action, 
  className, 
  icon,
  badge,
}: CardHeaderProps) {
  return (
    <div className={clsx('flex items-start justify-between', className)}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex-shrink-0">
              {icon}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {title}
              </h3>
              {badge && (
                <div className="flex-shrink-0">
                  {badge}
                </div>
              )}
            </div>
            {subtitle && (
              <p className="mt-1 text-sm text-gray-500">
                {subtitle}
              </p>
            )}
          </div>
        </div>
      </div>
      {action && (
        <div className="flex-shrink-0 ml-4">
          {action}
        </div>
      )}
    </div>
  );
}

export interface CardContentProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function CardContent({ 
  children, 
  className,
  padding = 'md',
}: CardContentProps) {
  const paddings = {
    none: '',
    sm: 'px-4 py-2',
    md: 'px-6 py-4',
    lg: 'px-8 py-6',
  };

  return (
    <div className={clsx(paddings[padding], className)}>
      {children}
    </div>
  );
}

export interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right' | 'between';
}

export function CardFooter({ 
  children, 
  className,
  align = 'right',
}: CardFooterProps) {
  const alignments = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
    between: 'justify-between',
  };

  return (
    <div className={clsx(
      'px-6 py-4 border-t border-gray-200',
      alignments[align],
      'flex items-center gap-3',
      className
    )}>
      {children}
    </div>
  );
}

export interface StatsCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  iconBg?: string;
  trend?: 'up' | 'down' | 'neutral';
  loading?: boolean;
  format?: 'number' | 'currency' | 'percentage';
}

export function StatsCard({ 
  title, 
  value, 
  change, 
  changeLabel, 
  icon, 
  iconBg = 'bg-primary-100',
  trend = 'neutral',
  loading = false,
  format = 'number',
}: StatsCardProps) {
  const trendColors = {
    up: 'text-success-600',
    down: 'text-danger-600',
    neutral: 'text-gray-600',
  };

  const trendIcons = {
    up: '↗',
    down: '↘',
    neutral: '→',
  };

  const formatValue = (val: string | number) => {
    if (format === 'currency') {
      return typeof val === 'number' ? `$${val.toLocaleString()}` : val;
    }
    if (format === 'percentage') {
      return typeof val === 'number' ? `${val}%` : val;
    }
    return val;
  };

  return (
    <Card className="stats-card">
      <div className="flex items-center gap-4">
        {icon && (
          <div className={clsx(
            'stats-card-icon',
            iconBg,
            loading && 'skeleton'
          )}>
            {!loading && icon}
          </div>
        )}
        
        <div className="flex-1 min-w-0">
          <p className={clsx(
            'stats-card-label',
            loading && 'skeleton skeleton-text w-20'
          )}>
            {!loading && title}
          </p>
          
          <p className={clsx(
            'stats-card-value',
            loading && 'skeleton skeleton-text w-32 mt-3'
          )}>
            {!loading && formatValue(value)}
          </p>
          
          {change !== undefined && !loading && (
            <p className={clsx(
              'stats-card-change',
              trendColors[trend]
            )}>
              <span className="font-semibold">
                {trendIcons[trend]} {Math.abs(change)}%
              </span>
              {changeLabel && (
                <span className="text-gray-500 ml-1">
                  {changeLabel}
                </span>
              )}
            </p>
          )}
          
          {loading && change === undefined && (
            <div className="mt-2 skeleton skeleton-text w-24" />
          )}
        </div>
      </div>
    </Card>
  );
}

export interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'accent';
  size?: 'sm' | 'md' | 'lg';
}

export function MetricCard({
  title,
  value,
  description,
  icon,
  color = 'primary',
  size = 'md',
}: MetricCardProps) {
  const colorClasses = {
    primary: 'bg-primary-50 border-primary-200 text-primary-700',
    success: 'bg-success-50 border-success-200 text-success-700',
    warning: 'bg-warning-50 border-warning-200 text-warning-700',
    danger: 'bg-danger-50 border-danger-200 text-danger-700',
    accent: 'bg-accent-50 border-accent-200 text-accent-700',
  };

  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <Card className={clsx(
      sizeClasses[size],
      'border-2',
      colorClasses[color]
    )}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">
            {title}
          </p>
          <p className="text-2xl font-bold mt-1">
            {value}
          </p>
          {description && (
            <p className="text-sm opacity-70 mt-2">
              {description}
            </p>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

export interface EmptyStateCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: React.ReactNode;
}

export function EmptyStateCard({
  title,
  description,
  icon,
  action,
}: EmptyStateCardProps) {
  return (
    <Card className="text-center py-12">
      <div className="empty-state">
        <div className="empty-state-icon mx-auto">
          {icon}
        </div>
        <h3 className="empty-state-title mt-4">
          {title}
        </h3>
        <p className="empty-state-description">
          {description}
        </p>
        {action && (
          <div className="mt-6">
            {action}
          </div>
        )}
      </div>
    </Card>
  );
}