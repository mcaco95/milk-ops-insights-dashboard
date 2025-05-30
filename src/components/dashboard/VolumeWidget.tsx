
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Barn } from '../../types/dashboard';
import { formatNumber, formatDateTime } from '../../utils/formatters';
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

  const BarnChart = ({ barn }: { barn: Barn }) => {
    const chartData = barn.tanks.map(tank => ({
      name: tank.name,
      current: tank.currentVolume,
      predicted: tank.predictedVolume - tank.currentVolume,
      fillPercentage: (tank.currentVolume / tank.predictedVolume) * 100,
      timeToFull: calculateTimeToFull(tank.currentVolume, tank.predictedVolume, tank.fillRate)
    }));

    const totalSuperLoads = barn.tanks.reduce((sum, tank) => sum + tank.superLoadsAvailable, 0);
    const lastHit = barn.tanks.reduce((latest, tank) => 
      new Date(tank.lastHit) > new Date(latest) ? tank.lastHit : latest, 
      barn.tanks[0]?.lastHit || ''
    );

    return (
      <div className={`${isMobile ? 'mb-6' : ''}`}>
        {isMobile && (
          <h3 className="text-lg font-semibold text-slate-800 mb-4">{barn.name}</h3>
        )}
        
        <div className="h-64 mb-6 relative">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 40, right: 30, left: 20, bottom: 5 }}>
              <defs>
                <linearGradient id="currentGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#1e40af" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
                <linearGradient id="predictedGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#93c5fd" />
                  <stop offset="100%" stopColor="#bfdbfe" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.6} />
              <XAxis 
                dataKey="name" 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#475569', fontSize: 12, fontWeight: 500 }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#475569', fontSize: 12 }}
                tickFormatter={(value) => formatNumber(value)}
              />
              <Bar dataKey="current" stackId="a" radius={[0, 0, 8, 8]} fill="url(#currentGradient)">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-current-${index}`} />
                ))}
              </Bar>
              <Bar dataKey="predicted" stackId="a" radius={[8, 8, 0, 0]} fill="url(#predictedGradient)">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-predicted-${index}`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          
          {/* Time to Full Labels floating above bars */}
          <div className="absolute inset-0 pointer-events-none">
            {chartData.map((entry, index) => {
              if (!entry.timeToFull) return null;
              
              // Calculate position based on chart dimensions and data
              const chartWidth = 100; // percentage
              const barWidth = chartWidth / chartData.length;
              const leftPosition = (index * barWidth) + (barWidth / 2);
              
              return (
                <div
                  key={`time-to-full-${index}`}
                  className="absolute top-2 transform -translate-x-1/2 bg-orange-500 text-white text-xs px-2 py-1 rounded-full shadow-lg font-medium z-10"
                  style={{ left: `${leftPosition}%` }}
                >
                  Full in: {entry.timeToFull}
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200/60">
          <div className="text-center bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-3 border border-blue-100">
            <p className="text-sm text-slate-600 mb-1 font-medium">Super Loads</p>
            <p className="text-2xl font-bold text-blue-700">{totalSuperLoads.toFixed(2)}</p>
          </div>
          <div className="text-center bg-gradient-to-r from-slate-50 to-gray-50 rounded-xl p-3 border border-slate-100">
            <p className="text-sm text-slate-600 mb-1 font-medium">Last Hit</p>
            <p className="text-sm font-semibold text-slate-800">{formatDateTime(lastHit)}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-2xl shadow-xl border border-slate-200/50 p-6 h-full backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-slate-800 tracking-tight">Volume & Predictions</h2>
        <div className="flex items-center space-x-4 text-sm text-slate-600">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-gradient-to-r from-blue-600 to-blue-700 rounded-full mr-2 shadow-sm"></div>
            Current
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-gradient-to-r from-blue-300 to-blue-400 rounded-full mr-2 shadow-sm"></div>
            Predicted
          </div>
        </div>
      </div>

      {isMobile ? (
        // Mobile: Show all barns stacked vertically
        <div className="space-y-6">
          {barns.map(barn => (
            <BarnChart key={barn.id} barn={barn} />
          ))}
        </div>
      ) : (
        // Desktop: Show tabs
        <>
          <Tabs value={activeBarn} onValueChange={setActiveBarn} className="mb-4">
            <TabsList className="grid w-full grid-cols-2">
              {barns.map(barn => (
                <TabsTrigger key={barn.id} value={barn.id.toString()}>
                  {barn.name}
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
