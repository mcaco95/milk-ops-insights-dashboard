
import { AlertTriangle, Droplets, Truck, TrendingUp } from 'lucide-react';
import { DashboardSummary } from '../../types/dashboard';
import { useIsMobile } from '../../hooks/useMobile';
import { formatNumber } from '../../utils/formatters';

interface DashboardSummaryWidgetProps {
  summary: DashboardSummary;
}

export const DashboardSummaryWidget = ({ summary }: DashboardSummaryWidgetProps) => {
  const isMobile = useIsMobile();

  const StatCard = ({ 
    icon: Icon, 
    title, 
    value, 
    subtitle, 
    color, 
    urgent = false 
  }: {
    icon: any;
    title: string;
    value: string | number;
    subtitle?: string;
    color: string;
    urgent?: boolean;
  }) => (
    <div className={`bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg border border-slate-200/50 ${
      isMobile ? 'p-3' : 'p-4'
    } backdrop-blur-sm ${urgent ? 'ring-2 ring-red-200' : ''}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600 font-medium mb-1`}>
            {title}
          </p>
          <p className={`${isMobile ? 'text-lg' : 'text-2xl'} font-bold ${color} tracking-tight`}>
            {typeof value === 'number' ? formatNumber(value) : value}
          </p>
          {subtitle && (
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-500 mt-1`}>
              {subtitle}
            </p>
          )}
        </div>
        <div className={`${isMobile ? 'w-8 h-8' : 'w-12 h-12'} rounded-lg bg-gradient-to-br ${color.includes('red') ? 'from-red-100 to-red-200' : 
          color.includes('orange') ? 'from-orange-100 to-orange-200' :
          color.includes('emerald') ? 'from-emerald-100 to-emerald-200' :
          'from-green-100 to-green-200'} flex items-center justify-center`}>
          <Icon size={isMobile ? 16 : 20} className={color} />
        </div>
      </div>
    </div>
  );

  return (
    <div className={`bg-gradient-to-br from-slate-50 to-emerald-50 rounded-2xl shadow-xl border border-slate-200/50 ${
      isMobile ? 'p-4' : 'p-6'
    } backdrop-blur-sm`}>
      <div className={`flex items-center justify-between ${isMobile ? 'mb-3' : 'mb-6'}`}>
        <h2 className={`${isMobile ? 'text-lg' : 'text-xl'} font-bold text-slate-800 tracking-tight`}>
          Operations Overview
        </h2>
        <div className="flex items-center space-x-2 text-sm text-slate-600">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="font-medium">Live Updates</span>
        </div>
      </div>

      <div className={`grid ${isMobile ? 'grid-cols-2' : 'grid-cols-2 lg:grid-cols-4'} gap-4`}>
        <StatCard
          icon={Droplets}
          title="Total Dairies"
          value={summary.totalDairies}
          subtitle="Active locations"
          color="text-emerald-600"
        />
        
        <StatCard
          icon={AlertTriangle}
          title="Wash Alerts"
          value={summary.tanksNeedingWash}
          subtitle={`${summary.criticalAlerts} critical`}
          color="text-orange-600"
          urgent={summary.criticalAlerts > 0}
        />
        
        <StatCard
          icon={Truck}
          title="Active Routes"
          value={summary.activeRoutes}
          subtitle="Live tracking"
          color="text-green-600"
        />
        
        <StatCard
          icon={TrendingUp}
          title="Capacity Avg"
          value={`${summary.averageCapacityUtilization}%`}
          subtitle="Utilization"
          color="text-teal-600"
        />
      </div>

      {/* Monthly Summary */}
      <div className={`${isMobile ? 'mt-3 pt-3' : 'mt-6 pt-6'} border-t border-slate-200/60`}>
        <div className={`grid ${isMobile ? 'grid-cols-2' : 'grid-cols-2'} gap-4`}>
          <div className="text-center">
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600 font-medium mb-1`}>
              Monthly Volume
            </p>
            <p className={`${isMobile ? 'text-lg' : 'text-xl'} font-bold text-emerald-700`}>
              {formatNumber(summary.totalMonthlyVolume)}
            </p>
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-500`}>
              units (June 2025)
            </p>
          </div>
          <div className="text-center">
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600 font-medium mb-1`}>
              Total Pickups
            </p>
            <p className={`${isMobile ? 'text-lg' : 'text-xl'} font-bold text-green-700`}>
              {summary.totalMonthlyPickups}
            </p>
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-500`}>
              deliveries
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
