
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
          color.includes('emerald') ? 'from-emerald-100 to-emerald-200' :
          color.includes('green') ? 'from-green-100 to-green-200' :
          'from-teal-100 to-teal-200'} flex items-center justify-center`}>
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
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="font-medium">Live Updates</span>
        </div>
      </div>

      <div className={`grid ${isMobile ? 'grid-cols-2' : 'grid-cols-2 lg:grid-cols-4'} gap-4`}>
        <StatCard
          icon={Droplets}
          title="Total Tanks"
          value={barn.tanks.length}
          subtitle="Active monitoring"
          color="text-emerald-600"
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
          color="text-teal-600"
        />
      </div>

      {/* Tank Status Grid */}
      <div className={`${isMobile ? 'mt-3 pt-3' : 'mt-6 pt-6'} border-t border-slate-200/60`}>
        <h3 className={`${isMobile ? 'text-sm' : 'text-base'} font-semibold text-slate-700 mb-3`}>
          Tank Status by Barn
        </h3>
        <div className={`grid ${isMobile ? 'grid-cols-1' : 'grid-cols-3'} gap-3`}>
          {[1, 2, 3].map(barnNum => {
            const barnTanks = barn.tanks.filter(tank => tank.name.includes(`Barn ${barnNum}`));
            const barnWashNeeded = barnTanks.filter(tank => tank.washAlertStatus !== 'ok').length;
            
            return (
              <div key={barnNum} className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                <div className="flex items-center justify-between mb-2">
                  <span className={`${isMobile ? 'text-sm' : 'text-base'} font-medium text-slate-700`}>
                    Barn {barnNum}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    barnWashNeeded > 0 ? 'bg-orange-100 text-orange-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    {barnTanks.length} tanks
                  </span>
                </div>
                <div className="flex space-x-1">
                  {barnTanks.map(tank => (
                    <div
                      key={tank.id}
                      className={`flex-1 h-2 rounded-full ${
                        tank.washAlertStatus === 'critical' ? 'bg-red-400' :
                        tank.washAlertStatus === 'warning' ? 'bg-orange-400' :
                        'bg-emerald-400'
                      }`}
                      title={`${tank.name}: ${tank.washAlertStatus}`}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
