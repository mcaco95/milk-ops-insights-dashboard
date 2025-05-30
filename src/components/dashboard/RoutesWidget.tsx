
import { useState } from 'react';
import { ExternalLink, Clock, MapPin, Eye } from 'lucide-react';
import { RouteRecord } from '../../types/dashboard';
import { formatTime } from '../../utils/formatters';
import { useIsMobile } from '../../hooks/useMobile';
import { RouteDetailDialog } from './RouteDetailDialog';

interface RoutesWidgetProps {
  routes: RouteRecord[];
}

export const RoutesWidget = ({ routes }: RoutesWidgetProps) => {
  const [sortField, setSortField] = useState<keyof RouteRecord>('startTime');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedRoute, setSelectedRoute] = useState<RouteRecord | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const isMobile = useIsMobile();

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

  const handleMobileRowClick = (route: RouteRecord) => {
    setSelectedRoute(route);
    setDialogOpen(true);
  };

  const getStatusBadge = (status: RouteRecord['status']) => {
    const styles = {
      active: 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border-green-200',
      closed: 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-600 border-gray-200'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold border shadow-sm ${styles[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <>
      <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-2xl shadow-xl border border-slate-200/50 p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-800 tracking-tight">Today's Routes</h2>
          <div className="flex items-center space-x-2 text-sm text-slate-600">
            <Clock size={16} className="text-blue-500" />
            <span className="font-medium">Real-time updates</span>
          </div>
        </div>

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white/70 backdrop-blur-sm">
          {isMobile ? (
            // Mobile Layout - Condensed Cards
            <div className="divide-y divide-slate-100">
              {sortedRoutes.map((route, index) => (
                <div 
                  key={index} 
                  className="p-4 hover:bg-blue-50 transition-colors cursor-pointer active:bg-blue-100"
                  onClick={() => handleMobileRowClick(route)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-semibold text-slate-700">
                        {formatTime(route.startTime)}
                      </span>
                      <span className="text-lg font-bold text-blue-600">
                        {route.routeNumber}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {route.status === 'active' && (
                        <a 
                          href={route.trackingUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 transition-colors p-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MapPin size={16} />
                        </a>
                      )}
                      <Eye size={16} className="text-slate-400" />
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="space-y-1">
                      <div className="text-xs text-slate-600">
                        Invoice: <span className="font-mono font-medium">{route.invoiceNumber}</span>
                      </div>
                      {route.status === 'active' && (
                        <div className="flex items-center space-x-1 text-xs text-green-600">
                          <Clock size={10} />
                          <span>ETA: {route.eta}</span>
                        </div>
                      )}
                    </div>
                    {getStatusBadge(route.status)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            // Desktop Layout - Full Table
            <table className="w-full">
              <thead className="bg-gradient-to-r from-slate-100 to-blue-100 border-b border-slate-200">
                <tr>
                  <th 
                    className="text-left py-4 px-6 font-semibold text-slate-700 cursor-pointer hover:text-slate-900 transition-colors"
                    onClick={() => handleSort('startTime')}
                  >
                    Start Time
                  </th>
                  <th 
                    className="text-left py-4 px-6 font-semibold text-slate-700 cursor-pointer hover:text-slate-900 transition-colors"
                    onClick={() => handleSort('routeNumber')}
                  >
                    Route #
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-700">
                    Dairy (Tank)
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-700">
                    LT#
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-700">
                    Invoice#
                  </th>
                  <th 
                    className="text-left py-4 px-6 font-semibold text-slate-700 cursor-pointer hover:text-slate-900 transition-colors"
                    onClick={() => handleSort('status')}
                  >
                    Status
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-700">
                    ETA
                  </th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-700">
                    Track
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sortedRoutes.map((route, index) => (
                  <tr key={index} className="hover:bg-blue-50 transition-colors group">
                    <td className="py-4 px-6 text-sm font-medium text-slate-800">
                      {formatTime(route.startTime)}
                    </td>
                    <td className="py-4 px-6 text-sm font-bold text-blue-600 group-hover:text-blue-700">
                      {route.routeNumber}
                    </td>
                    <td className="py-4 px-6 text-sm text-slate-800 font-medium">
                      {route.dairy} ({route.tank})
                    </td>
                    <td className="py-4 px-6 text-sm font-mono text-slate-700 bg-slate-50 group-hover:bg-slate-100 transition-colors">
                      {route.ltNumber}
                    </td>
                    <td className="py-4 px-6 text-sm font-mono text-slate-700 bg-slate-50 group-hover:bg-slate-100 transition-colors">
                      {route.invoiceNumber}
                    </td>
                    <td className="py-4 px-6">
                      {getStatusBadge(route.status)}
                    </td>
                    <td className="py-4 px-6 text-sm text-slate-800">
                      {route.status === 'active' ? (
                        <div className="flex items-center space-x-2">
                          <Clock size={12} className="text-green-500" />
                          <span className="font-medium">{route.eta}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500 font-medium">closed</span>
                      )}
                    </td>
                    <td className="py-4 px-6">
                      {route.status === 'active' && (
                        <a 
                          href={route.trackingUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 transition-colors group"
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
          )}
        </div>
      </div>

      <RouteDetailDialog 
        route={selectedRoute}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </>
  );
};
