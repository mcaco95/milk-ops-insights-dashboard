
import { Milk, BarChart3, Truck, FileText, LogOut, Menu } from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";

// Navigation items for dairy users
const navigationItems = [
  {
    title: "Dashboard",
    url: "/dairy-dashboard",
    icon: BarChart3,
    description: "Overview of your dairy"
  },
  {
    title: "Tanks",
    url: "/dairy-dashboard/tanks", 
    icon: Milk,
    description: "Tank status and volumes"
  },
  {
    title: "Routes",
    url: "/dairy-dashboard/routes",
    icon: Truck,
    description: "Pickup schedules"
  },
  {
    title: "Reports",
    url: "/dairy-dashboard/reports",
    icon: FileText,
    description: "Monthly summaries"
  }
];

export function AppSidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    // Navigate back to login
    navigate('/');
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-600">
            <Milk className="h-4 w-4 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-sidebar-foreground">
              Milky Way Dairy
            </span>
            <span className="text-xs text-sidebar-foreground/70">
              Producer #633
            </span>
          </div>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    asChild 
                    isActive={location.pathname === item.url}
                    tooltip={item.description}
                  >
                    <a href={item.url} className="flex items-center gap-2">
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={handleLogout} tooltip="Return to login">
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
