
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, LogOut, Droplets, Truck, FileText, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';

interface DairyLayoutProps {
  children: React.ReactNode;
  dairyName?: string;
}

export const DairyLayout = ({ children, dairyName = "Milky Way Dairy" }: DairyLayoutProps) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    // In real app, clear auth state
    navigate('/');
  };

  const navItems = [
    { path: '/dairy-dashboard', icon: Home, label: 'Overview' },
    { path: '/dairy/tanks', icon: Droplets, label: 'Tanks' },
    { path: '/dairy/routes', icon: Truck, label: 'Routes' },
    { path: '/dairy/reports', icon: FileText, label: 'Reports' },
  ];

  const NavLink = ({ item, onClick }: { item: typeof navItems[0], onClick?: () => void }) => {
    const isActive = location.pathname === item.path;
    return (
      <Link
        to={item.path}
        onClick={onClick}
        className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
          isActive 
            ? 'bg-blue-100 text-blue-700 font-medium' 
            : 'text-slate-600 hover:bg-slate-100'
        }`}
      >
        <item.icon size={20} />
        <span>{item.label}</span>
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile Header */}
      <div className="md:hidden bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
        <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon">
              <Menu size={20} />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-80">
            <div className="flex flex-col h-full">
              <div className="border-b border-slate-200 pb-4 mb-4">
                <h2 className="text-lg font-semibold text-slate-800">{dairyName}</h2>
                <p className="text-sm text-slate-600">Dairy Dashboard</p>
              </div>
              <nav className="flex-1 space-y-2">
                {navItems.map((item) => (
                  <NavLink 
                    key={item.path} 
                    item={item} 
                    onClick={() => setIsSidebarOpen(false)} 
                  />
                ))}
              </nav>
              <div className="border-t border-slate-200 pt-4">
                <Button 
                  variant="ghost" 
                  onClick={handleLogout}
                  className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <LogOut size={20} className="mr-3" />
                  Logout
                </Button>
              </div>
            </div>
          </SheetContent>
        </Sheet>
        
        <h1 className="text-lg font-semibold text-slate-800">{dairyName}</h1>
        
        <Button variant="ghost" size="icon" onClick={handleLogout}>
          <LogOut size={20} />
        </Button>
      </div>

      {/* Desktop Layout */}
      <div className="hidden md:flex min-h-screen">
        {/* Desktop Sidebar */}
        <div className="w-64 bg-white border-r border-slate-200 flex flex-col">
          <div className="border-b border-slate-200 p-6">
            <h2 className="text-xl font-semibold text-slate-800">{dairyName}</h2>
            <p className="text-sm text-slate-600">Dairy Dashboard</p>
          </div>
          
          <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => (
              <NavLink key={item.path} item={item} />
            ))}
          </nav>
          
          <div className="border-t border-slate-200 p-4">
            <Button 
              variant="ghost" 
              onClick={handleLogout}
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut size={20} className="mr-3" />
              Logout
            </Button>
          </div>
        </div>

        {/* Desktop Content */}
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </div>

      {/* Mobile Content */}
      <div className="md:hidden">
        {children}
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 px-2 py-2">
        <div className="flex justify-around">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center px-3 py-2 min-w-0 ${
                  isActive ? 'text-blue-600' : 'text-slate-500'
                }`}
              >
                <item.icon size={20} />
                <span className="text-xs mt-1 truncate">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
};
