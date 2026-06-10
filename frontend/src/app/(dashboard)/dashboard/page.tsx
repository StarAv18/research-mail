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
          <Card className="min-h-[400px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="space-y-0.5">
                <CardTitle className="text-xl">Outreach Overview</CardTitle>
                <CardDescription>Activity across universities over time</CardDescription>
              </div>
              <Button variant="outline" size="sm" className="hidden sm:flex h-8">
                View Detailed Analytics
              </Button>
            </CardHeader>
            <CardContent className="flex h-[300px] items-center justify-center text-muted-foreground italic border-t border-white/5 mt-4">
              Chart visualization implementation pending...
            </CardContent>
          </Card>

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
