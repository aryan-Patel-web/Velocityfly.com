"use client"

import { useState, useEffect } from "react"

const sections = [
  { id: "hero", name: "Home" },
  { id: "platforms", name: "Platforms" },
  { id: "features", name: "Features" },
  { id: "youtube", name: "YouTube" },
  { id: "youtube-features", name: "YT Features" },
  { id: "stats", name: "Stats" },
  { id: "testimonials", name: "Reviews" },
  { id: "pricing", name: "Pricing" },
  { id: "how-it-works", name: "How It Works" },
  { id: "cta", name: "Get Started" },
]

export default function ScrollProgress() {
  const [activeSection, setActiveSection] = useState(0)
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = (window.scrollY / scrollHeight) * 100
      setScrollProgress(progress)

      const sectionElements = sections.map((s) => document.getElementById(s.id))
      const viewportMiddle = window.scrollY + window.innerHeight / 2

      sectionElements.forEach((el, index) => {
        if (el) {
          const rect = el.getBoundingClientRect()
          const elementTop = rect.top + window.scrollY
          const elementBottom = elementTop + rect.height

          if (viewportMiddle >= elementTop && viewportMiddle < elementBottom) {
            setActiveSection(index)
          }
        }
      })
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const scrollToSection = (id) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <div className="fixed right-4 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col items-center gap-2">
      <div className="relative h-40 w-1 bg-[#1a1625] rounded-full overflow-hidden mb-4">
        <div
          className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#8b5cf6] to-[#06b6d4] rounded-full transition-all duration-300"
          style={{ height: `${scrollProgress}%` }}
        />
      </div>

      {sections.map((section, index) => (
        <button
          key={section.id}
          onClick={() => scrollToSection(section.id)}
          className={`group relative flex items-center justify-center w-3 h-3 rounded-full transition-all duration-300 ${
            activeSection === index ? "bg-[#8b5cf6] scale-125 glow-box" : "bg-[#1a1625] hover:bg-[#8b5cf6]/50"
          }`}
        >
          <span className="absolute right-6 whitespace-nowrap text-xs text-white/70 opacity-0 group-hover:opacity-100 transition-opacity bg-[#1a1625] px-2 py-1 rounded">
            {section.name}
          </span>
        </button>
      ))}

      <div className="mt-4 text-xs text-white/50 font-mono">{String(activeSection + 1).padStart(2, "0")}/10</div>
    </div>
  )
}
