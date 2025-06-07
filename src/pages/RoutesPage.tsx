
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { RoutesResponse } from '../types/api';
import { formatDateTime } from '../utils/formatters';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Button } from '../components/ui/button';

const RoutesPage = () => {
  const [data, setData] = useState<RoutesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchData = async () => {
    if (!user?.dairy_id) return;
    
    try {
      const routesData = await apiService.getRoutes(user.dairy_id);
      setData(routesData);
      setError(null);
    } catch (err) {
      setError('Failed to load routes data');
      console.error('Routes fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [user?.dairy_id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-emerald-100 text-emerald-800';
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleMapClick = (route: any) => {
    // Future enhancement - Google Maps integration
    alert(`Map feature coming soon! Route ${route.route_number} with ${route.driver_name}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-emerald-200 border-t-emerald-600 mx-auto mb-4"></div>
          <p className="text-slate-700 font-medium">Loading routes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-green-100">
      <div className="container mx-auto p-4 md:p-6">
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-emerald-800 bg-clip-text text-transparent mb-2">
            Live Routes
          </h1>
          <p className="text-slate-600 text-lg">
            Real-time tracking of today's pickup routes
          </p>
        </div>

        {/* Routes Table */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 overflow-hidden">
          <div className="p-6 border-b border-slate-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">
              Today's Routes
            </h2>
            <div className="text-sm text-slate-500">
              Auto-refreshes every 30 seconds
            </div>
          </div>
          
          {error ? (
            <div className="p-6 text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Try Again
              </button>
            </div>
          ) : data && data.routes.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-24">Route #</TableHead>
                    <TableHead className="min-w-32">Driver</TableHead>
                    <TableHead className="min-w-24">Truck ID</TableHead>
                    <TableHead className="min-w-24">Tank</TableHead>
                    <TableHead className="min-w-20">Status</TableHead>
                    <TableHead className="min-w-32">ETA</TableHead>
                    <TableHead className="min-w-20">Map</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.routes.map((route) => (
                    <TableRow key={route.id}>
                      <TableCell className="font-medium">
                        {route.route_number}
                      </TableCell>
                      <TableCell>
                        {route.driver_name}
                      </TableCell>
                      <TableCell>
                        {route.truck_id}
                      </TableCell>
                      <TableCell>
                        Tank {route.tank_number}
                      </TableCell>
                      <TableCell>
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(route.status)}`}>
                          {route.status.charAt(0).toUpperCase() + route.status.slice(1)}
                        </span>
                      </TableCell>
                      <TableCell>
                        {formatDateTime(route.estimated_arrival)}
                      </TableCell>
                      <TableCell>
                        <Button
                          onClick={() => handleMapClick(route)}
                          variant="outline"
                          size="sm"
                          className="h-8 text-xs"
                        >
                          Map
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="p-6 text-center text-slate-500">
              No routes scheduled for today
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoutesPage;
