
import { DashboardResponse, VolumesResponse, RoutesResponse, TanksResponse } from '../types/api';

class ApiService {
  private isDemo(): boolean {
    return localStorage.getItem('demo_mode') === 'true';
  }

  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, redirect to login
        localStorage.clear();
        window.location.href = '/login';
        throw new Error('Session expired');
      }
      throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
  }

  private getMockDashboard(): DashboardResponse {
    return {
      total_tanks: 8,
      tanks_full: 3,
      active_routes: 5,
      monthly_volume: 125420,
      capacity_utilization: 78,
      critical_alerts: 1
    };
  }

  private getMockVolumes(month?: string): VolumesResponse {
    const currentMonth = month || new Date().toISOString().substring(0, 7);
    const volumes = Array.from({ length: 15 }, (_, i) => ({
      date: `${currentMonth}-${String(i + 1).padStart(2, '0')}`,
      volume: Math.floor(Math.random() * 5000) + 3000,
      pickups: Math.floor(Math.random() * 3) + 1,
      customer: ['Farm Fresh Co.', 'Valley Dairy', 'Mountain Creamery', 'Organic Plus'][Math.floor(Math.random() * 4)]
    }));

    return {
      month: currentMonth,
      total_volume: volumes.reduce((sum, v) => sum + v.volume, 0),
      total_pickups: volumes.reduce((sum, v) => sum + v.pickups, 0),
      volumes
    };
  }

  private getMockRoutes(): RoutesResponse {
    const statuses: ('scheduled' | 'active' | 'completed')[] = ['scheduled', 'active', 'completed'];
    const drivers = ['Mike Johnson', 'Sarah Smith', 'Tom Wilson', 'Lisa Brown'];
    const trucks = ['TR-001', 'TR-002', 'TR-003', 'TR-004'];
    
    const routes = Array.from({ length: 6 }, (_, i) => ({
      id: i + 1,
      route_number: `R-${String(i + 1).padStart(3, '0')}`,
      driver_name: drivers[i % drivers.length],
      truck_id: trucks[i % trucks.length],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      estimated_arrival: new Date(Date.now() + (i + 1) * 3600000).toISOString(),
      tank_number: `Tank-${i + 1}`,
      current_location: {
        lat: 40.7128 + (Math.random() - 0.5) * 0.1,
        lng: -74.0060 + (Math.random() - 0.5) * 0.1
      }
    }));

    return {
      date: new Date().toISOString().split('T')[0],
      routes
    };
  }

  private getMockTanks(): TanksResponse {
    const statuses: ('normal' | 'warning' | 'critical')[] = ['normal', 'warning', 'critical'];
    
    const tanks = Array.from({ length: 8 }, (_, i) => {
      const capacity = 5000 + Math.floor(Math.random() * 3000);
      const fillPercentage = Math.floor(Math.random() * 100);
      const currentVolume = Math.floor(capacity * fillPercentage / 100);
      
      return {
        id: i + 1,
        name: `Tank ${i + 1}`,
        current_volume: currentVolume,
        capacity,
        fill_percentage: fillPercentage,
        status: fillPercentage > 90 ? 'critical' : fillPercentage > 75 ? 'warning' : 'normal',
        last_pickup: new Date(Date.now() - Math.random() * 86400000 * 3).toISOString(),
        estimated_full: new Date(Date.now() + Math.random() * 86400000 * 2).toISOString()
      };
    });

    return {
      dairy_id: 'demo-dairy-001',
      tanks
    };
  }

  async getDashboard(dairyId: string): Promise<DashboardResponse> {
    if (this.isDemo()) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      return this.getMockDashboard();
    }

    const response = await fetch(`/api/dashboard/${dairyId}`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<DashboardResponse>(response);
  }

  async getVolumes(dairyId: string, month?: string): Promise<VolumesResponse> {
    if (this.isDemo()) {
      await new Promise(resolve => setTimeout(resolve, 300));
      return this.getMockVolumes(month);
    }

    const monthParam = month || new Date().toISOString().substring(0, 7);
    const response = await fetch(`/api/volumes/${dairyId}?month=${monthParam}`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<VolumesResponse>(response);
  }

  async getRoutes(dairyId: string): Promise<RoutesResponse> {
    if (this.isDemo()) {
      await new Promise(resolve => setTimeout(resolve, 400));
      return this.getMockRoutes();
    }

    const response = await fetch(`/api/routes/${dairyId}/today`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<RoutesResponse>(response);
  }

  async getTanks(dairyId: string): Promise<TanksResponse> {
    if (this.isDemo()) {
      await new Promise(resolve => setTimeout(resolve, 600));
      return this.getMockTanks();
    }

    const response = await fetch(`/api/tanks/${dairyId}`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<TanksResponse>(response);
  }
}

export const apiService = new ApiService();
