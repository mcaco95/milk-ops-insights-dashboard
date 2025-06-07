
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import VolumesPage from "./pages/VolumesPage";
import RoutesPage from "./pages/RoutesPage";
import TanksPage from "./pages/TanksPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Navbar />
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="/volumes" element={
              <ProtectedRoute>
                <Navbar />
                <VolumesPage />
              </ProtectedRoute>
            } />
            <Route path="/routes" element={
              <ProtectedRoute>
                <Navbar />
                <RoutesPage />
              </ProtectedRoute>
            } />
            <Route path="/tanks" element={
              <ProtectedRoute>
                <Navbar />
                <TanksPage />
              </ProtectedRoute>
            } />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
