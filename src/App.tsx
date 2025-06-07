import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Dashboard from "./pages/Dashboard";
import DairyDashboard from "./pages/DairyDashboard";
import NotFound from "./pages/NotFound";
import TanksPage from "./pages/dairy/TanksPage";
import RoutesPage from "./pages/dairy/RoutesPage";
import ReportsPage from "./pages/dairy/ReportsPage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dairy-dashboard" element={<DairyDashboard />} />
          <Route path="/dairy/tanks" element={<TanksPage />} />
          <Route path="/dairy/routes" element={<RoutesPage />} />
          <Route path="/dairy/reports" element={<ReportsPage />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
