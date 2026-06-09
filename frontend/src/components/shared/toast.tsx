'use client'

import * as React from "react"
import { useNotificationStore, Notification } from "@/store/use-notification-store"
import { cn } from "@/lib/utils"
import { 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  AlertTriangle,
  X 
} from "lucide-react"

const icons = {
  success: <CheckCircle2 className="h-5 w-5 text-emerald-400" />,
  error: <AlertCircle className="h-5 w-5 text-red-400" />,
  info: <Info className="h-5 w-5 text-blue-400" />,
  warning: <AlertTriangle className="h-5 w-5 text-amber-400" />,
}

export function ToastContainer() {
  const { notifications, removeNotification } = useNotificationStore()

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      {notifications.map((n) => (
        <Toast key={n.id} notification={n} onClose={() => removeNotification(n.id)} />
      ))}
    </div>
  )
}

function Toast({ notification, onClose }: { notification: Notification; onClose: () => void }) {
  return (
    <div 
      className={cn(
        "pointer-events-auto flex min-w-[320px] max-w-md animate-in slide-in-from-right-full duration-300",
        "glass-card bg-muted/90 p-4 border-white/10"
      )}
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0">{icons[notification.type]}</div>
        <div className="flex-1 space-y-1">
          <p className="text-sm font-medium text-foreground/90">{notification.message}</p>
          {notification.description && (
            <p className="text-xs text-muted-foreground">{notification.description}</p>
          )}
        </div>
        <button 
          onClick={onClose}
          className="flex-shrink-0 rounded-md p-1 hover:bg-white/5 text-muted-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      {/* Progress Bar */}
      <div className="absolute bottom-0 left-0 h-0.5 w-full bg-white/5 overflow-hidden">
        <div 
          className={cn(
            "h-full transition-all duration-[5000ms] ease-linear",
            notification.type === 'success' ? 'bg-emerald-500' :
            notification.type === 'error' ? 'bg-red-500' :
            notification.type === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
          )}
          style={{ width: '100%', animation: 'progress 5s linear forwards' }}
        />
      </div>
    </div>
  )
}
