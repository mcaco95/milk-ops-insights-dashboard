
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
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

  const colors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

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
    <div className="bg-white rounded-xl shadow-lg p-6 h-full">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Monthly Pick-Ups</h2>
        <button
          onClick={handleDownloadCSV}
          className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Download size={16} />
          <span>CSV</span>
        </button>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-6">
        <p className="text-sm text-gray-600 mb-1">Total this month</p>
        <p className="text-3xl font-bold text-blue-600">{formatNumber(totalWeight)} lbs</p>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis 
              dataKey="customer" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 12 }}
              tickFormatter={(value) => formatNumber(value)}
            />
            <Bar dataKey="weight" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
