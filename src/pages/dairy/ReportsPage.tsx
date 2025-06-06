
import { AppSidebar } from '../../components/AppSidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Download, Calendar } from 'lucide-react';

export default function ReportsPage() {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <AppSidebar />
        <SidebarInset>
          <div className="container mx-auto p-4 md:p-6">
            {/* Header with sidebar toggle */}
            <div className="flex items-center justify-between mb-6 md:mb-8">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-2 md:mb-3 tracking-tight">
                  Monthly Reports
                </h1>
                <p className="text-slate-600 text-base md:text-lg font-medium">
                  Access your dairy production reports
                </p>
              </div>
              <SidebarTrigger />
            </div>

            {/* Simple Reports Interface */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Report 1 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    May 2025 Summary
                  </CardTitle>
                  <CardDescription>Monthly production and pickups</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-semibold mb-4">246,300 Liters</p>
                  <p className="text-sm text-slate-600 mb-6">12 Pickups • Generated June 1, 2025</p>
                  <Button className="w-full flex items-center justify-center gap-2">
                    <Download className="h-4 w-4" />
                    Download PDF
                  </Button>
                </CardContent>
              </Card>

              {/* Report 2 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    April 2025 Summary
                  </CardTitle>
                  <CardDescription>Monthly production and pickups</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-semibold mb-4">239,470 Liters</p>
                  <p className="text-sm text-slate-600 mb-6">11 Pickups • Generated May 1, 2025</p>
                  <Button className="w-full flex items-center justify-center gap-2">
                    <Download className="h-4 w-4" />
                    Download PDF
                  </Button>
                </CardContent>
              </Card>

              {/* Request Custom Report */}
              <Card className="bg-gradient-to-br from-slate-50 to-blue-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-blue-600" />
                    Custom Report
                  </CardTitle>
                  <CardDescription>Generate a report for any date range</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-6">
                    Select a custom date range to generate a specialized report for your records.
                  </p>
                  <Button variant="outline" className="w-full">
                    Request Custom Report
                  </Button>
                </CardContent>
              </Card>
            </div>

            <p className="mt-8 text-center text-slate-500 text-sm">
              Need help with reports? Contact your regional manager at (555) 123-4567
            </p>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
