// ============================================
// KRONOS UI COMPONENTS - ENHANCED INPUT
// ============================================

import { forwardRef, useState } from 'react';
import { clsx } from 'clsx';
import { Eye, EyeOff, AlertCircle, CheckCircle, Search, X } from 'lucide-react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  inputSize?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'filled' | 'outlined';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className,
    label,
    error,
    success,
    hint,
    leftIcon,
    rightIcon,
    fullWidth,
    type = 'text',
    inputSize = 'md',
    variant = 'default',
    disabled,
    ...props 
  }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === 'password';
    const inputType = isPassword && showPassword ? 'text' : type;

    const sizes = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-2.5 text-sm',
      lg: 'px-5 py-3 text-base',
    };

    const variants = {
      default: 'input',
      filled: 'bg-gray-100 border-gray-100 focus:bg-white focus:border-primary-500',
      outlined: 'bg-transparent border-2 border-gray-300 focus:border-primary-500',
    };

    return (
      <div className={clsx(fullWidth && 'w-full')}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}
          
          <input
            ref={ref}
            type={inputType}
            disabled={disabled}
            className={clsx(
              variants[variant],
              sizes[inputSize],
              leftIcon && 'pl-10',
              (rightIcon || isPassword || error || success) && 'pr-10',
              error && 'input-error',
              success && 'input-success',
              disabled && 'opacity-50 cursor-not-allowed bg-gray-50',
              className
            )}
            {...props}
          />
          
          {/* Right side icons */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
            {error && (
              <AlertCircle className="w-4 h-4 text-danger-500" />
            )}
            {success && !error && (
              <CheckCircle className="w-4 h-4 text-success-500" />
            )}
            {isPassword && (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            )}
            {rightIcon && !error && !success && !isPassword && rightIcon}
          </div>
        </div>
        
        {/* Helper text */}
        {(hint || error || success) && (
          <div className="mt-1.5">
            {error && (
              <p className="text-sm text-danger-600 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" />
                {error}
              </p>
            )}
            {success && !error && (
              <p className="text-sm text-success-600 flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" />
                {success}
              </p>
            )}
            {hint && !error && !success && (
              <p className="text-sm text-gray-500">
                {hint}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Search Input Component
export interface SearchInputProps extends Omit<InputProps, 'leftIcon' | 'rightIcon'> {
  onClear?: () => void;
  showClearButton?: boolean;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ 
    onClear,
    showClearButton = true,
    value,
    ...props 
  }, ref) => {
    const handleClear = () => {
      if (onClear) {
        onClear();
      }
    };

    return (
      <Input
        ref={ref}
        type="search"
        value={value}
        leftIcon={<Search className="w-4 h-4" />}
        rightIcon={
          showClearButton && value ? (
            <button
              type="button"
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          ) : undefined
        }
        {...props}
      />
    );
  }
);

SearchInput.displayName = 'SearchInput';

// Textarea Component
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  success?: string;
  hint?: string;
  fullWidth?: boolean;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ 
    className,
    label,
    error,
    success,
    hint,
    fullWidth,
    resize = 'vertical',
    disabled,
    ...props 
  }, ref) => {
    const resizeClasses = {
      none: 'resize-none',
      vertical: 'resize-y',
      horizontal: 'resize-x',
      both: 'resize',
    };

    return (
      <div className={clsx(fullWidth && 'w-full')}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        
        <textarea
          ref={ref}
          disabled={disabled}
          className={clsx(
            'input min-h-[100px]',
            resizeClasses[resize],
            error && 'input-error',
            success && 'input-success',
            disabled && 'opacity-50 cursor-not-allowed bg-gray-50',
            className
          )}
          {...props}
        />
        
        {/* Helper text */}
        {(hint || error || success) && (
          <div className="mt-1.5">
            {error && (
              <p className="text-sm text-danger-600 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" />
                {error}
              </p>
            )}
            {success && !error && (
              <p className="text-sm text-success-600 flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" />
                {success}
              </p>
            )}
            {hint && !error && !success && (
              <p className="text-sm text-gray-500">
                {hint}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

// Select Component
export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  fullWidth?: boolean;
  options: Array<{ value: string; label: string; disabled?: boolean }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    className,
    label,
    error,
    hint,
    fullWidth,
    options,
    disabled,
    ...props 
  }, ref) => {
    return (
      <div className={clsx(fullWidth && 'w-full')}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        
        <select
          ref={ref}
          disabled={disabled}
          className={clsx(
            'input appearance-none cursor-pointer',
            'bg-[url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 20 20\'%3E%3Cpath stroke=\'%236b7280\' stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'1.5\' d=\'m6 8 4 4 4-4\'/%3E%3C/svg%3E")] bg-[length:1.25rem] bg-[right_0.5rem_center] bg-no-repeat pr-10',
            error && 'input-error',
            disabled && 'opacity-50 cursor-not-allowed bg-gray-50',
            className
          )}
          {...props}
        >
          {options.map((option) => (
            <option 
              key={option.value} 
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        {/* Helper text */}
        {(hint || error) && (
          <div className="mt-1.5">
            {error && (
              <p className="text-sm text-danger-600 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" />
                {error}
              </p>
            )}
            {hint && !error && (
              <p className="text-sm text-gray-500">
                {hint}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';