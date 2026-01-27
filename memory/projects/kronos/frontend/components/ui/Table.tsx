// ============================================
// KRONOS UI COMPONENTS - ENHANCED TABLE
// ============================================

import { clsx } from 'clsx';
import { ReactNode, useState } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown, MoreVertical } from 'lucide-react';

export interface TableProps {
  children: React.ReactNode;
  className?: string;
  striped?: boolean;
  hoverable?: boolean;
  bordered?: boolean;
}

export function Table({ 
  children, 
  className, 
  striped = false,
  hoverable = true,
  bordered = false,
}: TableProps) {
  return (
    <div className="table-container">
      <div className="overflow-x-auto">
        <table className={clsx(
          'table',
          bordered && 'border-separate border-spacing-0',
          className
        )}>
          {children}
        </table>
      </div>
    </div>
  );
}

export interface TableHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function TableHeader({ children, className }: TableHeaderProps) {
  return (
    <thead className={clsx('table-header', className)}>
      {children}
    </thead>
  );
}

export interface TableBodyProps {
  children: React.ReactNode;
  className?: string;
}

export function TableBody({ children, className }: TableBodyProps) {
  return (
    <tbody className={clsx('divide-y divide-gray-200', className)}>
      {children}
    </tbody>
  );
}

export interface TableRowProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  selected?: boolean;
}

export function TableRow({ children, className, onClick, selected }: TableRowProps) {
  return (
    <tr 
      className={clsx(
        'table-row',
        onClick && 'cursor-pointer',
        selected && 'bg-primary-50',
        className
      )}
      onClick={onClick}
    >
      {children}
    </tr>
  );
}

export interface TableHeadProps {
  children: React.ReactNode;
  className?: string;
  sortable?: boolean;
  sortDirection?: 'asc' | 'desc' | null;
  onSort?: () => void;
  align?: 'left' | 'center' | 'right';
}

export function TableHead({ 
  children, 
  className, 
  sortable,
  sortDirection,
  onSort,
  align = 'left',
}: TableHeadProps) {
  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  };

  return (
    <th className={clsx('table-header-cell', alignClasses[align], className)}>
      {sortable ? (
        <button
          onClick={onSort}
          className="flex items-center gap-2 hover:text-gray-700 transition-colors group"
        >
          <span>{children}</span>
          <span className="text-gray-400 group-hover:text-gray-600">
            {sortDirection === 'asc' && <ChevronUp className="w-4 h-4" />}
            {sortDirection === 'desc' && <ChevronDown className="w-4 h-4" />}
            {sortDirection === null && <ChevronsUpDown className="w-4 h-4" />}
          </span>
        </button>
      ) : (
        children
      )}
    </th>
  );
}

export interface TableCellProps {
  children: React.ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right';
  truncate?: boolean;
}

export function TableCell({ 
  children, 
  className, 
  align = 'left',
  truncate = false,
}: TableCellProps) {
  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  };

  return (
    <td className={clsx(
      'table-cell',
      alignClasses[align],
      truncate && 'max-w-xs truncate',
      className
    )}>
      {children}
    </td>
  );
}

// Table Footer
export interface TableFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function TableFooter({ children, className }: TableFooterProps) {
  return (
    <tfoot className={clsx('bg-gray-50 border-t border-gray-200', className)}>
      {children}
    </tfoot>
  );
}

// Empty State
export interface TableEmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  colSpan?: number;
}

export function TableEmptyState({ 
  title, 
  description, 
  icon,
  action,
  colSpan = 6,
}: TableEmptyStateProps) {
  return (
    <TableRow>
      <TableCell colSpan={colSpan} className="!py-16">
        <div className="text-center">
          {icon && (
            <div className="mx-auto w-12 h-12 text-gray-400 mb-4">
              {icon}
            </div>
          )}
          <h3 className="text-sm font-medium text-gray-900 mb-1">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-500 mb-4">
              {description}
            </p>
          )}
          {action && (
            <div className="mt-6">
              {action}
            </div>
          )}
        </div>
      </TableCell>
    </TableRow>
  );
}

