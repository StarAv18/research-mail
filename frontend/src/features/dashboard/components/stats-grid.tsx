import * as React from "react"
import { Users, FileEdit, Send, Activity } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { apiClient } from "@/services/api-client"
import { APIResponse } from "@/types"

interface Metrics {
  professorsFound: number
  draftsCreated: number
  emailsSent: number
  responseRate: number
}

export function StatsGrid() {
  const [metrics, setMetrics] = React.useState<Metrics>({
    professorsFound: 0,
    draftsCreated: 0,
    emailsSent: 0,
    responseRate: 0,
  })

  React.useEffect(() => {
    apiClient
      .get<any, APIResponse<Metrics>>('/system/metrics')
      .then((response) => setMetrics(response.data))
      .catch(() => {
        setMetrics({ professorsFound: 0, draftsCreated: 0, emailsSent: 0, responseRate: 0 })
      })
  }, [])

  const stats = [
    { name: 'Professors Found', value: String(metrics.professorsFound), icon: Users, change: 'Live', changeType: 'positive' },
    { name: 'Drafts Created', value: String(metrics.draftsCreated), icon: FileEdit, change: 'Live', changeType: 'positive' },
    { name: 'Emails Sent', value: String(metrics.emailsSent), icon: Send, change: 'Live', changeType: 'positive' },
    { name: 'Response Rate', value: `${metrics.responseRate}%`, icon: Activity, change: 'Tracked', changeType: 'positive' },
  ]

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.name} className="relative overflow-hidden group">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="rounded-lg bg-primary/10 p-2.5 group-hover:bg-primary/20 transition-colors">
                <stat.icon className="h-6 w-6 text-primary" />
              </div>
              <Badge variant={stat.changeType === 'positive' ? 'success' : 'destructive'}>
                {stat.change}
              </Badge>
            </div>
            <div className="mt-4">
              <p className="text-sm font-medium text-muted-foreground">{stat.name}</p>
              <h3 className="text-2xl font-bold mt-1 text-foreground/90">{stat.value}</h3>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
