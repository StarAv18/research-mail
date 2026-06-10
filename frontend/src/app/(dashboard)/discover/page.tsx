'use client'

import * as React from "react"
import { Search, Loader2, Mail, Globe, BookOpen, ExternalLink, FilePlus2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { discoveryService } from "@/features/discovery/services/discovery-service"
import { draftsService } from "@/features/drafts/services/drafts-service"
import { useNotificationStore } from "@/store/use-notification-store"
import { Professor, ProfessorSearchResult } from "@/types"

export default function DiscoveryPage() {
  const [profileUrl, setProfileUrl] = React.useState("")
  const [researchArea, setResearchArea] = React.useState("")
  const [institution, setInstitution] = React.useState("")
  const [country, setCountry] = React.useState("")
  const [region, setRegion] = React.useState("")
  const [senderName, setSenderName] = React.useState("")
  const [senderUniversity, setSenderUniversity] = React.useState("")
  const [senderBackground, setSenderBackground] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [drafting, setDrafting] = React.useState(false)
  const [professor, setProfessor] = React.useState<Professor | null>(null)
  const [results, setResults] = React.useState<ProfessorSearchResult[]>([])
  const addNotification = useNotificationStore((s) => s.addNotification)

  const handleAnalyzeUrl = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!profileUrl) return

    setLoading(true)
    try {
      const data = await discoveryService.scrapeProfessor(profileUrl)
      setProfessor(data)
      setResults([{
        name: data.name,
        university: data.university,
        department: data.department,
        email: data.email,
        website: data.website,
        researchInterests: data.researchInterests,
        recentWork: data.biography || "",
        biography: data.biography || "",
      }])
      addNotification({
        type: 'success',
        message: 'Professor profile analyzed',
        description: `Successfully extracted data for ${data.name}`
      })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Analysis failed', description: error.message })
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setProfessor(null)
    try {
      const data = await discoveryService.searchProfessors({
        researchArea,
        institution,
        country,
        region,
        limit: 10,
      })
      setResults(data.professors)
      addNotification({
        type: data.count > 0 ? 'success' : 'info',
        message: `${data.count} professors found`,
        description: data.query,
      })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Search failed', description: error.message })
    } finally {
      setLoading(false)
    }
  }

  const createDrafts = async () => {
    const professorsWithEmail = results.filter((item) => item.email)
    if (professorsWithEmail.length === 0) {
      addNotification({ type: 'warning', message: 'No professor emails found', description: 'Drafts require an email address.' })
      return
    }

    setDrafting(true)
    try {
      const drafts = await draftsService.generateDrafts(professorsWithEmail, {
        senderName: senderName || "A prospective research intern",
        senderUniversity: senderUniversity || "my university",
        senderBackground: senderBackground || "I have relevant technical and research experience and would be excited to contribute to your work.",
      })
      addNotification({ type: 'success', message: `${drafts.length} drafts created`, description: 'Review them in Email Drafts.' })
    } catch (error: any) {
      addNotification({ type: 'error', message: 'Draft generation failed', description: error.message })
    } finally {
      setDrafting(false)
    }
  }

  return (
    <div className="animate-in space-y-8 fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Discover Professors</h1>
        <p className="mt-1 text-muted-foreground">Search by research area, institution, country, or region, then scrape profiles and create outreach drafts.</p>
      </div>

      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-xl">Search the Web</CardTitle>
          <CardDescription>Use public search results and faculty pages to find professors.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="grid grid-cols-1 gap-3 lg:grid-cols-5">
            <Input placeholder="Research area, e.g. computer vision" value={researchArea} onChange={(e) => setResearchArea(e.target.value)} />
            <Input placeholder="Institute, e.g. Stanford" value={institution} onChange={(e) => setInstitution(e.target.value)} />
            <Input placeholder="Country, e.g. USA" value={country} onChange={(e) => setCountry(e.target.value)} />
            <Input placeholder="Region, e.g. California" value={region} onChange={(e) => setRegion(e.target.value)} />
            <Button type="submit" variant="accent" className="gap-2" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Analyze a Specific Profile</CardTitle>
          <CardDescription>Paste a faculty profile URL when you already know the professor page.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAnalyzeUrl} className="flex flex-col gap-4 sm:flex-row">
            <div className="relative flex-1">
              <Globe className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <Input
                placeholder="https://profiles.stanford.edu/name..."
                className="h-12 border-white/10 bg-white pl-10 text-slate-950 placeholder:text-slate-400 focus:border-primary/50"
                value={profileUrl}
                onChange={(e) => setProfileUrl(e.target.value)}
                disabled={loading}
              />
            </div>
            <Button type="submit" variant="accent" className="h-12 gap-2 px-8" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Analyze Profile
            </Button>
          </form>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card>
          <CardHeader className="gap-4 border-b border-white/5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <CardTitle className="text-xl">Professors Found ({results.length})</CardTitle>
                <CardDescription>Review scraped interests and recent work before drafting outreach.</CardDescription>
              </div>
              <Button className="gap-2" variant="accent" onClick={createDrafts} disabled={drafting}>
                {drafting ? <Loader2 className="h-4 w-4 animate-spin" /> : <FilePlus2 className="h-4 w-4" />}
                Create Email Drafts
              </Button>
            </div>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              <Input placeholder="Your name" value={senderName} onChange={(e) => setSenderName(e.target.value)} />
              <Input placeholder="Your university" value={senderUniversity} onChange={(e) => setSenderUniversity(e.target.value)} />
              <Input placeholder="Your background / skills" value={senderBackground} onChange={(e) => setSenderBackground(e.target.value)} />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-white/5 bg-muted/20 text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Professor</th>
                    <th className="px-6 py-4 font-semibold">Interests</th>
                    <th className="px-6 py-4 font-semibold">Recent Work</th>
                    <th className="px-6 py-4 font-semibold">Contact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {results.map((item, index) => (
                    <tr key={`${item.website}-${index}`} className="align-top hover:bg-white/[0.02]">
                      <td className="px-6 py-4">
                        <div className="font-medium text-foreground/90">{item.name}</div>
                        <div className="text-xs text-muted-foreground">{item.university}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex max-w-sm flex-wrap gap-1.5">
                          {item.researchInterests.length > 0 ? item.researchInterests.map((interest) => (
                            <Badge key={interest} variant="accent">{interest}</Badge>
                          )) : <span className="text-muted-foreground">Not extracted</span>}
                        </div>
                      </td>
                      <td className="max-w-xl px-6 py-4 text-muted-foreground">
                        {item.recentWork || item.biography || "No recent work extracted yet."}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-2">
                          <span className="flex items-center gap-2 text-muted-foreground"><Mail className="h-4 w-4 text-primary" />{item.email || "No email found"}</span>
                          {item.website && (
                            <a href={item.website} target="_blank" className="flex items-center gap-2 text-primary hover:underline">
                              <ExternalLink className="h-4 w-4" />
                              Profile
                            </a>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {!professor && results.length === 0 && !loading && (
        <Card className="border-dashed border-white/10 bg-transparent py-20">
          <CardContent className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="rounded-full bg-muted p-4">
              <BookOpen className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <p className="text-lg font-medium text-foreground/70">No professors searched yet</p>
              <p className="mx-auto max-w-xs text-sm text-muted-foreground">
                Search a topic and institution to build a professor list.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
