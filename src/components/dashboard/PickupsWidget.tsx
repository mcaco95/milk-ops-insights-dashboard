
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Download } from 'lucide-react';
import { CustomerSummary } from '../../types/dashboard';
import { formatNumber } from '../../utils/formatters';

interface PickupsWidgetProps {
  pickups: CustomerSummary[];
}

export const PickupsWidget = ({ pickups }: PickupsWidgetProps) => {
  const totalWeight = pickups.reduce((sum, pickup) => sum + pickup.totalWeight, 0);
  
  const chartData = pickups.map(pickup => ({
    customer: pickup.customer,
    weight: pickup.totalWeight
  }));

  const handleDownloadCSV = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Customer,Total Weight,Invoice Count\n"
      + pickups.map(p => `${p.customer},${p.totalWeight},${p.invoiceCount}`).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "monthly_pickups.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-2xl shadow-xl border border-slate-200/50 p-6 h-full backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-slate-800 tracking-tight">Monthly Pick-Ups</h2>
        <button
          onClick={handleDownloadCSV}
          className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-slate-600 to-slate-700 text-white rounded-lg hover:from-slate-700 hover:to-slate-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <Download size={16} />
          <span>CSV</span>
        </button>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 mb-6 border border-blue-100 shadow-inner">
        <p className="text-sm text-slate-600 mb-1 font-medium">Total this month</p>
        <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">{formatNumber(totalWeight)} lbs</p>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#334155" />
                <stop offset="50%" stopColor="#475569" />
                <stop offset="100%" stopColor="#64748b" />
              </linearGradient>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="2" dy="4" stdDeviation="3" floodColor="#1e293b" floodOpacity="0.3"/>
              </filter>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.6} />
            <XAxis 
              dataKey="customer" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#475569', fontSize: 11, fontWeight: 500 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#475569', fontSize: 12 }}
              tickFormatter={(value) => formatNumber(value)}
            />
            <Bar 
              dataKey="weight" 
              radius={[8, 8, 0, 0]} 
              fill="url(#barGradient)"
              filter="url(#shadow)"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
