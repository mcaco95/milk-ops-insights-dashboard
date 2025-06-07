
import { useState, useEffect } from 'react';
import { DairyLayout } from '../../components/dairy/DairyLayout';
import { Truck, Clock, Phone, MapPin } from 'lucide-react';
import { RouteRecord } from '../../types/dashboard';
import { Button } from '@/components/ui/button';

const fetchRouteData = async () => {
  // Mock data - in real app would fetch from API
  const routes: RouteRecord[] = [
    {
      startTime: "2025-06-05T12:00:00Z",
      routeNumber: 74,
      dairy: "Milky Way (633)",
      tank: 2,
      ltNumber: "LMH32001",
      invoiceNumber: "10175359",
      status: "active",
      eta: "7:28",
      trackingUrl: "https://track.example.com/LMH32001",
      driverName: "Maria Rodriguez",
      vehicleId: "VEH-015",
      currentLocation: {
        lat: 33.4584,
        lng: -112.0840,
        speed: 65,
        timestamp: "2025-06-05T14:32:00Z"
      }
    },
    {
      startTime: "2025-06-05T08:00:00Z",
      routeNumber: 73,
      dairy: "Milky Way (633)",
      tank: 1,
      ltNumber: "LMH32002",
      invoiceNumber: "10175358",
      status: "completed",
      eta: "Completed",
      trackingUrl: "https://track.example.com/LMH32002",
      driverName: "John Smith",
      vehicleId: "VEH-012"
    }
  ];
  return routes;
};

const RouteCard = ({ route }: { route: RouteRecord }) => {
  const isActive = route.status === 'active';
  
  return (
    <div className={`p-4 rounded-lg border-2 mb-4 ${
      isActive 
        ? 'bg-blue-50 border-blue-200' 
        : 'bg-gray-50 border-gray-200'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <Truck size={20} className={isActive ? 'text-blue-600' : 'text-gray-600'} />
          <h3 className="text-lg font-semibold text-slate-800 ml-2">
            Route #{route.routeNumber}
          </h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          isActive 
            ? 'bg-blue-100 text-blue-700' 
            : 'bg-green-100 text-green-700'
        }`}>
          {isActive ? 'In Progress' : 'Completed'}
        </span>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-slate-600">Driver:</span>
          <span className="text-slate-800 font-medium">{route.driverName}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-600">Truck:</span>
          <span className="text-slate-800">{route.ltNumber}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-600">Tank:</span>
          <span className="text-slate-800">Tank {route.tank}</span>
        </div>

        {isActive && (
          <>
            <div className="flex items-center justify-between">
              <span className="text-slate-600 flex items-center">
                <Clock size={16} className="mr-1" />
                ETA:
              </span>
              <span className="text-lg font-semibold text-blue-600">{route.eta}</span>
            </div>

            {route.currentLocation && (
              <div className="flex items-center justify-between">
                <span className="text-slate-600 flex items-center">
                  <MapPin size={16} className="mr-1" />
                  Speed:
                </span>
                <span className="text-slate-800">{route.currentLocation.speed} mph</span>
              </div>
            )}

            <div className="pt-3 border-t border-slate-200 flex space-x-3">
              <Button size="sm" className="flex-1">
                <Phone size={16} className="mr-2" />
                Call Driver
              </Button>
              <Button size="sm" variant="outline" className="flex-1">
                Track Truck
              </Button>
            </div>
          </>
        )}

        {!isActive && (
          <div className="pt-2 border-t border-slate-200">
            <span className="text-sm text-slate-600">
              Completed: {new Date(route.startTime).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

const RoutesPage = () => {
  const [routes, setRoutes] = useState<RouteRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchRouteData();
        setRoutes(data);
      } catch (error) {
        console.error('Failed to load route data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 10000); // Update every 10 seconds for live tracking
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <DairyLayout>
        <div className="flex items-center justify-center min-h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading routes...</p>
          </div>
        </div>
      </DairyLayout>
    );
  }

  const activeRoutes = routes.filter(route => route.status === 'active');
  const completedRoutes = routes.filter(route => route.status === 'completed');

  return (
    <DairyLayout>
      <div className="p-4 pb-20 md:pb-4">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">Milk Pickups</h1>
          <p className="text-slate-600">Track your milk collection routes</p>
        </div>

        {activeRoutes.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Active Pickups</h2>
            {activeRoutes.map((route) => (
              <RouteCard key={route.routeNumber} route={route} />
            ))}
          </div>
        )}

        {completedRoutes.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Recent Pickups</h2>
            {completedRoutes.map((route) => (
              <RouteCard key={route.routeNumber} route={route} />
            ))}
          </div>
        )}

        {routes.length === 0 && (
          <div className="text-center py-12">
            <Truck size={48} className="text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-600 mb-2">No pickups scheduled</h3>
            <p className="text-slate-500">Your milk pickup routes will appear here</p>
          </div>
        )}
      </div>
    </DairyLayout>
  );
};

export default RoutesPage;
