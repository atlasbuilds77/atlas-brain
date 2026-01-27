// ============================================
// KRONOS UI COMPONENTS - ENHANCED BUTTON
// ============================================

import { forwardRef } from 'react';
import { clsx } from 'clsx';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'danger' | 'success' | 'ghost' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'md', 
    loading, 
    icon,
    iconPosition = 'left',
    fullWidth,
    rounded = 'lg',
    shadow = 'sm',
    children, 
    disabled,
    ...props 
  }, ref) => {
    const variants = {
      primary: 'btn-primary',
      secondary: 'btn-secondary',
      accent: 'btn-accent',
      danger: 'btn-danger',
      success: 'btn-success',
      ghost: 'btn-ghost',
      outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 active:bg-primary-100 focus:ring-primary-500',
    };

    const sizes = {
      xs: 'px-2.5 py-1.5 text-xs',
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-2.5 text-sm',
      lg: 'px-5 py-3 text-base',
      xl: 'px-6 py-3.5 text-base',
    };

    const roundedStyles = {
      sm: 'rounded',
      md: 'rounded-lg',
      lg: 'rounded-xl',
      full: 'rounded-full',
    };

    const shadowStyles = {
      none: '',
      sm: 'shadow-sm',
      md: 'shadow',
      lg: 'shadow-md',
    };

    return (
      <button
        ref={ref}
        className={clsx(
          'btn',
          variants[variant],
          sizes[size],
          roundedStyles[rounded],
          shadowStyles[shadow],
          fullWidth && 'w-full',
          loading && 'relative !text-transparent',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <svg 
              className="animate-spin h-4 w-4" 
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle 
                className="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4"
                fill="none"
              />
              <path 
                className="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        )}
        
        {!loading && icon && iconPosition === 'left' && (
          <span className="flex-shrink-0">{icon}</span>
        )}
        
        <span className={clsx(
          'truncate',
          loading && 'opacity-0'
        )}>
          {children}
        </span>
        
        {!loading && icon && iconPosition === 'right' && (
          <span className="flex-shrink-0">{icon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

// Icon Button Variant
export interface IconButtonProps extends Omit<ButtonProps, 'children'> {
  icon: React.ReactNode;
  label: string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, label, size = 'md', className, ...props }, ref) => {
    const sizes = {
      xs: 'p-1.5',
      sm: 'p-2',
      md: 'p-2.5',
      lg: 'p-3',
      xl: 'p-3.5',
    };

    return (
      <Button
        ref={ref}
        size={size}
        className={clsx(
          sizes[size],
          '!p-0 aspect-square',
          className
        )}
        aria-label={label}
        {...props}
      >
        <span className="flex items-center justify-center">
          {icon}
        </span>
      </Button>
    );
  }
);

IconButton.displayName = 'IconButton';

// Button Group Component
interface ButtonGroupProps {
  children: React.ReactNode;
  className?: string;
}

export const ButtonGroup = ({ children, className }: ButtonGroupProps) => {
  return (
    <div className={clsx(
      'inline-flex rounded-lg overflow-hidden border border-gray-200 divide-x divide-gray-200',
      className
    )}>
      {children}
    </div>
  );
};

// Split Button Component
interface SplitButtonProps {
  mainAction: React.ReactNode;
  dropdownAction: React.ReactNode;
  className?: string;
}

export const SplitButton = ({ mainAction, dropdownAction, className }: SplitButtonProps) => {
  return (
    <div className={clsx('inline-flex rounded-lg overflow-hidden', className)}>
      {mainAction}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 w-px bg-gray-300" />
        {dropdownAction}
      </div>
    </div>
  );
};