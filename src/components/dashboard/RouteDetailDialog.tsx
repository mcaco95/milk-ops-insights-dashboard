
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Clock, MapPin, Truck } from "lucide-react";
import { RouteRecord } from "../../types/dashboard";
import { formatTime } from "../../utils/formatters";

interface RouteDetailDialogProps {
  route: RouteRecord | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const RouteDetailDialog = ({ route, open, onOpenChange }: RouteDetailDialogProps) => {
  if (!route) return null;

  const getStatusBadge = (status: RouteRecord['status']) => {
    const styles = {
      active: 'bg-green-100 text-green-800 border-green-200',
      closed: 'bg-gray-100 text-gray-600 border-gray-200'
    };

    return (
      <Badge className={`${styles[status]} border`}>
        {status}
      </Badge>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Truck size={20} />
            Route {route.routeNumber} Details
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 pt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Start Time</label>
              <p className="text-sm text-gray-900">{formatTime(route.startTime)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <div className="mt-1">{getStatusBadge(route.status)}</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Dairy</label>
              <p className="text-sm text-gray-900">{route.dairy}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Tank</label>
              <p className="text-sm text-gray-900">{route.tank}</p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">LT Number</label>
            <p className="text-sm font-mono text-gray-900">{route.ltNumber}</p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">Invoice Number</label>
            <p className="text-sm font-mono text-gray-900">{route.invoiceNumber}</p>
          </div>

          {route.status === 'active' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">ETA</label>
                <div className="flex items-center space-x-1 mt-1">
                  <Clock size={12} className="text-green-500" />
                  <span className="text-sm text-gray-900">{route.eta}</span>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Tracking</label>
                <a 
                  href={route.trackingUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 transition-colors mt-1"
                >
                  <MapPin size={14} />
                  <ExternalLink size={12} />
                  <span className="text-sm">Track</span>
                </a>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
