
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
import { Switch } from "@/components/ui/switch";
import { Tank } from '../../types/dashboard';
import { formatNumber, formatDateTime } from '../../utils/formatters';

interface VolumeWidgetProps {
  tanks: Tank[];
}

export const VolumeWidget = ({ tanks }: VolumeWidgetProps) => {
  const [visibleTanks, setVisibleTanks] = useState<Record<number, boolean>>(
    tanks.reduce((acc, tank) => ({ ...acc, [tank.id]: true }), {})
  );

  const filteredTanks = tanks.filter(tank => visibleTanks[tank.id]);
  
  const chartData = filteredTanks.map(tank => ({
    name: tank.name,
    current: tank.currentVolume,
    predicted: tank.predictedVolume - tank.currentVolume,
    fillPercentage: (tank.currentVolume / tank.predictedVolume) * 100,
    eta: tank.eta
  }));

  const totalSuperLoads = filteredTanks.reduce((sum, tank) => sum + tank.superLoadsAvailable, 0);
  const lastHit = filteredTanks.reduce((latest, tank) => 
    new Date(tank.lastHit) > new Date(latest) ? tank.lastHit : latest, 
    filteredTanks[0]?.lastHit || ''
  );

  const toggleTankVisibility = (tankId: number) => {
    setVisibleTanks(prev => ({ ...prev, [tankId]: !prev[tankId] }));
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

      {/* Tank Toggles */}
      <div className="mb-4 space-y-2">
        {tanks.map(tank => (
          <div key={tank.id} className="flex items-center justify-between py-1">
            <span className="text-sm font-medium text-slate-700">{tank.name}</span>
            <Switch
              checked={visibleTanks[tank.id]}
              onCheckedChange={() => toggleTankVisibility(tank.id)}
            />
          </div>
        ))}
      </div>

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
        
        {/* ETA Labels floating above bars */}
        {chartData.map((entry, index) => {
          if (!entry.eta) return null;
          const xPos = 20 + (index * (100 / chartData.length)) + '%';
          return (
            <div
              key={`eta-${index}`}
              className="absolute top-2 transform -translate-x-1/2 bg-green-500 text-white text-xs px-2 py-1 rounded-full shadow-lg font-medium"
              style={{ left: xPos }}
            >
              ETA: {entry.eta}
            </div>
          );
        })}
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