// Loading State
export interface TableLoadingStateProps {
  rows?: number;
  cols?: number;
  colSpan?: number;
}

export function TableLoadingState({ 
  rows = 5, 
  cols = 4,
  colSpan,
}: TableLoadingStateProps) {
  if (colSpan) {
    return (
      <>
        {Array.from({ length: rows }).map((_, i) => (
          <TableRow key={i}>
            <TableCell colSpan={colSpan}>
              <div className="flex items-center gap-4">
                <div className="skeleton w-10 h-10 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="skeleton h-4 w-3/4" />
                  <div className="skeleton h-3 w-1/2" />
                </div>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </>
    );
  }

  return (
    <>
      {Array.from({ length: rows }).map((_, i) => (
        <TableRow key={i}>
          {Array.from({ length: cols }).map((_, j) => (
            <TableCell key={j}>
              <div className="skeleton h-4 w-full" />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </>
  );
}

// Action Cell (for dropdowns, etc.)
export interface TableActionCellProps {
  onEdit?: () => void;
  onDelete?: () => void;
  onView?: () => void;
  customActions?: Array<{
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
    variant?: 'default' | 'danger';
  }>;
}

export function TableActionCell({
  onEdit,
  onDelete,
  onView,
  customActions = [],
}: TableActionCellProps) {
  const [isOpen, setIsOpen] = useState(false);

  const actions = [
    ...(onView ? [{ label: 'View', onClick: onView, variant: 'default' as const }] : []),
    ...(onEdit ? [{ label: 'Edit', onClick: onEdit, variant: 'default' as const }] : []),
    ...customActions,
    ...(onDelete ? [{ label: 'Delete', onClick: onDelete, variant: 'danger' as const }] : []),
  ];

  return (
    <TableCell align="right">
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
          aria-label="Actions"
        >
          <MoreVertical className="w-4 h-4 text-gray-500" />
        </button>

        {isOpen && (
          <>
            <div 
              className="fixed inset-0 z-10" 
              onClick={() => setIsOpen(false)}
            />
            <div className="absolute right-0 mt-2 w-48 dropdown z-20">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => {
                    action.onClick();
                    setIsOpen(false);
                  }}
                  className={clsx(
                    'dropdown-item flex items-center gap-3 w-full',
                    action.variant === 'danger' && 'text-danger-600 hover:bg-danger-50'
                  )}
                >
                  {action.icon}
                  {action.label}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </TableCell>
  );
}

// Pagination Component
export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  itemsPerPage?: number;
  totalItems?: number;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  itemsPerPage,
  totalItems,
}: PaginationProps) {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);
  
  // Show only 7 page numbers at a time
  const getVisiblePages = () => {
    if (totalPages <= 7) return pages;
    
    if (currentPage <= 3) {
      return [...pages.slice(0, 5), '...', totalPages];
    }
    
    if (currentPage >= totalPages - 2) {
      return [1, '...', ...pages.slice(totalPages - 5)];
    }
    
    return [
      1,
      '...',
      currentPage - 1,
      currentPage,
      currentPage + 1,
      '...',
      totalPages,
    ];
  };

  return (
    <div className="px-6 py-4 border-t border-gray-200 bg-white flex items-center justify-between">
      <div className="text-sm text-gray-700">
        {itemsPerPage && totalItems && (
          <p>
            Showing <span className="font-medium">{((currentPage - 1) * itemsPerPage) + 1}</span> to{' '}
            <span className="font-medium">
              {Math.min(currentPage * itemsPerPage, totalItems)}
            </span> of{' '}
            <span className="font-medium">{totalItems}</span> results
          </p>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>

        <div className="flex items-center gap-1">
          {getVisiblePages().map((page, index) => (
            <button
              key={index}
              onClick={() => typeof page === 'number' && onPageChange(page)}
              disabled={page === '...'}
              className={clsx(
                'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                page === currentPage
                  ? 'bg-primary-600 text-white'
                  : page === '...'
                  ? 'text-gray-400 cursor-default'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
              )}
            >
              {page}
            </button>
          ))}
        </div>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}