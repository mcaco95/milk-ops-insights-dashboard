
import { AlertTriangle, Droplets, Clock, TrendingUp } from 'lucide-react';
import { Barn } from '../../types/dashboard';
import { useIsMobile } from '../../hooks/useMobile';
import { formatNumber } from '../../utils/formatters';

interface DairyOverviewWidgetProps {
  barn: Barn;
}

export const DairyOverviewWidget = ({ barn }: DairyOverviewWidgetProps) => {
  const isMobile = useIsMobile();

  const tanksNeedingWash = barn.tanks.filter(tank => tank.washAlertStatus !== 'ok').length;
  const criticalTanks = barn.tanks.filter(tank => tank.washAlertStatus === 'critical').length;
  const totalVolume = barn.tanks.reduce((sum, tank) => sum + tank.currentVolume, 0);
  const totalCapacity = barn.tanks.reduce((sum, tank) => sum + tank.capacity, 0);
  const capacityUtilization = Math.round((totalVolume / totalCapacity) * 100);

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
          color.includes('blue') ? 'from-blue-100 to-blue-200' :
          'from-green-100 to-green-200'} flex items-center justify-center`}>
          <Icon size={isMobile ? 16 : 20} className={color} />
        </div>
      </div>
    </div>
  );

  return (
    <div className={`bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-xl border border-slate-200/50 ${
      isMobile ? 'p-4' : 'p-6'
    } backdrop-blur-sm`}>
      <div className={`flex items-center justify-between ${isMobile ? 'mb-3' : 'mb-6'}`}>
        <h2 className={`${isMobile ? 'text-lg' : 'text-xl'} font-bold text-slate-800 tracking-tight`}>
          Your Dairy Overview
        </h2>
        <div className="flex items-center space-x-2 text-sm text-slate-600">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="font-medium">Live Updates</span>
        </div>
      </div>

      <div className={`grid ${isMobile ? 'grid-cols-2' : 'grid-cols-2 lg:grid-cols-4'} gap-4`}>
        <StatCard
          icon={Droplets}
          title="Total Tanks"
          value={barn.tanks.length}
          subtitle="Active monitoring"
          color="text-blue-600"
        />
        
        <StatCard
          icon={AlertTriangle}
          title="Wash Needed"
          value={tanksNeedingWash}
          subtitle={criticalTanks > 0 ? `${criticalTanks} critical` : 'All monitored'}
          color="text-orange-600"
          urgent={criticalTanks > 0}
        />
        
        <StatCard
          icon={TrendingUp}
          title="Capacity"
          value={`${capacityUtilization}%`}
          subtitle="Current utilization"
          color="text-green-600"
        />
        
        <StatCard
          icon={Clock}
          title="Current Volume"
          value={`${formatNumber(totalVolume)}L`}
          subtitle={`of ${formatNumber(totalCapacity)}L`}
          color="text-purple-600"
        />
      </div>

      {/* Priority Actions Section - Much clearer than color bars */}
      <div className={`${isMobile ? 'mt-3 pt-3' : 'mt-6 pt-6'} border-t border-slate-200/60`}>
        <h3 className={`${isMobile ? 'text-sm' : 'text-base'} font-semibold text-slate-700 mb-3`}>
          Priority Actions
        </h3>
        
        {criticalTanks > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <div>
                <p className="font-semibold text-red-700">URGENT: Tanks Need Wash</p>
                <p className="text-sm text-red-600">
                  {criticalTanks} tank{criticalTanks > 1 ? 's' : ''} need immediate attention
                </p>
              </div>
            </div>
          </div>
        )}
        
        {tanksNeedingWash > criticalTanks && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-3">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-orange-500" />
              <div>
                <p className="font-semibold text-orange-700">Schedule Wash Soon</p>
                <p className="text-sm text-orange-600">
                  {tanksNeedingWash - criticalTanks} tank{tanksNeedingWash - criticalTanks > 1 ? 's' : ''} need washing within 24 hours
                </p>
              </div>
            </div>
          </div>
        )}
        
        {tanksNeedingWash === 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <div className="h-5 w-5 rounded-full bg-green-500 flex items-center justify-center">
                <div className="h-2 w-2 bg-white rounded-full"></div>
              </div>
              <div>
                <p className="font-semibold text-green-700">All Tanks OK</p>
                <p className="text-sm text-green-600">No immediate action needed</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
