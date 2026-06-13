import * as React from "react"
import { Clock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { activityService } from "@/features/activity/services/activity-service"
import { ActivityLogItem } from "@/types"

export function RecentActivity() {
  const [recentActivity, setRecentActivity] = React.useState<ActivityLogItem[]>([])

  React.useEffect(() => {
    activityService.list()
      .then((items) => setRecentActivity(items.slice(0, 5)))
      .catch(() => setRecentActivity([]))
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {recentActivity.length === 0 ? (
          <div className="rounded-md border border-dashed border-white/10 py-8 text-center text-sm text-muted-foreground">
            No activity logged yet.
          </div>
        ) : recentActivity.map((activity, idx) => (
          <div key={activity.id} className="flex gap-4 group">
            <div className="relative mt-0.5">
              <div className="h-2.5 w-2.5 rounded-full bg-primary shadow-soft-glow" />
              {idx !== recentActivity.length - 1 && (
                <div className="absolute left-[4.5px] top-4 h-10 w-[1px] bg-white/10" />
              )}
            </div>
            <div className="space-y-1">
              <p className="text-sm text-foreground/80 group-hover:text-primary transition-colors">
                {renderMessage(activity)}
              </p>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {new Date(activity.createdAt).toLocaleString()}
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

function renderMessage(activity: ActivityLogItem) {
  const entity = activity.entityType
  const details = activity.details || {}
  if (activity.eventType === 'search') {
    return `Ran discovery search for ${String(details.research_area || details.query || 'research topics')}`
  }
  if (activity.eventType === 'draft_create') {
    return `Generated draft for ${String(details.professor || 'a professor')}`
  }
  if (activity.eventType === 'email_send') {
    return `Sent outreach email to ${String(details.recipient || 'a professor')}`
  }
  if (activity.eventType === 'document_upload') {
    return `Uploaded document ${String(details.filename || '')}`.trim()
  }
  return `${activity.eventType.replaceAll('_', ' ')} ${entity}`
}
