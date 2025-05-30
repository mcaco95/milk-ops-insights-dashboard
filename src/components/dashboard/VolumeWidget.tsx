
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
import { Tank } from '../../types/dashboard';
import { formatNumber, formatDateTime } from '../../utils/formatters';

interface VolumeWidgetProps {
  tanks: Tank[];
}

export const VolumeWidget = ({ tanks }: VolumeWidgetProps) => {
  const chartData = tanks.map(tank => ({
    name: tank.name,
    current: tank.currentVolume,
    predicted: tank.predictedVolume - tank.currentVolume,
    fillPercentage: (tank.currentVolume / tank.predictedVolume) * 100
  }));

  const totalSuperLoads = tanks.reduce((sum, tank) => sum + tank.superLoadsAvailable, 0);
  const lastHit = tanks.reduce((latest, tank) => 
    new Date(tank.lastHit) > new Date(latest) ? tank.lastHit : latest, 
    tanks[0]?.lastHit || ''
  );

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 h-full">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Volume & Predictions</h2>
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-600 rounded mr-2"></div>
            Current
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-300 rounded mr-2"></div>
            Predicted
          </div>
        </div>
      </div>

      <div className="h-64 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis 
              dataKey="name" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 12 }}
              tickFormatter={(value) => formatNumber(value)}
            />
            <Bar dataKey="current" stackId="a" radius={[0, 0, 4, 4]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-current-${index}`} fill="#059669" />
              ))}
            </Bar>
            <Bar dataKey="predicted" stackId="a" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-predicted-${index}`} fill="#86efac" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Super Loads</p>
          <p className="text-2xl font-bold text-blue-600">{totalSuperLoads.toFixed(2)}</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Last Hit</p>
          <p className="text-sm font-semibold text-gray-900">{formatDateTime(lastHit)}</p>
        </div>
      </div>
    </div>
  );
};
