import * as React from "react"
import { BrainCircuit, ArrowUpRight } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export function AISuggestion() {
  return (
    <Card className="bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
      <CardContent className="p-6">
        <h4 className="font-bold text-primary flex items-center gap-2">
          <BrainCircuit className="h-5 w-5" />
          AI Suggestion
        </h4>
        <p className="text-sm mt-3 text-foreground/80 leading-relaxed">
          Based on your experience in **PyTorch**, you might want to look into **Dr. Andrew Ng&apos;s** latest work on efficient LLM fine-tuning.
        </p>
        <Button variant="primary" size="sm" className="w-full mt-4 gap-2">
          View Profile
          <ArrowUpRight className="h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  )
}
