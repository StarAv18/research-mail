'use client'

import * as React from "react"
import { Search, Loader2, Mail, Globe, BookOpen, UserPlus } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { discoveryService } from "@/features/discovery/services/discovery-service"
import { useNotificationStore } from "@/store/use-notification-store"
import { Professor } from "@/types"

export default function DiscoveryPage() {
  const [url, setUrl] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [professor, setProfessor] = React.useState<Professor | null>(null)
  const addNotification = useNotificationStore((s) => s.addNotification)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url) return

    setLoading(true)
    try {
      const data = await discoveryService.scrapeProfessor(url)
      setProfessor(data)
      addNotification({
        type: 'success',
        message: 'Professor profile analyzed',
        description: `Successfully extracted data for ${data.name}`
      })
    } catch (error: any) {
      addNotification({
        type: 'error',
        message: 'Analysis failed',
        description: error.message
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground/90">Discover Professors</h1>
        <p className="text-muted-foreground mt-1">Enter a university profile URL to analyze research interests and generate outreach.</p>
      </div>

      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="relative flex-1">
              <Globe className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input 
                placeholder="https://profiles.stanford.edu/name..." 
                className="pl-10 h-12 bg-background/50 border-white/10 focus:border-primary/50"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
              />
            </div>
            <Button type="submit" variant="accent" className="h-12 px-8 gap-2" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Analyze Profile
            </Button>
          </form>
        </CardContent>
      </Card>

      {professor && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3 animate-in slide-in-from-bottom-4 duration-500">
          {/* Profile Card */}
          <Card className="lg:col-span-1 h-fit">
            <CardHeader className="text-center">
              <div className="mx-auto h-24 w-24 rounded-full bg-gradient-to-tr from-primary to-accent p-1 shadow-accent-glow">
                <div className="h-full w-full rounded-full bg-muted flex items-center justify-center">
                  <UserPlus className="h-10 w-10 text-primary" />
                </div>
              </div>
              <CardTitle className="mt-4 text-2xl">{professor.name}</CardTitle>
              <CardDescription>{professor.university}</CardDescription>
              <div className="flex justify-center gap-2 mt-2">
                <Badge variant="secondary">{professor.department || "Faculty"}</Badge>
                {professor.country && <Badge variant="outline">{professor.country}</Badge>}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Mail className="h-4 w-4 text-primary" />
                {professor.email || "Email not found"}
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Globe className="h-4 w-4 text-primary" />
                <a href={professor.website} target="_blank" className="hover:text-primary transition-colors truncate">
                  {professor.website}
                </a>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full gap-2" variant="primary">
                Generate Outreach Email
              </Button>
            </CardFooter>
          </Card>

          {/* Details Card */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2 text-primary">
                <BookOpen className="h-5 w-5" />
                <h3 className="text-xl font-bold">Research & Interests</h3>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">Key Interests</h4>
                <div className="flex flex-wrap gap-2">
                  {professor.researchInterests.length > 0 ? (
                    professor.researchInterests.map((interest) => (
                      <Badge key={interest} variant="accent" className="px-3 py-1">
                        {interest}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-sm text-muted-foreground italic">No interests extracted yet</span>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">Biography / Research Text</h4>
                <div className="rounded-xl bg-muted/30 p-4 border border-white/5 max-h-[400px] overflow-y-auto">
                  <p className="text-sm leading-relaxed text-foreground/80 whitespace-pre-wrap">
                    {professor.biography || "No research text available for analysis."}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {!professor && !loading && (
        <Card className="border-dashed border-white/10 bg-transparent py-20">
          <CardContent className="flex flex-col items-center justify-center text-center space-y-4">
            <div className="rounded-full bg-muted p-4">
              <Globe className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <p className="text-lg font-medium text-foreground/70">No professor analyzed yet</p>
              <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                Paste a link from a university faculty directory to start your outreach process.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
