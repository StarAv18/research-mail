'use client'

import * as React from "react"
import { 
  FileText, 
  Search, 
  MoreVertical, 
  Edit2, 
  Trash2, 
  Mail, 
  ExternalLink,
  CheckCircle2,
  Clock,
  AlertCircle,
  Send
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { draftsService } from "@/features/drafts/services/drafts-service"
import { Draft, DraftStatus } from "@/types"
import { useNotificationStore } from "@/store/use-notification-store"

const statusConfig = {
  [DraftStatus.PENDING]: { icon: Clock, variant: 'secondary' as const, label: 'Pending' },
  [DraftStatus.EDITED]: { icon: Edit2, variant: 'accent' as const, label: 'Edited' },
  [DraftStatus.READY]: { icon: CheckCircle2, variant: 'success' as const, label: 'Ready' },
  [DraftStatus.SENT]: { icon: Mail, variant: 'default' as const, label: 'Sent' },
  [DraftStatus.FAILED]: { icon: AlertCircle, variant: 'destructive' as const, label: 'Failed' },
  [DraftStatus.ARCHIVED]: { icon: FileText, variant: 'outline' as const, label: 'Archived' },
}

export default function DraftsPage() {
  const [drafts, setDrafts] = React.useState<Draft[]>([])
  const [loading, setLoading] = React.useState(true)
  const [search, setSearch] = React.useState("")
  const addNotification = useNotificationStore((s) => s.addNotification)

  const fetchDrafts = React.useCallback(async () => {
    setLoading(true)
    try {
      const data = await draftsService.listDrafts(search)
      setDrafts(data)
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Failed to fetch drafts', description: error.message })
    } finally {
      setLoading(false)
    }
  }, [search, addNotification])

  React.useEffect(() => {
    fetchDrafts()
  }, [fetchDrafts])

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this draft?")) return
    try {
      await draftsService.deleteDraft(id)
      setDrafts(drafts.filter(d => d.id !== id))
      addNotification({ type: 'success', message: 'Draft deleted' })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Delete failed', description: error.message })
    }
  }

  const gmailComposeUrl = (draft: Draft) => {
    const params = new URLSearchParams({
      view: "cm",
      fs: "1",
      to: draft.professorEmail,
      su: draft.subject,
      body: draft.body,
    })
    return `https://mail.google.com/mail/?${params.toString()}`
  }

  const handleSend = async (draft: Draft) => {
    if (!confirm(`Send this email to ${draft.professorEmail} using your saved Gmail app password?`)) return
    try {
      await draftsService.sendWithGmail(draft.id)
      addNotification({ type: 'success', message: 'Email sent', description: draft.professorEmail })
      fetchDrafts()
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Send failed', description: error.message })
    }
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Email Drafts</h1>
          <p className="text-muted-foreground mt-1">Review, edit, and send your personalized outreach emails.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            Bulk Actions
          </Button>
        </div>
      </div>

      <Card className="border-white/5">
        <CardHeader className="border-b border-white/5 pb-6">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input 
              placeholder="Search by name, email, or university..." 
              className="pl-10 bg-muted/30 border-white/10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase text-muted-foreground bg-muted/20 border-b border-white/5">
                <tr>
                  <th className="px-6 py-4 font-semibold">Professor</th>
                  <th className="px-6 py-4 font-semibold">Subject</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Created</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {loading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={5} className="px-6 py-8 h-16 bg-white/5" />
                    </tr>
                  ))
                ) : drafts.length > 0 ? (
                  drafts.map((draft) => {
                    const status = statusConfig[draft.status]
                    return (
                      <tr key={draft.id} className="hover:bg-white/[0.02] transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex flex-col">
                            <span className="font-medium text-foreground/90">{draft.professorName}</span>
                            <span className="text-xs text-muted-foreground">{draft.university}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-muted-foreground line-clamp-1 max-w-[300px]">
                            {draft.subject}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant={status.variant} className="gap-1 px-2 py-0.5">
                            <status.icon className="h-3 w-3" />
                            {status.label}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-muted-foreground">
                          {new Date(draft.createdAt).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-8 w-8 text-red-400 hover:text-red-300 hover:bg-red-400/10"
                              onClick={() => handleDelete(draft.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                            <a href={gmailComposeUrl(draft)} target="_blank" rel="noreferrer">
                              <Button variant="ghost" size="icon" className="h-8 w-8 text-primary" title="Open in Gmail compose">
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </a>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-emerald-400"
                              title="Send with Gmail app password"
                              onClick={() => handleSend(draft)}
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    )
                  })
                ) : (
                  <tr>
                    <td colSpan={5} className="px-6 py-20 text-center text-muted-foreground italic">
                      No drafts found. Try searching or discover new professors to generate emails.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
