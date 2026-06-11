import React from 'react';

export interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
  /** Additional Tailwind classes */
  className?: string;
}

export const Table: React.FC<TableProps> = ({ children, className = '', ...props }) => (
  <div className="overflow-x-auto rounded-md shadow-sm border border-slate-200">
    <table className={`min-w-full divide-y divide-slate-200 ${className}`} {...props}>
      {children}
    </table>
  </div>
);

export interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  className?: string;
}

export const TableHeader: React.FC<TableHeaderProps> = ({ children, className = '', ...props }) => (
  <thead className={`bg-slate-50 ${className}`} {...props}>
    {children}
  </thead>
);

export interface TableBodyProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  className?: string;
}

export const TableBody: React.FC<TableBodyProps> = ({ children, className = '', ...props }) => (
  <tbody className={className} {...props}>
    {children}
  </tbody>
);

export interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  className?: string;
}

export const TableRow: React.FC<TableRowProps> = ({ children, className = '', ...props }) => (
  <tr className={`border-b border-slate-200 hover:bg-slate-50 ${className}`} {...props}>
    {children}
  </tr>
);

export interface TableCellProps extends React.TdHTMLAttributes<HTMLTableDataCellElement> {
  className?: string;
}

export const TableCell: React.FC<TableCellProps> = ({ children, className = '', ...props }) => (
  <td className={`px-4 py-2 text-sm text-slate-700 ${className}`} {...props}>
    {children}
  </td>
);

export interface TableHeadProps extends React.ThHTMLAttributes<HTMLTableHeaderCellElement> {
  className?: string;
}

export const TableHead: React.FC<TableHeadProps> = ({ children, className = '', ...props }) => (
  <th className={`px-4 py-2 text-left text-sm font-medium text-slate-900 ${className}`} {...props}>
    {children}
  </th>
);
