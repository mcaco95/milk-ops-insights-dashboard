
export interface DashboardResponse {
  total_tanks: number;
  tanks_full: number;
  active_routes: number;
  monthly_volume: number;
  capacity_utilization: number;
  critical_alerts: number;
}

export interface VolumeData {
  date: string;
  volume: number;
  pickups: number;
  customer: string;
}

export interface VolumesResponse {
  month: string;
  total_volume: number;
  total_pickups: number;
  volumes: VolumeData[];
}

export interface RouteData {
  id: number;
  route_number: string;
  driver_name: string;
  truck_id: string;
  status: 'scheduled' | 'active' | 'completed';
  estimated_arrival: string;
  tank_number: string;
  current_location?: {
    lat: number;
    lng: number;
  };
}

export interface RoutesResponse {
  date: string;
  routes: RouteData[];
}

export interface TankData {
  id: number;
  name: string;
  current_volume: number;
  capacity: number;
  fill_percentage: number;
  status: 'normal' | 'warning' | 'critical';
  last_pickup: string;
  estimated_full: string;
}

export interface TanksResponse {
  dairy_id: string;
  tanks: TankData[];
}
