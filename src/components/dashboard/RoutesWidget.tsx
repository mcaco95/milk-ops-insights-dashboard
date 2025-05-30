
import { useState } from 'react';
import { ExternalLink, Clock, MapPin } from 'lucide-react';
import { RouteRecord } from '../../types/dashboard';
import { formatTime } from '../../utils/formatters';

interface RoutesWidgetProps {
  routes: RouteRecord[];
}

export const RoutesWidget = ({ routes }: RoutesWidgetProps) => {
  const [sortField, setSortField] = useState<keyof RouteRecord>('startTime');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const sortedRoutes = [...routes].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];
    
    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  const handleSort = (field: keyof RouteRecord) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getStatusBadge = (status: RouteRecord['status']) => {
    const styles = {
      active: 'bg-green-100 text-green-800 border-green-200',
      closed: 'bg-gray-100 text-gray-600 border-gray-200'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${styles[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Today's Routes</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock size={16} />
          <span>Real-time updates</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th 
                className="text-left py-3 px-4 font-medium text-gray-600 cursor-pointer hover:text-gray-900"
                onClick={() => handleSort('startTime')}
              >
                Start Time
              </th>
              <th 
                className="text-left py-3 px-4 font-medium text-gray-600 cursor-pointer hover:text-gray-900"
                onClick={() => handleSort('routeNumber')}
              >
                Route #
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-600">
                Dairy (Tank)
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-600">
                LT#
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-600">
                Invoice#
              </th>
              <th 
                className="text-left py-3 px-4 font-medium text-gray-600 cursor-pointer hover:text-gray-900"
                onClick={() => handleSort('status')}
              >
                Status
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-600">
                ETA
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-600">
                Track
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedRoutes.map((route, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-3 px-4 text-sm text-gray-900">
                  {formatTime(route.startTime)}
                </td>
                <td className="py-3 px-4 text-sm font-medium text-blue-600">
                  {route.routeNumber}
                </td>
                <td className="py-3 px-4 text-sm text-gray-900">
                  {route.dairy} ({route.tank})
                </td>
                <td className="py-3 px-4 text-sm font-mono text-gray-700">
                  {route.ltNumber}
                </td>
                <td className="py-3 px-4 text-sm font-mono text-gray-700">
                  {route.invoiceNumber}
                </td>
                <td className="py-3 px-4">
                  {getStatusBadge(route.status)}
                </td>
                <td className="py-3 px-4 text-sm text-gray-900">
                  {route.status === 'active' ? (
                    <div className="flex items-center space-x-1">
                      <Clock size={12} className="text-green-500" />
                      <span>{route.eta}</span>
                    </div>
                  ) : (
                    <span className="text-gray-500">closed</span>
                  )}
                </td>
                <td className="py-3 px-4">
                  {route.status === 'active' && (
                    <a 
                      href={route.trackingUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <MapPin size={14} />
                      <ExternalLink size={12} />
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
