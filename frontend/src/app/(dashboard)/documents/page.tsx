'use client'

import * as React from "react"
import { FileUp, FileText, RefreshCcw, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { documentsService } from "@/features/documents/services/documents-service"
import { DocumentDetail, DocumentItem } from "@/types"
import { useNotificationStore } from "@/store/use-notification-store"

export default function DocumentsPage() {
  const [documents, setDocuments] = React.useState<DocumentItem[]>([])
  const [selected, setSelected] = React.useState<DocumentDetail | null>(null)
  const [uploading, setUploading] = React.useState(false)
  const [replacingId, setReplacingId] = React.useState<string | null>(null)
  const addNotification = useNotificationStore((s) => s.addNotification)

  const loadDocuments = React.useCallback(async () => {
    try {
      const items = await documentsService.list()
      setDocuments(items)
      if (items[0]) {
        const detail = await documentsService.get(items[0].id)
        setSelected(detail)
      }
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Failed to load documents', description: error.message })
    }
  }, [addNotification])

  React.useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const uploaded = await documentsService.upload(file)
      setDocuments((current) => [uploaded, ...current])
      setSelected(await documentsService.get(uploaded.id))
      addNotification({ type: 'success', message: 'Document uploaded', description: uploaded.filename })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Upload failed', description: error.message })
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  const handleSelect = async (documentId: string) => {
    setSelected(await documentsService.get(documentId))
  }

  const handleReplace = async (documentId: string, file?: File) => {
    if (!file) return
    setReplacingId(documentId)
    try {
      const updated = await documentsService.replace(documentId, { file })
      setDocuments((current) => current.map((item) => item.id === documentId ? updated : item))
      setSelected(await documentsService.get(documentId))
      addNotification({ type: 'success', message: 'Document replaced', description: updated.filename })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Replace failed', description: error.message })
    } finally {
      setReplacingId(null)
    }
  }

  const handleDelete = async (documentId: string) => {
    if (!confirm('Delete this document?')) return
    try {
      await documentsService.remove(documentId)
      const remaining = documents.filter((item) => item.id !== documentId)
      setDocuments(remaining)
      setSelected(remaining[0] ? await documentsService.get(remaining[0].id) : null)
      addNotification({ type: 'success', message: 'Document deleted' })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Delete failed', description: error.message })
    }
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Documents</h1>
          <p className="mt-1 text-muted-foreground">Upload supporting PDF, DOCX, or TXT files used for personalized drafting.</p>
        </div>
        <label className="inline-flex cursor-pointer">
          <input type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={handleUpload} />
          <Button variant="accent" className="gap-2" disabled={uploading}>
            <FileUp className="h-4 w-4" />
            {uploading ? 'Uploading...' : 'Upload Document'}
          </Button>
        </label>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.1fr_1.4fr]">
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Files</CardTitle>
            <CardDescription>Stored with metadata and preview support.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {documents.length === 0 ? (
              <div className="rounded-md border border-dashed border-white/10 py-12 text-center text-muted-foreground">
                No documents uploaded yet.
              </div>
            ) : documents.map((document) => (
              <div
                key={document.id}
                className="rounded-lg border border-white/10 p-4 hover:bg-white/[0.02]"
              >
                <button className="w-full text-left" onClick={() => handleSelect(document.id)}>
                  <div className="font-medium text-foreground/90">{document.filename}</div>
                  <div className="text-xs text-muted-foreground">
                    {document.mimeType} · {(document.size / 1024).toFixed(1)} KB
                  </div>
                </button>
                <div className="mt-3 flex gap-2">
                  <label className="cursor-pointer">
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.docx,.txt"
                      onChange={(event) => handleReplace(document.id, event.target.files?.[0])}
                    />
                    <Button variant="outline" size="sm" className="gap-1" disabled={replacingId === document.id}>
                      <RefreshCcw className="h-3.5 w-3.5" />
                      Replace
                    </Button>
                  </label>
                  <Button variant="outline" size="sm" className="gap-1 text-red-300" onClick={() => handleDelete(document.id)}>
                    <Trash2 className="h-3.5 w-3.5" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
            <CardDescription>Metadata and extracted preview text for the selected file.</CardDescription>
          </CardHeader>
          <CardContent>
            {selected ? (
              <div className="space-y-4">
                <div className="rounded-lg border border-white/10 p-4">
                  <div className="font-medium text-foreground/90">{selected.document.filename}</div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    Uploaded {selected.document.uploadedAt ? new Date(selected.document.uploadedAt).toLocaleString() : 'recently'}
                  </div>
                </div>
                <a href={selected.previewUrl} target="_blank" rel="noreferrer">
                  <Button variant="outline" className="gap-2">
                    <FileText className="h-4 w-4" />
                    Open Original Preview
                  </Button>
                </a>
                <div className="rounded-lg border border-white/10 bg-muted/20 p-4 text-sm leading-6 text-muted-foreground whitespace-pre-wrap">
                  {selected.document.previewText || 'No text preview was extracted for this file.'}
                </div>
              </div>
            ) : (
              <div className="rounded-md border border-dashed border-white/10 py-12 text-center text-muted-foreground">
                Select a document to preview it.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
