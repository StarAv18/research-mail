'use client'

import * as React from "react"
import { 
  Search, 
  Bell, 
  Cpu, 
  ChevronDown,
  Menu,
  KeyRound,
  Save,
  X,
  Mail
} from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useLayoutStore } from "@/store/use-layout-store"
import { AI_API_KEY_KEY, AI_PROVIDER_KEY, GMAIL_ADDRESS_KEY, GMAIL_APP_PASSWORD_KEY } from "@/services/api-client"

export function TopNav() {
  const { toggleSidebar } = useLayoutStore()
  const [settingsOpen, setSettingsOpen] = React.useState(false)
  const [provider, setProvider] = React.useState("gemini")
  const [apiKey, setApiKey] = React.useState("")
  const [gmailAddress, setGmailAddress] = React.useState("")
  const [gmailAppPassword, setGmailAppPassword] = React.useState("")

  React.useEffect(() => {
    setProvider(localStorage.getItem(AI_PROVIDER_KEY) || "gemini")
    setApiKey(localStorage.getItem(AI_API_KEY_KEY) || "")
    setGmailAddress(localStorage.getItem(GMAIL_ADDRESS_KEY) || "")
    setGmailAppPassword(localStorage.getItem(GMAIL_APP_PASSWORD_KEY) || "")
  }, [])

  const saveSettings = () => {
    localStorage.setItem(AI_PROVIDER_KEY, provider)
    localStorage.setItem(AI_API_KEY_KEY, apiKey.trim())
    localStorage.setItem(GMAIL_ADDRESS_KEY, gmailAddress.trim())
    localStorage.setItem(GMAIL_APP_PASSWORD_KEY, gmailAppPassword.trim())
    setSettingsOpen(false)
  }

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
        <button
          className="flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1.5 shadow-[0_0_10px_rgba(0,112,243,0.1)] transition-colors hover:bg-primary/15"
          onClick={() => setSettingsOpen(true)}
          aria-label="Open AI settings"
        >
          <Cpu className="h-4 w-4 text-primary" />
          <span className="text-xs font-medium text-primary hidden md:inline-block">
            {provider === "gemini" ? "Gemini" : provider === "openrouter" ? "OpenRouter" : "Ollama"}
            {apiKey ? ": Ready" : ": Needs key"}
          </span>
          <div className={`h-2 w-2 rounded-full ${apiKey ? "bg-emerald-500 shadow-[0_0_8px_#10b981]" : "bg-amber-400 shadow-[0_0_8px_#f59e0b]"}`} />
        </button>
        
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

      {settingsOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-background/70 px-4 pt-20 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-lg border border-white/10 bg-slate-950 p-5 shadow-2xl">
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <KeyRound className="h-5 w-5 text-accent" />
                <h2 className="text-lg font-semibold">AI Settings</h2>
              </div>
              <button
                className="rounded-md p-1 text-muted-foreground hover:bg-white/5 hover:text-foreground"
                onClick={() => setSettingsOpen(false)}
                aria-label="Close AI settings"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <label className="block space-y-2">
                <span className="text-sm font-medium text-muted-foreground">Provider</span>
                <select
                  className="h-10 w-full rounded-md border border-white/10 bg-muted/50 px-3 text-sm text-foreground outline-none focus:border-primary"
                  value={provider}
                  onChange={(event) => setProvider(event.target.value)}
                >
                  <option value="gemini">Gemini</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="ollama">Ollama</option>
                </select>
              </label>

              <label className="block space-y-2">
                <span className="text-sm font-medium text-muted-foreground">API key</span>
                <Input
                  type="password"
                  value={apiKey}
                  onChange={(event) => setApiKey(event.target.value)}
                  placeholder="Paste your provider API key"
                />
              </label>

              <div className="border-t border-white/10 pt-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <Mail className="h-4 w-4 text-accent" />
                  Gmail sending
                </div>
                <div className="space-y-3">
                  <label className="block space-y-2">
                    <span className="text-sm font-medium text-muted-foreground">Gmail address</span>
                    <Input
                      type="email"
                      value={gmailAddress}
                      onChange={(event) => setGmailAddress(event.target.value)}
                      placeholder="yourname@gmail.com"
                    />
                  </label>
                  <label className="block space-y-2">
                    <span className="text-sm font-medium text-muted-foreground">Gmail app password</span>
                    <Input
                      type="password"
                      value={gmailAppPassword}
                      onChange={(event) => setGmailAppPassword(event.target.value)}
                      placeholder="16-character app password"
                    />
                  </label>
                </div>
              </div>

              <Button className="w-full gap-2" variant="accent" onClick={saveSettings}>
                <Save className="h-4 w-4" />
                Save Settings
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
