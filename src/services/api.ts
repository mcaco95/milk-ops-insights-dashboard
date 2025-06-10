import { DashboardResponse, VolumesResponse, RoutesResponse, TanksResponse, PickupLogsResponse } from '../types/api';
import { AdminDairiesResponse } from '../types/auth';

class ApiService {
  private baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  private useMocks = import.meta.env.VITE_USE_MOCKS === 'true';

  private getHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
  
  private async fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    return fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: this.getHeaders(),
    });
  }

  async login(username: string, password: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    return this.handleResponse<any>(response);
  }

  async getDashboard(dairyId: string): Promise<DashboardResponse> {
    if (this.useMocks) return this.getMockDashboard();
    const response = await this.fetchWithAuth(`/api/dashboard/${dairyId}`);
    return this.handleResponse<DashboardResponse>(response);
  }

  async getVolumes(dairyId: string, month: string): Promise<VolumesResponse> {
    if (this.useMocks) return this.getMockVolumes();
    const response = await this.fetchWithAuth(`/api/volumes/${dairyId}?month=${month}`);
    return this.handleResponse<VolumesResponse>(response);
  }

  async getPickupLogs(dairyId: string, month: string): Promise<PickupLogsResponse> {
    const response = await this.fetchWithAuth(`/api/pickup-logs/${dairyId}?month=${month}`);
    return this.handleResponse<PickupLogsResponse>(response);
  }

  async getRoutes(dairyId: string): Promise<RoutesResponse> {
    const response = await this.fetchWithAuth(`/api/routes/${dairyId}/today`);
    return this.handleResponse<RoutesResponse>(response);
  }

  async getTanks(dairyId: string): Promise<TanksResponse> {
    const response = await this.fetchWithAuth(`/api/tanks/${dairyId}`);
    return this.handleResponse<TanksResponse>(response);
  }
  
  async getAllDairies(): Promise<AdminDairiesResponse> {
      const response = await this.fetchWithAuth('/api/admin/dairies');
      return this.handleResponse<AdminDairiesResponse>(response);
  }

  // MOCK DATA
  private getMockDashboard(): DashboardResponse {
    return { total_tanks: 10, tanks_full: 2, active_routes: 3, monthly_volume: 1234567, capacity_utilization: 85, critical_alerts: 1 };
  }
  
  private getMockVolumes(): VolumesResponse {
    return {
      month: '2023-05',
      total_volume: 1234567,
      total_pickup_count: 15,
      volumes: [
        { customer: 'Fairlife', volume: 500000, pickup_count: 5 },
        { customer: 'UDA', volume: 400000, pickup_count: 4 },
        { customer: 'Schreiber', volume: 334567, pickup_count: 6 },
      ],
    };
  }
}

export const apiService = new ApiService(); 