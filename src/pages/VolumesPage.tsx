
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { VolumesResponse } from '../types/api';
import { formatNumber, formatDate } from '../utils/formatters';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

const VolumesPage = () => {
  const [data, setData] = useState<VolumesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().substring(0, 7));
  const { user } = useAuth();

  const fetchData = async () => {
    if (!user?.dairy_id) return;
    
    try {
      const volumesData = await apiService.getVolumes(user.dairy_id, selectedMonth);
      setData(volumesData);
      setError(null);
    } catch (err) {
      setError('Failed to load volumes data');
      console.error('Volumes fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user?.dairy_id, selectedMonth]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-700 font-medium">Loading volumes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto p-4 md:p-6">
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-2">
            Monthly Volumes
          </h1>
          <p className="text-slate-600 text-lg">
            Track your monthly pickup volumes and trends
          </p>
        </div>

        {/* Month Selector */}
        <div className="mb-6">
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="px-4 py-2 border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Summary Cards */}
        {data && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
              <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide mb-2">
                Total Volume
              </h3>
              <p className="text-3xl font-bold text-slate-900">
                {formatNumber(data.total_volume)} gal
              </p>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
              <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide mb-2">
                Total Pickups
              </h3>
              <p className="text-3xl font-bold text-slate-900">
                {data.total_pickups}
              </p>
            </div>
          </div>
        )}

        {/* Volumes Table */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 overflow-hidden">
          <div className="p-6 border-b border-slate-200">
            <h2 className="text-xl font-semibold text-slate-900">
              Daily Breakdown
            </h2>
          </div>
          
          {error ? (
            <div className="p-6 text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          ) : data && data.volumes.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-24">Date</TableHead>
                    <TableHead className="text-right min-w-32">Volume (gal)</TableHead>
                    <TableHead className="text-right min-w-24">Pickups</TableHead>
                    <TableHead className="min-w-32">Customer</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.volumes.map((volume, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">
                        {formatDate(volume.date)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatNumber(volume.volume)}
                      </TableCell>
                      <TableCell className="text-right">
                        {volume.pickups}
                      </TableCell>
                      <TableCell>
                        {volume.customer}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="p-6 text-center text-slate-500">
              No volume data available for this month
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VolumesPage;
