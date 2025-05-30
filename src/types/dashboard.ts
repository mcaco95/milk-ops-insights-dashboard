
export type Tank = {
  id: number;
  name: string;
  currentVolume: number;
  predictedVolume: number;
  superLoadsAvailable: number;
  lastHit: string;
};

export type CustomerSummary = {
  customer: string;
  totalWeight: number;
  invoiceCount: number;
};

export type RouteRecord = {
  startTime: string;
  routeNumber: number;
  dairy: string;
  tank: number;
  ltNumber: string;
  invoiceNumber: string;
  status: 'active' | 'closed';
  eta: string;
  trackingUrl: string;
};
