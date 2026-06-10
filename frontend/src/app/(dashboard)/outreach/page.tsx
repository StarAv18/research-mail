'use client'

import * as React from "react"
import { Send, MailCheck, Clock, ShieldCheck } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

const workflow = [
  {
    title: "Find professors",
    description: "Analyze a faculty profile from Research Discovery.",
    icon: ShieldCheck,
  },
  {
    title: "Review drafts",
    description: "Edit generated messages before sending.",
    icon: Clock,
  },
  {
    title: "Send outreach",
    description: "Use saved drafts for tracked email outreach.",
    icon: MailCheck,
  },
]

export default function OutreachPage() {
  return (
    <div className="animate-in space-y-8 fade-in duration-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Outreach</h1>
          <p className="mt-1 text-muted-foreground">Prepare and send professor outreach from your generated drafts.</p>
        </div>
        <Button variant="accent" className="gap-2">
          <Send className="h-4 w-4" />
          Send Ready Drafts
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {workflow.map((item) => (
          <Card key={item.title}>
            <CardHeader>
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                <item.icon className="h-5 w-5 text-primary" />
              </div>
              <CardTitle className="text-lg">{item.title}</CardTitle>
              <CardDescription>{item.description}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-xl">Sending Queue</CardTitle>
            <CardDescription>Ready drafts will appear here before delivery.</CardDescription>
          </div>
          <Badge variant="secondary">0 queued</Badge>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border border-dashed border-white/10 py-16 text-center">
            <p className="font-medium text-foreground/80">No outreach queued</p>
            <p className="mt-1 text-sm text-muted-foreground">Create or approve drafts to start a sending batch.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
