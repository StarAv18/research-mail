import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'accent'
  size?: 'sm' | 'md' | 'lg' | 'icon'
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', asChild = false, ...props }, ref) => {
    const variants = {
      primary: 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-soft-glow',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
      outline: 'border border-primary/50 bg-transparent hover:bg-primary/10 text-primary',
      ghost: 'hover:bg-accent/10 text-accent',
      accent: 'bg-accent text-accent-foreground hover:bg-accent/90 shadow-accent-glow',
    }

    const sizes = {
      sm: 'h-8 px-3 text-xs',
      md: 'h-10 px-4 py-2',
      lg: 'h-12 px-8 text-base',
      icon: 'h-10 w-10',
    }

    const Comp = asChild ? React.Fragment : "button"
    const content = (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50 active:scale-95",
          variants[variant],
          sizes[size],
          className
        )}
        ref={ref}
        {...props}
      />
    )

    if (asChild) {
      // Simplified asChild implementation for this context
      // In a full implementation, we'd use Slot from @radix-ui/react-slot
      const { children, ...rest } = props
      if (React.isValidElement(children)) {
        return React.cloneElement(children, {
          ...rest,
          className: cn(
            "inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50 active:scale-95",
            variants[variant],
            sizes[size],
            className,
            (children.props as any).className
          ),
          ref
        } as any)
      }
    }

    return content
  }
)
Button.displayName = "Button"

export { Button }
