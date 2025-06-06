
import { useState, useEffect } from 'react';
import { AppSidebar } from '../../components/AppSidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { SimpleTankStatus } from '../../components/dashboard/SimpleTankStatus';
import { Barn } from '../../types/dashboard';

const fetchTanksData = async (dairyId: string) => {
  // Mock data for now - this would be replaced with actual API call
  const barn: Barn = {
    id: 1,
    name: "Milky Way Dairy",
    producerId: "633",
    location: { lat: 33.4484, lng: -112.0740 },
    tanks: [
      // Same tanks as in DairyDashboard
      // ... data would go here
    ]
  };
  
  return barn;
};

export default function TanksPage() {
  const [barn, setBarn] = useState<Barn | null>(null);
  const [loading, setLoading] = useState(true);

  // In real implementation, get dairy ID from authentication
  const dairyId = "633"; // Milky Way dairy ID

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchTanksData(dairyId);
        setBarn(data);
      } catch (error) {
        console.error('Failed to load tanks data:', error);
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
                  Tank Management
                </h1>
                <p className="text-slate-600 text-base md:text-lg font-medium">
                  Monitor and manage your dairy tanks
                </p>
              </div>
              <SidebarTrigger />
            </div>

            {/* Main content */}
            <div className="bg-white rounded-2xl shadow-xl p-4 md:p-6">
              <p className="text-lg text-slate-700 mb-4">
                This page will show detailed tank management features. Coming soon!
              </p>
              
              {!loading && barn && (
                <SimpleTankStatus tanks={barn.tanks} />
              )}
            </div>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
