'use client'

import * as React from "react"
import { 
  Search, 
  Bell, 
  Cpu, 
  ChevronDown,
  Menu
} from "lucide-react"
import { Input } from "@/components/ui/input"
import { useLayoutStore } from "@/store/use-layout-store"

export function TopNav() {
  const { toggleSidebar } = useLayoutStore()

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between bg-background/50 backdrop-blur-xl border-b border-white/10 px-4 lg:px-8">
      <div className="flex flex-1 items-center gap-4">
        <button 
          className="rounded-full p-2 hover:bg-white/5 lg:hidden" 
          onClick={toggleSidebar}
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5 text-muted-foreground" />
        </button>

        <div className="relative w-full max-w-md hidden sm:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input 
            placeholder="Search professors, research areas..." 
            className="pl-10 bg-muted/30 border-white/5"
          />
        </div>
      </div>

      <div className="flex items-center gap-3 lg:gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 shadow-[0_0_10px_rgba(0,112,243,0.1)]">
          <Cpu className="h-4 w-4 text-primary" />
          <span className="text-xs font-medium text-primary hidden md:inline-block">Ollama: Online</span>
          <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
        </div>
        
        <button className="relative rounded-full p-2 text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-primary shadow-soft-glow" />
        </button>

        <div className="h-8 w-[1px] bg-white/10 hidden sm:block" />

        <button className="flex items-center gap-2 group">
          <div className="h-8 w-8 rounded-full bg-muted border border-white/10" />
          <ChevronDown className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
        </button>
      </div>
    </header>
  )
}
