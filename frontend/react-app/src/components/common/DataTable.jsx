import React from 'react';
import './DataTable.css';

/**
 * Professional Data Table Component
 * Clean, modern table for displaying structured data
 */
const DataTable = ({ 
    columns, 
    data, 
    onRowClick,
    hoverable = true,
    compact = false
}) => {
    return (
        <div className="data-table-container">
            <table className={`data-table ${compact ? 'data-table-compact' : ''} ${hoverable ? 'data-table-hoverable' : ''}`}>
                <thead>
                    <tr>
                        {columns.map((column, idx) => (
                            <th 
                                key={idx}
                                style={{ 
                                    textAlign: column.align || 'left',
                                    width: column.width || 'auto'
                                }}
                            >
                                {column.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, rowIdx) => (
                        <tr 
                            key={rowIdx}
                            onClick={() => onRowClick && onRowClick(row)}
                            style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                        >
                            {columns.map((column, colIdx) => (
                                <td 
                                    key={colIdx}
                                    style={{ textAlign: column.align || 'left' }}
                                >
                                    {column.render 
                                        ? column.render(row[column.key], row) 
                                        : row[column.key]
                                    }
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default DataTable;
