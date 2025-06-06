
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { AlertTriangle, Droplets } from 'lucide-react';
import { Barn } from '../../types/dashboard';
import { formatNumber, formatMobileDateTime } from '../../utils/formatters';
import { useIsMobile } from '../../hooks/useMobile';

interface VolumeWidgetProps {
  barns: Barn[];
}

export const VolumeWidget = ({ barns }: VolumeWidgetProps) => {
  const [activeBarn, setActiveBarn] = useState(barns[0]?.id.toString() || "1");
  const isMobile = useIsMobile();

  const calculateTimeToFull = (currentVolume: number, predictedVolume: number, fillRate?: number): string => {
    if (!fillRate || currentVolume >= predictedVolume) return '';
    
    const remainingVolume = predictedVolume - currentVolume;
    const hoursToFull = remainingVolume / fillRate;
    
    if (hoursToFull < 1) {
      return `${Math.round(hoursToFull * 60)}m`;
    } else if (hoursToFull < 24) {
      const hours = Math.floor(hoursToFull);
      const minutes = Math.round((hoursToFull - hours) * 60);
      return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
    } else {
      const days = Math.floor(hoursToFull / 24);
      const hours = Math.round(hoursToFull % 24);
      return hours > 0 ? `${days}d ${hours}h` : `${days}d`;
    }
  };

  const getWashAlertColor = (status: string): string => {
    switch (status) {
      case 'critical': return '#dc2626'; // red-600
      case 'warning': return '#ea580c'; // orange-600
      default: return '#1e40af'; // blue-700
    }
  };

  // Custom tick component to show tank name and ETA
  const CustomXAxisTick = (props: any) => {
    const { x, y, payload } = props;
    const chartData = props.chartData;
    const tankData = chartData.find((item: any) => item.name === payload.value);
    
    return (
      <g transform={`translate(${x},${y})`}>
        <text 
          x={0} 
          y={0} 
          dy={16} 
          textAnchor="middle" 
          fill="#475569" 
          fontSize={isMobile ? 8 : 12}
          fontWeight={500}
        >
          {payload.value}
        </text>
        {tankData?.timeToFull && (
          <text 
            x={0} 
            y={0} 
            dy={isMobile ? 28 : 32} 
            textAnchor="middle" 
            fill={getWashAlertColor(tankData.washStatus)}
            fontSize={isMobile ? 8 : 10}
            fontWeight={600}
          >
            ETA: {tankData.timeToFull}
          </text>
        )}
      </g>
    );
  };

  const BarnChart = ({ barn }: { barn: Barn }) => {
    const chartData = barn.tanks.map(tank => ({
      name: tank.name,
      current: tank.currentVolume,
      predicted: tank.predictedVolume - tank.currentVolume,
      fillPercentage: (tank.currentVolume / tank.predictedVolume) * 100,
      timeToFull: calculateTimeToFull(tank.currentVolume, tank.predictedVolume, tank.fillRate),
      washStatus: tank.washAlertStatus,
      capacity: tank.capacity
    }));

    const totalSuperLoads = barn.tanks.reduce((sum, tank) => sum + tank.superLoadsAvailable, 0);
    const lastHit = barn.tanks.reduce((latest, tank) => 
      new Date(tank.lastHit) > new Date(latest) ? tank.lastHit : latest, 
      barn.tanks[0]?.lastHit || ''
    );

    const alertsCount = barn.tanks.filter(tank => tank.washAlertStatus !== 'ok').length;
    const criticalCount = barn.tanks.filter(tank => tank.washAlertStatus === 'critical').length;

    return (
      <div className={`${isMobile ? 'mb-3' : ''}`}>
        {isMobile && (
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-slate-800">{barn.name}</h3>
            {alertsCount > 0 && (
              <div className="flex items-center space-x-1">
                <AlertTriangle size={12} className={criticalCount > 0 ? 'text-red-500' : 'text-orange-500'} />
                <span className={`text-xs font-medium ${criticalCount > 0 ? 'text-red-600' : 'text-orange-600'}`}>
                  {alertsCount} alert{alertsCount > 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>
        )}
        
        <div className={`${isMobile ? 'h-40' : 'h-72'} ${isMobile ? 'mb-2' : 'mb-6'}`}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={chartData} 
              margin={isMobile ? { top: 5, right: 10, left: 5, bottom: 40 } : { top: 10, right: 30, left: 20, bottom: 50 }}
            >
              <defs>
                <linearGradient id="currentGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#1e40af" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
                <linearGradient id="predictedGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#93c5fd" />
                  <stop offset="100%" stopColor="#bfdbfe" />
                </linearGradient>
                {/* Wash alert gradients */}
                <linearGradient id="criticalGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#dc2626" />
                  <stop offset="100%" stopColor="#ef4444" />
                </linearGradient>
                <linearGradient id="warningGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ea580c" />
                  <stop offset="100%" stopColor="#f97316" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.6} />
              <XAxis 
                dataKey="name" 
                axisLine={false}
                tickLine={false}
                tick={(props) => <CustomXAxisTick {...props} chartData={chartData} />}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#475569', fontSize: isMobile ? 8 : 12 }}
                tickFormatter={(value) => formatNumber(value)}
              />
              <Bar dataKey="current" stackId="a" radius={[0, 0, 8, 8]}>
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-current-${index}`} 
                    fill={entry.washStatus === 'critical' ? 'url(#criticalGradient)' : 
                          entry.washStatus === 'warning' ? 'url(#warningGradient)' : 
                          'url(#currentGradient)'}
                  />
                ))}
              </Bar>
              <Bar dataKey="predicted" stackId="a" radius={[8, 8, 0, 0]} fill="url(#predictedGradient)">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-predicted-${index}`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className={`grid grid-cols-2 gap-2 ${isMobile ? 'pt-1' : 'pt-4'} border-t border-slate-200/60`}>
          <div className={`text-center bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg ${isMobile ? 'p-1.5' : 'p-3'} border border-blue-100`}>
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600 mb-1 font-medium`}>Super Loads</p>
            <p className={`${isMobile ? 'text-base' : 'text-2xl'} font-bold text-blue-700`}>{totalSuperLoads.toFixed(2)}</p>
          </div>
          <div className={`text-center bg-gradient-to-r from-slate-50 to-gray-50 rounded-lg ${isMobile ? 'p-1.5' : 'p-3'} border border-slate-100`}>
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600 mb-1 font-medium`}>Last Hit</p>
            <p className={`${isMobile ? 'text-xs' : 'text-sm'} font-semibold text-slate-800`}>
              {formatMobileDateTime(lastHit)}
            </p>
          </div>
        </div>

        {/* Wash Alert Summary */}
        {!isMobile && alertsCount > 0 && (
          <div className="mt-4 p-3 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200">
            <div className="flex items-center space-x-2">
              <AlertTriangle size={16} className={criticalCount > 0 ? 'text-red-500' : 'text-orange-500'} />
              <span className={`text-sm font-medium ${criticalCount > 0 ? 'text-red-600' : 'text-orange-600'}`}>
                {alertsCount} tank{alertsCount > 1 ? 's' : ''} need{alertsCount === 1 ? 's' : ''} wash
                {criticalCount > 0 && ` (${criticalCount} critical)`}
              </span>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`bg-gradient-to-br from-slate-50 to-blue-50 rounded-2xl shadow-xl border border-slate-200/50 ${isMobile ? 'p-3' : 'p-6'} h-full backdrop-blur-sm`}>
      <div className={`flex items-center justify-between ${isMobile ? 'mb-2' : 'mb-6'}`}>
        <div className="flex items-center space-x-2">
          <Droplets size={isMobile ? 16 : 20} className="text-blue-600" />
          <h2 className={`${isMobile ? 'text-base' : 'text-xl'} font-bold text-slate-800 tracking-tight`}>
            Volume & Wash Status
          </h2>
        </div>
        <div className={`flex ${isMobile ? 'flex-col space-y-1' : 'items-center space-x-4'} ${isMobile ? 'text-xs' : 'text-sm'} text-slate-600`}>
          <div className="flex items-center">
            <div className={`${isMobile ? 'w-1.5 h-1.5' : 'w-3 h-3'} bg-gradient-to-r from-blue-600 to-blue-700 rounded-full ${isMobile ? 'mr-1' : 'mr-2'} shadow-sm`}></div>
            Normal
          </div>
          <div className="flex items-center">
            <div className={`${isMobile ? 'w-1.5 h-1.5' : 'w-3 h-3'} bg-gradient-to-r from-orange-600 to-orange-700 rounded-full ${isMobile ? 'mr-1' : 'mr-2'} shadow-sm`}></div>
            Wash Alert
          </div>
          <div className="flex items-center">
            <div className={`${isMobile ? 'w-1.5 h-1.5' : 'w-3 h-3'} bg-gradient-to-r from-red-600 to-red-700 rounded-full ${isMobile ? 'mr-1' : 'mr-2'} shadow-sm`}></div>
            Critical
          </div>
        </div>
      </div>

      {isMobile ? (
        <div className="space-y-3">
          {barns.map(barn => (
            <BarnChart key={barn.id} barn={barn} />
          ))}
        </div>
      ) : (
        <>
          <Tabs value={activeBarn} onValueChange={setActiveBarn} className="mb-4">
            <TabsList className="grid w-full grid-cols-3">
              {barns.map(barn => (
                <TabsTrigger key={barn.id} value={barn.id.toString()}>
                  {barn.name.split('-')[0]}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {barns.map(barn => (
            barn.id.toString() === activeBarn && (
              <BarnChart key={barn.id} barn={barn} />
            )
          ))}
        </>
      )}
    </div>
  );
};
