
import { DashboardResponse, VolumesResponse, RoutesResponse, TanksResponse } from '../types/api';

class ApiService {
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

  async getDashboard(dairyId: string): Promise<DashboardResponse> {
    const response = await fetch(`/api/dashboard/${dairyId}`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<DashboardResponse>(response);
  }

  async getVolumes(dairyId: string, month?: string): Promise<VolumesResponse> {
    const monthParam = month || new Date().toISOString().substring(0, 7);
    const response = await fetch(`/api/volumes/${dairyId}?month=${monthParam}`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<VolumesResponse>(response);
  }

  async getRoutes(dairyId: string): Promise<RoutesResponse> {
    const response = await fetch(`/api/routes/${dairyId}/today`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<RoutesResponse>(response);
  }

  async getTanks(dairyId: string): Promise<TanksResponse> {
    const response = await fetch(`/api/tanks/${dairyId}`, {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<TanksResponse>(response);
  }
}

export const apiService = new ApiService();
