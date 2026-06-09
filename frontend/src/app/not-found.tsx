import * as React from 'react'
import Link from 'next/link'
import { FileQuestion, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center px-4 animate-in fade-in duration-500">
      <div className="rounded-full bg-primary/10 p-4 mb-6">
        <FileQuestion className="h-12 w-12 text-primary" />
      </div>
      <h1 className="text-4xl font-bold tracking-tight text-foreground/90 mb-2">
        404
      </h1>
      <h2 className="text-xl font-semibold text-foreground/80 mb-4">
        Page Not Found
      </h2>
      <p className="text-muted-foreground max-w-md mb-8">
        The page you are looking for doesn&apos;t exist or has been moved to a new URL.
      </p>
      <Button asChild variant="primary" className="gap-2">
        <Link href="/">
          <Home className="h-4 w-4" />
          Back to Dashboard
        </Link>
      </Button>
    </div>
  )
}
