
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui/button';
import { Menu, X } from 'lucide-react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Monthly Volumes', path: '/volumes' },
    { name: 'Live Routes', path: '/routes' },
    { name: 'Tank Status', path: '/tanks' },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    logout();
    setShowLogoutConfirm(false);
  };

  return (
    <>
      <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo/Brand */}
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent">
                Dairy Dashboard
              </h1>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive(item.path)
                      ? 'bg-blue-100 text-blue-700 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </div>

            {/* Right Side - Dairy Name & Logout */}
            <div className="hidden md:flex items-center space-x-4">
              <span className="text-sm text-slate-600 font-medium">
                {user?.dairy_name}
              </span>
              <Button
                onClick={() => setShowLogoutConfirm(true)}
                variant="outline"
                size="sm"
                className="h-9"
              >
                Logout
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Navigation Menu */}
          {isMobileMenuOpen && (
            <div className="md:hidden bg-white border-t border-slate-200">
              <div className="px-4 py-4 space-y-3">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`block px-4 py-3 rounded-lg text-base font-medium transition-all duration-200 ${
                      isActive(item.path)
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
                
                <div className="pt-3 border-t border-slate-200">
                  <div className="text-sm text-slate-500 mb-2">
                    {user?.dairy_name}
                  </div>
                  <Button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      setShowLogoutConfirm(true);
                    }}
                    variant="outline"
                    className="w-full h-11"
                  >
                    Logout
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Confirm Logout
            </h3>
            <p className="text-slate-600 mb-6">
              Are you sure you want to log out? You'll need to sign in again to access your dashboard.
            </p>
            <div className="flex space-x-3">
              <Button
                onClick={() => setShowLogoutConfirm(false)}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleLogout}
                className="flex-1 bg-red-600 hover:bg-red-700"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
