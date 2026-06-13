'use client'

import * as React from "react"
import Link from "next/link"
import { TrendingUp } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { StatsGrid } from "@/features/dashboard/components/stats-grid"
import { RecentActivity } from "@/features/dashboard/components/recent-activity"
import { AISuggestion } from "@/features/dashboard/components/ai-suggestion"
import { AnalyticsOverview } from "@/features/dashboard/components/analytics-overview"

export default function DashboardPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Welcome back, here&apos;s an overview of your outreach progress.</p>
        </div>
        <Button variant="accent" className="w-full gap-2 sm:w-auto" asChild>
          <Link href="/discover">
            <TrendingUp className="h-4 w-4" />
            Analyze New Field
          </Link>
        </Button>
      </div>

      <StatsGrid />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <AnalyticsOverview />

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Top Research Areas</CardTitle>
              <CardDescription>Fields where you have the highest fit scores</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {['Computer Vision', 'Generative AI', 'Robotics', 'NLP', 'Bioinformatics'].map((area) => (
                  <Badge 
                    key={area} 
                    variant="accent" 
                    className="px-4 py-1.5 text-sm cursor-pointer hover:bg-accent/30 transition-colors"
                  >
                    {area}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <RecentActivity />
          <AISuggestion />
        </div>
      </div>
    </div>
  )
}
