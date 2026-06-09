import * as React from "react"
import { Users, FileEdit, Send, Activity } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const stats = [
  { name: 'Professors Found', value: '128', icon: Users, change: '+12%', changeType: 'positive' },
  { name: 'Drafts Created', value: '45', icon: FileEdit, change: '+5%', changeType: 'positive' },
  { name: 'Emails Sent', value: '24', icon: Send, change: '+18%', changeType: 'positive' },
  { name: 'Response Rate', value: '14%', icon: Activity, change: '-2%', changeType: 'negative' },
]

export function StatsGrid() {
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
