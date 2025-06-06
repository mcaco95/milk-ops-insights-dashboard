
import { useState, useEffect } from 'react';
import { AppSidebar } from '../../components/AppSidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { RoutesWidget } from '../../components/dashboard/RoutesWidget';
import { RouteRecord } from '../../types/dashboard';

const fetchRoutesData = async (dairyId: string) => {
  // Mock data for now - this would be replaced with actual API call
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
    }
    // Additional routes would be here
  ];
  
  return routes;
};

export default function RoutesPage() {
  const [routes, setRoutes] = useState<RouteRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // In real implementation, get dairy ID from authentication
  const dairyId = "633"; // Milky Way dairy ID

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchRoutesData(dairyId);
        setRoutes(data);
      } catch (error) {
        console.error('Failed to load routes data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [dairyId]);

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <AppSidebar />
        <SidebarInset>
          <div className="container mx-auto p-4 md:p-6">
            {/* Header with sidebar toggle */}
            <div className="flex items-center justify-between mb-6 md:mb-8">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-2 md:mb-3 tracking-tight">
                  Pickup Routes
                </h1>
                <p className="text-slate-600 text-base md:text-lg font-medium">
                  Track milk collection routes
                </p>
              </div>
              <SidebarTrigger />
            </div>

            {/* Main content */}
            <div className="bg-white rounded-2xl shadow-xl p-4 md:p-6">
              <p className="text-lg text-slate-700 mb-4">
                This page will provide detailed route tracking. Coming soon!
              </p>
              
              {!loading && (
                <RoutesWidget routes={routes} />
              )}
            </div>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
