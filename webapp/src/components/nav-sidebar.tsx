'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  AlertTriangle,
  Users,
  Globe,
  MessageSquareQuote,
} from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from '@/components/ui/sidebar';

const navigation = [
  { name: 'Executive Summary', href: '/', icon: LayoutDashboard },
  { name: 'Pain Points', href: '/pain-points', icon: AlertTriangle },
  { name: 'Pilot Candidates', href: '/pilot-candidates', icon: Users },
  { name: 'Regional Comparison', href: '/regional', icon: Globe },
  { name: 'Qualitative Insights', href: '/qualitative', icon: MessageSquareQuote },
];

export function NavSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-4">
        <div className="flex items-center justify-center group-data-[collapsible=icon]:hidden">
          <Image
            src="/ICPSLogo.png"
            alt="ICPS Logo"
            width={180}
            height={60}
            className="object-contain"
            priority
          />
        </div>
        <div className="hidden items-center justify-center group-data-[collapsible=icon]:flex">
          <Image
            src="/ICPSLogo.png"
            alt="ICPS Logo"
            width={32}
            height={32}
            className="object-contain"
            priority
          />
        </div>
      </SidebarHeader>
      <SidebarSeparator />
      <SidebarContent>
        <SidebarMenu className="p-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <SidebarMenuItem key={item.name}>
                <SidebarMenuButton
                  asChild
                  isActive={isActive}
                  tooltip={item.name}
                >
                  <Link href={item.href}>
                    <item.icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="p-4">
        <div className="group-data-[collapsible=icon]:hidden">
          <p className="text-xs text-muted-foreground">
            Electoral Workforce Survey
          </p>
          <p className="text-xs text-muted-foreground">
            ICPS &amp; BSV Association
          </p>
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
