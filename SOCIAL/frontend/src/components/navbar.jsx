"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Menu, X, Zap, ChevronDown } from "lucide-react"

function NavParticles() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    let animationFrameId
    let particles = []

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = 80
    }

    const createParticles = () => {
      particles = []
      for (let i = 0; i < 50; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          size: Math.random() * 2 + 0.5,
          speedX: (Math.random() - 0.5) * 0.5,
          speedY: (Math.random() - 0.5) * 0.3,
          opacity: Math.random() * 0.5 + 0.2,
        })
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particles.forEach((particle) => {
        particle.x += particle.speedX
        particle.y += particle.speedY

        if (particle.x < 0) particle.x = canvas.width
        if (particle.x > canvas.width) particle.x = 0
        if (particle.y < 0) particle.y = canvas.height
        if (particle.y > canvas.height) particle.y = 0

        const gradient = ctx.createRadialGradient(particle.x, particle.y, 0, particle.x, particle.y, particle.size * 2)
        gradient.addColorStop(0, `rgba(139, 92, 246, ${particle.opacity})`)
        gradient.addColorStop(1, `rgba(6, 182, 212, 0)`)

        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()
      })

      animationFrameId = requestAnimationFrame(animate)
    }

    resizeCanvas()
    createParticles()
    animate()

    window.addEventListener("resize", () => {
      resizeCanvas()
      createParticles()
    })

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener("resize", resizeCanvas)
    }
  }, [])

  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />
}

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState(null)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const navLinks = [
    { name: "Platforms", href: "#platforms" },
    { name: "Features", href: "#features" },
    {
      name: "YouTube",
      href: "#youtube",
      dropdown: [
        { name: "YouTube Studio", href: "#youtube" },
        { name: "Deep Dive Features", href: "#youtube-features" },
      ],
    },
    { name: "Pricing", href: "#pricing" },
    { name: "How It Works", href: "#how-it-works" },
  ]

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        isScrolled ? "bg-[#0a0a0f]/90 backdrop-blur-xl border-b border-white/5 py-2" : "bg-transparent py-4"
      }`}
    >
      {isScrolled && <NavParticles />}

      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[#8b5cf6]/50 to-transparent" />

      <div className="relative max-w-7xl mx-auto px-6 flex items-center justify-between">
        <a href="#hero" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] rounded-xl blur-lg opacity-50 group-hover:opacity-100 transition-opacity animate-pulse" />
            <div className="relative w-11 h-11 rounded-xl bg-gradient-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-[#8b5cf6]/0 via-white/20 to-[#8b5cf6]/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
              <Zap className="w-6 h-6 text-white relative z-10" />
            </div>
            <div
              className="absolute inset-[-4px] rounded-xl border border-[#8b5cf6]/30 animate-spin-slow"
              style={{ animationDuration: "8s" }}
            />
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              VelocityPost
            </span>
            <span className="text-[10px] text-[#06b6d4] tracking-widest uppercase">AI Automation</span>
          </div>
        </a>

        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map((link) => (
            <div
              key={link.name}
              className="relative"
              onMouseEnter={() => link.dropdown && setActiveDropdown(link.name)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <a
                href={link.href}
                className="px-4 py-2 text-white/70 hover:text-white transition-all relative group flex items-center gap-1 rounded-lg hover:bg-white/5"
              >
                {link.name}
                {link.dropdown && <ChevronDown className="w-3 h-3" />}
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] group-hover:w-3/4 transition-all duration-300 rounded-full" />
              </a>

              {link.dropdown && activeDropdown === link.name && (
                <div className="absolute top-full left-0 mt-2 w-48 py-2 bg-[#13111c]/95 backdrop-blur-xl rounded-xl border border-white/10 shadow-2xl animate-fade-in">
                  {link.dropdown.map((item) => (
                    <a
                      key={item.name}
                      href={item.href}
                      className="block px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      {item.name}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="hidden lg:flex items-center gap-3">
          <Button
            variant="ghost"
            className="text-white/70 hover:text-white hover:bg-white/5 border border-transparent hover:border-white/10"
          >
            Log In
          </Button>
          <Button className="relative overflow-hidden bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] hover:opacity-90 text-white font-semibold px-6 group">
            <span className="relative z-10">Start Free Trial</span>
            <div className="absolute inset-0 bg-gradient-to-r from-[#06b6d4] to-[#8b5cf6] opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-500" />
          </Button>
        </div>

        <button
          className="lg:hidden text-white p-2 rounded-lg hover:bg-white/5"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {isMobileMenuOpen && (
        <div className="lg:hidden absolute top-full left-4 right-4 mt-2 bg-[#13111c]/95 backdrop-blur-xl rounded-2xl border border-white/10 p-4 animate-fade-in">
          {navLinks.map((link) => (
            <div key={link.name}>
              <a
                href={link.href}
                className="block py-3 px-4 text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                onClick={() => !link.dropdown && setIsMobileMenuOpen(false)}
              >
                {link.name}
              </a>
              {link.dropdown && (
                <div className="ml-4 border-l border-white/10 pl-4">
                  {link.dropdown.map((item) => (
                    <a
                      key={item.name}
                      href={item.href}
                      className="block py-2 text-sm text-white/50 hover:text-white transition-colors"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      {item.name}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
          <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-white/10">
            <Button variant="ghost" className="w-full justify-center text-white/70">
              Log In
            </Button>
            <Button className="w-full bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4]">Start Free Trial</Button>
          </div>
        </div>
      )}
    </nav>
  )
}














