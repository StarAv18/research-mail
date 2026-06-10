import {
  FileText,
  LayoutDashboard,
  type LucideIcon,
  Search,
  Send,
} from "lucide-react"

export type DashboardNavItem = {
  name: string
  href: string
  icon: LucideIcon
}

export const DASHBOARD_NAV_ITEMS: DashboardNavItem[] = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Research Discovery",
    href: "/discover",
    icon: Search,
  },
  {
    name: "Drafts",
    href: "/drafts",
    icon: FileText,
  },
  {
    name: "Outreach",
    href: "/outreach",
    icon: Send,
  },
]
