'use client'

import * as React from "react"
import { MailCheck, Send } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { campaignsService } from "@/features/campaigns/services/campaigns-service"
import { draftsService } from "@/features/drafts/services/drafts-service"
import { Campaign, CampaignLog, Draft } from "@/types"
import { useNotificationStore } from "@/store/use-notification-store"

export default function OutreachPage() {
  const [drafts, setDrafts] = React.useState<Draft[]>([])
  const [campaigns, setCampaigns] = React.useState<Campaign[]>([])
  const [selectedDraftIds, setSelectedDraftIds] = React.useState<string[]>([])
  const [campaignName, setCampaignName] = React.useState("New Outreach Campaign")
  const [selectedCampaignId, setSelectedCampaignId] = React.useState<string | null>(null)
  const [campaignLogs, setCampaignLogs] = React.useState<CampaignLog[]>([])
  const addNotification = useNotificationStore((s) => s.addNotification)

  const loadData = React.useCallback(async () => {
    try {
      const [draftItems, campaignItems] = await Promise.all([
        draftsService.listDrafts(),
        campaignsService.list(),
      ])
      setDrafts(draftItems)
      setCampaigns(campaignItems)
      if (campaignItems[0]) {
        setSelectedCampaignId(campaignItems[0].id)
        setCampaignLogs(await campaignsService.logs(campaignItems[0].id))
      }
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Failed to load outreach data', description: error.message })
    }
  }, [addNotification])

  React.useEffect(() => {
    loadData()
  }, [loadData])

  const readyDrafts = drafts.filter((draft) => draft.professorEmail && draft.status !== 'sent')

  const toggleDraft = (draftId: string) => {
    setSelectedDraftIds((current) =>
      current.includes(draftId) ? current.filter((id) => id !== draftId) : [...current, draftId]
    )
  }

  const createCampaign = async () => {
    if (selectedDraftIds.length === 0) {
      addNotification({ type: 'warning', message: 'Select at least one draft first' })
      return
    }
    try {
      const campaign = await campaignsService.create({ name: campaignName, draftIds: selectedDraftIds })
      setCampaigns((current) => [campaign, ...current])
      setSelectedCampaignId(campaign.id)
      setSelectedDraftIds([])
      addNotification({ type: 'success', message: 'Campaign created', description: campaign.name })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Campaign creation failed', description: error.message })
    }
  }

  const executeCampaign = async () => {
    if (!selectedCampaignId) return
    try {
      const result = await campaignsService.execute(selectedCampaignId)
      setCampaignLogs(await campaignsService.logs(selectedCampaignId))
      setCampaigns(await campaignsService.list())
      addNotification({
        type: result.failed > 0 ? 'warning' : 'success',
        message: 'Campaign executed',
        description: `${result.sent} sent, ${result.failed} failed`,
      })
      loadData()
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Campaign execution failed', description: error.message })
    }
  }

  const selectCampaign = async (campaignId: string) => {
    setSelectedCampaignId(campaignId)
    setCampaignLogs(await campaignsService.logs(campaignId))
  }

  return (
    <div className="animate-in space-y-8 fade-in duration-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Outreach Campaigns</h1>
          <p className="mt-1 text-muted-foreground">Create batches from approved drafts, execute Gmail sending, and review delivery logs.</p>
        </div>
        <Button variant="accent" className="gap-2" onClick={executeCampaign} disabled={!selectedCampaignId}>
          <Send className="h-4 w-4" />
          Execute Selected Campaign
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.2fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Create Campaign</CardTitle>
            <CardDescription>Select drafts with recipient emails and group them into a sending batch.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <input
              className="h-11 w-full rounded-md border border-white/10 bg-muted/20 px-3 text-sm"
              value={campaignName}
              onChange={(event) => setCampaignName(event.target.value)}
              placeholder="Campaign name"
            />
            <div className="space-y-3">
              {readyDrafts.length === 0 ? (
                <div className="rounded-md border border-dashed border-white/10 py-10 text-center text-muted-foreground">
                  No sendable drafts available yet.
                </div>
              ) : readyDrafts.map((draft) => (
                <label key={draft.id} className="flex cursor-pointer items-start gap-3 rounded-lg border border-white/10 p-4">
                  <input
                    type="checkbox"
                    checked={selectedDraftIds.includes(draft.id)}
                    onChange={() => toggleDraft(draft.id)}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium text-foreground/90">{draft.professorName}</div>
                    <div className="text-xs text-muted-foreground">{draft.professorEmail}</div>
                    <div className="mt-1 text-sm text-muted-foreground line-clamp-2">{draft.subject}</div>
                  </div>
                </label>
              ))}
            </div>
            <Button variant="outline" className="gap-2" onClick={createCampaign}>
              <MailCheck className="h-4 w-4" />
              Create Campaign
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Campaign Dashboard</CardTitle>
            <CardDescription>Status, send metrics, and execution logs.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {campaigns.length === 0 ? (
              <div className="rounded-md border border-dashed border-white/10 py-10 text-center text-muted-foreground">
                No campaigns created yet.
              </div>
            ) : campaigns.map((campaign) => (
              <button
                key={campaign.id}
                className="w-full rounded-lg border border-white/10 p-4 text-left hover:bg-white/[0.02]"
                onClick={() => selectCampaign(campaign.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium text-foreground/90">{campaign.name}</div>
                  <Badge variant="secondary">{campaign.status}</Badge>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {campaign.sentCount} sent · {campaign.failedCount} failed · {campaign.totalDrafts} drafts
                </div>
              </button>
            ))}

            <div className="rounded-lg border border-white/10 p-4">
              <div className="text-sm font-medium text-foreground/90">Execution Logs</div>
              <div className="mt-3 space-y-2">
                {campaignLogs.length === 0 ? (
                  <div className="text-sm text-muted-foreground">No logs for the selected campaign yet.</div>
                ) : campaignLogs.map((log) => (
                  <div key={log.id} className="rounded-md bg-muted/20 p-3 text-sm">
                    <div className="font-medium text-foreground/90">{log.recipientEmail}</div>
                    <div className="text-xs text-muted-foreground">
                      {log.status} {log.sentAt ? `· ${new Date(log.sentAt).toLocaleString()}` : ''}
                    </div>
                    {log.errorMessage && (
                      <div className="mt-1 text-xs text-red-300">{log.errorMessage}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
