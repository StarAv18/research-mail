import * as React from "react"
import { Clock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

const recentActivity = [
  { id: 1, type: 'discovery', message: 'Found 12 new professors at MIT', time: '2 hours ago' },
  { id: 2, type: 'draft', message: 'Generated email for Dr. Andrew Ng', time: '4 hours ago' },
  { id: 3, type: 'sent', message: 'Outreach sent to Dr. Fei-Fei Li', time: 'Yesterday' },
]

export function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {recentActivity.map((activity, idx) => (
          <div key={activity.id} className="flex gap-4 group">
            <div className="relative mt-0.5">
              <div className="h-2.5 w-2.5 rounded-full bg-primary shadow-soft-glow" />
              {idx !== recentActivity.length - 1 && (
                <div className="absolute left-[4.5px] top-4 h-10 w-[1px] bg-white/10" />
              )}
            </div>
            <div className="space-y-1">
              <p className="text-sm text-foreground/80 group-hover:text-primary transition-colors">
                {activity.message}
              </p>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {activity.time}
              </div>
            </div>
          </div>
        ))}
        <Button variant="ghost" size="sm" className="w-full text-muted-foreground mt-2">
          View All Activity
        </Button>
      </CardContent>
    </Card>
  )
}
