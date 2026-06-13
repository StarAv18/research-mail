import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { activityService } from "@/features/activity/services/activity-service"
import { DashboardAnalytics } from "@/types"

const emptyState: DashboardAnalytics = {
  dailyOutreach: [],
  weeklyOutreach: [],
  monthlyOutreach: [],
  professorsDiscovered: 0,
  draftsGenerated: 0,
  emailsSent: 0,
  responsesReceived: 0,
}

export function AnalyticsOverview() {
  const [analytics, setAnalytics] = React.useState<DashboardAnalytics>(emptyState)

  React.useEffect(() => {
    activityService.analytics()
      .then(setAnalytics)
      .catch(() => setAnalytics(emptyState))
  }, [])

  return (
    <Card className="min-h-[400px]">
      <CardHeader>
        <CardTitle className="text-xl">Outreach Overview</CardTitle>
        <CardDescription>Daily, weekly, and monthly campaign activity.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <ChartRow title="Daily Outreach" items={analytics.dailyOutreach.slice(-7)} />
        <ChartRow title="Weekly Outreach" items={analytics.weeklyOutreach.slice(-7)} />
        <ChartRow title="Monthly Outreach" items={analytics.monthlyOutreach.slice(-7)} />
        <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
          <Metric label="Professors Discovered" value={analytics.professorsDiscovered} />
          <Metric label="Drafts Generated" value={analytics.draftsGenerated} />
          <Metric label="Emails Sent" value={analytics.emailsSent} />
          <Metric label="Responses Received" value={analytics.responsesReceived} />
        </div>
      </CardContent>
    </Card>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-white/10 bg-muted/20 p-3">
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-1 text-xl font-semibold text-foreground/90">{value}</div>
    </div>
  )
}

function ChartRow({ title, items }: { title: string; items: { date: string; value: number }[] }) {
  const max = Math.max(...items.map((item) => item.value), 1)

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium text-foreground/90">{title}</div>
      <div className="grid grid-cols-7 gap-2">
        {items.length === 0 ? (
          <div className="col-span-7 rounded-md border border-dashed border-white/10 py-4 text-center text-sm text-muted-foreground">
            No activity yet
          </div>
        ) : items.map((item) => (
          <div key={`${title}-${item.date}`} className="space-y-2">
            <div className="flex h-28 items-end rounded-md bg-muted/20 p-2">
              <div
                className="w-full rounded-sm bg-primary/80"
                style={{ height: `${Math.max((item.value / max) * 100, 8)}%` }}
              />
            </div>
            <div className="text-center text-[10px] text-muted-foreground">
              {new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
