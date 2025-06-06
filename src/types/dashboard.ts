
export type WashAlertStatus = 'ok' | 'warning' | 'critical';

export type Tank = {
  id: number;
  name: string;
  currentVolume: number;
  predictedVolume: number;
  superLoadsAvailable: number;
  lastHit: string;
  fillRate?: number; // gallons per hour
  washAlertStatus: WashAlertStatus;
  washAlertTime?: string; // when alert was triggered
  capacity: number; // actual tank capacity in liters
};

export type Barn = {
  id: number;
  name: string;
  producerId: string;
  tanks: Tank[];
  location?: {
    lat: number;
    lng: number;
  };
};

export type CustomerSummary = {
  customer: string;
  totalWeight: number;
  invoiceCount: number;
  marketShare: number; // percentage
};

export type GPSLocation = {
  lat: number;
  lng: number;
  speed: number;
  timestamp: string;
};

export type RouteRecord = {
  startTime: string;
  routeNumber: number;
  dairy: string;
  tank: number;
  ltNumber: string;
  invoiceNumber: string;
  status: 'active' | 'closed' | 'scheduled';
  eta: string;
  trackingUrl: string;
  driverName?: string;
  vehicleId?: string;
  currentLocation?: GPSLocation;
};

export type DashboardSummary = {
  totalDairies: number;
  tanksNeedingWash: number;
  criticalAlerts: number;
  averageCapacityUtilization: number;
  activeRoutes: number;
  totalMonthlyVolume: number;
  totalMonthlyPickups: number;
};

export type HandlerBreakdown = {
  handler: string;
  volume: number;
  marketShare: number;
  pickupCount: number;
};
