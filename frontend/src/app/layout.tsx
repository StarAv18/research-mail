import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "@/styles/globals.css"
import { ToastContainer } from "@/components/shared/toast"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Research Internship Agent",
  description: "Premium AI-powered research internship platform",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        {children}
        <ToastContainer />
      </body>
    </html>
  )
}
