
import { DairyLayout } from '../../components/dairy/DairyLayout';
import { FileText, Download, TrendingUp, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';

const ReportsPage = () => {
  const mockReports = [
    {
      id: 1,
      title: 'May 2025 Production Report',
      type: 'Monthly Summary',
      date: '2025-05-31',
      totalMilk: '245,600L',
      avgDaily: '7,920L',
      status: 'Available'
    },
    {
      id: 2,
      title: 'April 2025 Production Report',
      type: 'Monthly Summary',
      date: '2025-04-30',
      totalMilk: '238,400L',
      avgDaily: '7,947L',
      status: 'Available'
    },
    {
      id: 3,
      title: 'March 2025 Production Report',
      type: 'Monthly Summary',
      date: '2025-03-31',
      totalMilk: '251,200L',
      avgDaily: '8,103L',
      status: 'Available'
    }
  ];

  const currentStats = {
    thisMonth: '186,400L',
    lastMonth: '238,400L',
    avgDaily: '7,850L',
    trend: '+2.3%'
  };

  return (
    <DairyLayout>
      <div className="p-4 pb-20 md:pb-4">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">Production Reports</h1>
          <p className="text-slate-600">View your milk production summaries</p>
        </div>

        {/* Current Month Summary */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 mb-6">
          <div className="flex items-center mb-4">
            <TrendingUp size={20} className="text-blue-600 mr-2" />
            <h2 className="text-lg font-semibold text-slate-800">June 2025 (Current)</h2>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{currentStats.thisMonth}</p>
              <p className="text-sm text-slate-600">This Month</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-800">{currentStats.lastMonth}</p>
              <p className="text-sm text-slate-600">Last Month</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-800">{currentStats.avgDaily}</p>
              <p className="text-sm text-slate-600">Avg Daily</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{currentStats.trend}</p>
              <p className="text-sm text-slate-600">vs Last Month</p>
            </div>
          </div>
        </div>

        {/* Historical Reports */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Monthly Reports</h2>
          <div className="space-y-4">
            {mockReports.map((report) => (
              <div key={report.id} className="bg-white rounded-lg border border-slate-200 p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <FileText size={20} className="text-slate-600 mr-3" />
                    <div>
                      <h3 className="font-semibold text-slate-800">{report.title}</h3>
                      <p className="text-sm text-slate-600">{report.type}</p>
                    </div>
                  </div>
                  <Button size="sm" variant="outline">
                    <Download size={16} className="mr-2" />
                    Download
                  </Button>
                </div>

                <div className="grid grid-cols-3 gap-4 pt-3 border-t border-slate-200">
                  <div>
                    <p className="text-sm text-slate-600">Total Production</p>
                    <p className="font-semibold text-slate-800">{report.totalMilk}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Daily Average</p>
                    <p className="font-semibold text-slate-800">{report.avgDaily}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Date</p>
                    <p className="font-semibold text-slate-800">
                      {new Date(report.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-slate-100 rounded-lg p-4">
          <h3 className="font-semibold text-slate-800 mb-3">Quick Actions</h3>
          <div className="space-y-2">
            <Button variant="outline" className="w-full justify-start">
              <Calendar size={16} className="mr-2" />
              Request Custom Report
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Download size={16} className="mr-2" />
              Export All Reports
            </Button>
          </div>
        </div>
      </div>
    </DairyLayout>
  );
};

export default ReportsPage;
