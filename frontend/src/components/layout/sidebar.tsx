'use client'

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { BrainCircuit, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { DASHBOARD_NAV_ITEMS } from "@/lib/constants"
import { useLayoutStore } from "@/store/use-layout-store"

export function Sidebar() {
  const pathname = usePathname()
  const { isSidebarOpen, closeSidebar } = useLayoutStore()

  return (
    <>
      {/* Mobile Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden" 
          onClick={closeSidebar}
        />
      )}

      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 flex-col bg-background/80 backdrop-blur-xl border-r border-white/10 transition-transform duration-300 ease-in-out lg:static lg:flex lg:translate-x-0",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-16 items-center justify-between px-6">
          <Link href="/dashboard" className="flex items-center gap-2" onClick={closeSidebar}>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary shadow-soft-glow">
              <BrainCircuit className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold tracking-tight text-foreground/90">
              Research Agent
            </span>
          </Link>
          <button 
            className="rounded-full p-1 hover:bg-white/5 lg:hidden" 
            onClick={closeSidebar}
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {DASHBOARD_NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={closeSidebar}
                className={cn(
                  "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                  isActive 
                    ? "bg-primary/10 text-primary shadow-[inset_0_0_10px_rgba(0,112,243,0.1)]" 
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                )}
              >
                <item.icon className={cn(
                  "mr-3 h-5 w-5 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )} />
                {item.name}
                {isActive && (
                  <div className="ml-auto h-1.5 w-1.5 rounded-full bg-primary shadow-soft-glow" />
                )}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-white/10">
          <div className="rounded-xl bg-muted/50 p-4 border border-white/5">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-primary to-accent" />
              <div className="flex flex-col">
                <span className="text-sm font-medium text-foreground/90">John Doe</span>
                <span className="text-xs text-muted-foreground text-ellipsis overflow-hidden whitespace-nowrap">Researcher</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
