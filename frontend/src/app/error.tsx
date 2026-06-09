'use client'

import * as React from 'react'
import { AlertCircle, RotateCcw, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  React.useEffect(() => {
    // Log the error to an error reporting service
    console.error('Unhandled Application Error:', error)
  }, [error])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center px-4 animate-in fade-in duration-500">
      <div className="rounded-full bg-red-500/10 p-4 mb-6">
        <AlertCircle className="h-12 w-12 text-red-500" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight text-foreground/90 mb-2">
        Something went wrong
      </h1>
      <p className="text-muted-foreground max-w-md mb-8">
        An unexpected error occurred in the application. We've been notified and are looking into it.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 w-full max-w-xs">
        <Button 
          variant="primary" 
          onClick={() => reset()}
          className="gap-2"
        >
          <RotateCcw className="h-4 w-4" />
          Try again
        </Button>
        <Button 
          variant="outline" 
          onClick={() => window.location.href = '/'}
          className="gap-2"
        >
          <Home className="h-4 w-4" />
          Go home
        </Button>
      </div>
    </div>
  )
}
