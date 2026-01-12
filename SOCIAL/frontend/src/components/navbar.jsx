// "use client"

// import { useState, useEffect, useRef } from "react"
// import { Button } from "@/components/ui/button"
// import { Menu, X, Zap, ChevronDown } from "lucide-react"

// function NavParticles() {
//   const canvasRef = useRef(null)

//   useEffect(() => {
//     const canvas = canvasRef.current
//     if (!canvas) return
//     const ctx = canvas.getContext("2d")
//     let animationFrameId
//     let particles = []

//     const resizeCanvas = () => {
//       canvas.width = window.innerWidth
//       canvas.height = 80
//     }

//     const createParticles = () => {
//       particles = []
//       for (let i = 0; i < 50; i++) {
//         particles.push({
//           x: Math.random() * canvas.width,
//           y: Math.random() * canvas.height,
//           size: Math.random() * 2 + 0.5,
//           speedX: (Math.random() - 0.5) * 0.5,
//           speedY: (Math.random() - 0.5) * 0.3,
//           opacity: Math.random() * 0.5 + 0.2,
//         })
//       }
//     }

//     const animate = () => {
//       ctx.clearRect(0, 0, canvas.width, canvas.height)

//       particles.forEach((particle) => {
//         particle.x += particle.speedX
//         particle.y += particle.speedY

//         if (particle.x < 0) particle.x = canvas.width
//         if (particle.x > canvas.width) particle.x = 0
//         if (particle.y < 0) particle.y = canvas.height
//         if (particle.y > canvas.height) particle.y = 0

//         const gradient = ctx.createRadialGradient(particle.x, particle.y, 0, particle.x, particle.y, particle.size * 2)
//         gradient.addColorStop(0, `rgba(139, 92, 246, ${particle.opacity})`)
//         gradient.addColorStop(1, `rgba(6, 182, 212, 0)`)

//         ctx.beginPath()
//         ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
//         ctx.fillStyle = gradient
//         ctx.fill()
//       })

//       animationFrameId = requestAnimationFrame(animate)
//     }

//     resizeCanvas()
//     createParticles()
//     animate()

//     window.addEventListener("resize", () => {
//       resizeCanvas()
//       createParticles()
//     })

//     return () => {
//       cancelAnimationFrame(animationFrameId)
//       window.removeEventListener("resize", resizeCanvas)
//     }
//   }, [])

//   return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />
// }

// export default function Navbar() {
//   const [isScrolled, setIsScrolled] = useState(false)
//   const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
//   const [activeDropdown, setActiveDropdown] = useState(null)

//   useEffect(() => {
//     const handleScroll = () => {
//       setIsScrolled(window.scrollY > 50)
//     }
//     window.addEventListener("scroll", handleScroll)
//     return () => window.removeEventListener("scroll", handleScroll)
//   }, [])

//   const navLinks = [
//     { name: "Platforms", href: "#platforms" },
//     { name: "Features", href: "#features" },
//     {
//       name: "YouTube",
//       href: "#youtube",
//       dropdown: [
//         { name: "YouTube Studio", href: "#youtube" },
//         { name: "Deep Dive Features", href: "#youtube-features" },
//       ],
//     },
//     { name: "Pricing", href: "#pricing" },
//     { name: "How It Works", href: "#how-it-works" },
//   ]

//   return (
//     <nav
//       className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
//         isScrolled ? "bg-[#0a0a0f]/90 backdrop-blur-xl border-b border-white/5 py-2" : "bg-transparent py-4"
//       }`}
//     >
//       {isScrolled && <NavParticles />}

//       <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[#8b5cf6]/50 to-transparent" />

//       <div className="relative max-w-7xl mx-auto px-6 flex items-center justify-between">
//         <a href="#hero" className="flex items-center gap-3 group">
//           <div className="relative">
//             <div className="absolute inset-0 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] rounded-xl blur-lg opacity-50 group-hover:opacity-100 transition-opacity animate-pulse" />
//             <div className="relative w-11 h-11 rounded-xl bg-gradient-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center overflow-hidden">
//               <div className="absolute inset-0 bg-gradient-to-r from-[#8b5cf6]/0 via-white/20 to-[#8b5cf6]/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
//               <Zap className="w-6 h-6 text-white relative z-10" />
//             </div>
//             <div
//               className="absolute inset-[-4px] rounded-xl border border-[#8b5cf6]/30 animate-spin-slow"
//               style={{ animationDuration: "8s" }}
//             />
//           </div>
//           <div className="flex flex-col">
//             <span className="text-xl font-bold bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
//               VelocityPost
//             </span>
//             <span className="text-[10px] text-[#06b6d4] tracking-widest uppercase">AI Automation</span>
//           </div>
//         </a>

//         <div className="hidden lg:flex items-center gap-1">
//           {navLinks.map((link) => (
//             <div
//               key={link.name}
//               className="relative"
//               onMouseEnter={() => link.dropdown && setActiveDropdown(link.name)}
//               onMouseLeave={() => setActiveDropdown(null)}
//             >
//               <a
//                 href={link.href}
//                 className="px-4 py-2 text-white/70 hover:text-white transition-all relative group flex items-center gap-1 rounded-lg hover:bg-white/5"
//               >
//                 {link.name}
//                 {link.dropdown && <ChevronDown className="w-3 h-3" />}
//                 <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] group-hover:w-3/4 transition-all duration-300 rounded-full" />
//               </a>

//               {link.dropdown && activeDropdown === link.name && (
//                 <div className="absolute top-full left-0 mt-2 w-48 py-2 bg-[#13111c]/95 backdrop-blur-xl rounded-xl border border-white/10 shadow-2xl animate-fade-in">
//                   {link.dropdown.map((item) => (
//                     <a
//                       key={item.name}
//                       href={item.href}
//                       className="block px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
//                     >
//                       {item.name}
//                     </a>
//                   ))}
//                 </div>
//               )}
//             </div>
//           ))}
//         </div>

//         <div className="hidden lg:flex items-center gap-3">
//           <Button
//             variant="ghost"
//             className="text-white/70 hover:text-white hover:bg-white/5 border border-transparent hover:border-white/10"
//           >
//             Log In
//           </Button>
//           <Button className="relative overflow-hidden bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] hover:opacity-90 text-white font-semibold px-6 group">
//             <span className="relative z-10">Start Free Trial</span>
//             <div className="absolute inset-0 bg-gradient-to-r from-[#06b6d4] to-[#8b5cf6] opacity-0 group-hover:opacity-100 transition-opacity" />
//             <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-500" />
//           </Button>
//         </div>

//         <button
//           className="lg:hidden text-white p-2 rounded-lg hover:bg-white/5"
//           onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
//         >
//           {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
//         </button>
//       </div>

//       {isMobileMenuOpen && (
//         <div className="lg:hidden absolute top-full left-4 right-4 mt-2 bg-[#13111c]/95 backdrop-blur-xl rounded-2xl border border-white/10 p-4 animate-fade-in">
//           {navLinks.map((link) => (
//             <div key={link.name}>
//               <a
//                 href={link.href}
//                 className="block py-3 px-4 text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
//                 onClick={() => !link.dropdown && setIsMobileMenuOpen(false)}
//               >
//                 {link.name}
//               </a>
//               {link.dropdown && (
//                 <div className="ml-4 border-l border-white/10 pl-4">
//                   {link.dropdown.map((item) => (
//                     <a
//                       key={item.name}
//                       href={item.href}
//                       className="block py-2 text-sm text-white/50 hover:text-white transition-colors"
//                       onClick={() => setIsMobileMenuOpen(false)}
//                     >
//                       {item.name}
//                     </a>
//                   ))}
//                 </div>
//               )}
//             </div>
//           ))}
//           <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-white/10">
//             <Button variant="ghost" className="w-full justify-center text-white/70">
//               Log In
//             </Button>
//             <Button className="w-full bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4]">Start Free Trial</Button>
//           </div>
//         </div>
//       )}
//     </nav>
//   )
// }



import { useState, useEffect, useRef } from "react"
import { useAuth } from "../quickpage/AuthContext"

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

    const handleResize = () => {
      resizeCanvas()
      createParticles()
    }

    window.addEventListener("resize", handleResize)

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener("resize", handleResize)
    }
  }, [])

  return <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />
}

// Icon Components
const MenuIcon = () => (
  <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"/>
  </svg>
)

const XIcon = () => (
  <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
  </svg>
)

const ZapIcon = () => (
  <svg style={{ width: '24px', height: '24px', color: 'white' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
  </svg>
)

const ChevronDownIcon = ({ size = "16px" }) => (
  <svg style={{ width: size, height: size }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
  </svg>
)

const UserIcon = () => (
  <svg style={{ width: '16px', height: '16px', color: 'white' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
  </svg>
)

const LayoutDashboardIcon = () => (
  <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
  </svg>
)

const LogOutIcon = () => (
  <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
  </svg>
)

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState(null)
  const [showUserMenu, setShowUserMenu] = useState(false)
  
  const { isAuthenticated, user, logout } = useAuth()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
    setIsMobileMenuOpen(false)
    window.location.href = "/"
  }

  const handleLogin = () => {
    window.location.href = "/login"
  }

  const handleSignup = () => {
    window.location.href = "/register"
  }

  const handleDashboard = () => {
    window.location.href = "/youtube"
  }

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

  const navStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 50,
    transition: 'all 0.5s',
    backgroundColor: isScrolled ? 'rgba(10, 10, 15, 0.9)' : 'transparent',
    backdropFilter: isScrolled ? 'blur(40px)' : 'none',
    borderBottom: isScrolled ? '1px solid rgba(255, 255, 255, 0.05)' : 'none',
    padding: isScrolled ? '8px 0' : '16px 0'
  }

  const buttonStyle = {
    padding: '10px 20px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '600',
    transition: 'all 0.2s',
  }

  const primaryButtonStyle = {
    ...buttonStyle,
    background: 'linear-gradient(to right, #8b5cf6, #06b6d4)',
    color: 'white',
  }

  const ghostButtonStyle = {
    ...buttonStyle,
    background: 'transparent',
    color: 'rgba(255, 255, 255, 0.7)',
    border: '1px solid transparent',
  }

  return (
    <nav style={navStyle}>
      {isScrolled && <NavParticles />}

      <div style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        right: 0, 
        height: '1px', 
        background: 'linear-gradient(to right, transparent, rgba(139, 92, 246, 0.5), transparent)' 
      }} />

      <div style={{ 
        position: 'relative', 
        maxWidth: '1280px', 
        margin: '0 auto', 
        padding: '0 24px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between' 
      }}>
        <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
          <div style={{ position: 'relative' }}>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'linear-gradient(to bottom right, #8b5cf6, #06b6d4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <ZapIcon />
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ 
              fontSize: '20px', 
              fontWeight: 'bold', 
              background: 'linear-gradient(to right, white, rgba(255, 255, 255, 0.8))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              VelocityPost
            </span>
            <span style={{ 
              fontSize: '10px', 
              color: '#06b6d4', 
              letterSpacing: '2px', 
              textTransform: 'uppercase' 
            }}>
              AI Automation
            </span>
          </div>
        </a>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {navLinks.map((link) => (
            <div
              key={link.name}
              style={{ position: 'relative' }}
              onMouseEnter={() => link.dropdown && setActiveDropdown(link.name)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <a
                href={link.href}
                style={{
                  padding: '8px 16px',
                  color: 'rgba(255, 255, 255, 0.7)',
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  borderRadius: '8px',
                  transition: 'all 0.2s'
                }}
              >
                {link.name}
                {link.dropdown && <ChevronDownIcon size="12px" />}
              </a>

              {link.dropdown && activeDropdown === link.name && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  marginTop: '8px',
                  width: '192px',
                  padding: '8px 0',
                  background: 'rgba(19, 17, 28, 0.95)',
                  backdropFilter: 'blur(40px)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
                }}>
                  {link.dropdown.map((item) => (
                    <a
                      key={item.name}
                      href={item.href}
                      style={{
                        display: 'block',
                        padding: '8px 16px',
                        fontSize: '14px',
                        color: 'rgba(255, 255, 255, 0.7)',
                        textDecoration: 'none',
                        transition: 'all 0.2s'
                      }}
                    >
                      {item.name}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {isAuthenticated && user ? (
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'linear-gradient(to bottom right, #8b5cf6, #06b6d4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <UserIcon />
                </div>
                <span style={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontSize: '14px',
                  maxWidth: '150px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {user.email || user.name}
                </span>
                <ChevronDownIcon size="16px" />
              </button>

              {showUserMenu && (
                <>
                  <div 
                    style={{ position: 'fixed', inset: 0, zIndex: 40 }} 
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    right: 0,
                    marginTop: '8px',
                    width: '224px',
                    padding: '8px 0',
                    background: 'rgba(19, 17, 28, 0.95)',
                    backdropFilter: 'blur(40px)',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                    zIndex: 50
                  }}>
                    <div style={{
                      padding: '8px 16px',
                      borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <p style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)', margin: 0 }}>Signed in as</p>
                      <p style={{ 
                        fontSize: '14px', 
                        color: 'white', 
                        margin: '4px 0 0 0',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {user.email || user.name}
                      </p>
                    </div>
                    
                    <button
                      onClick={handleDashboard}
                      style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '8px 16px',
                        fontSize: '14px',
                        color: 'rgba(255, 255, 255, 0.7)',
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.2s'
                      }}
                    >
                      <LayoutDashboardIcon />
                      Dashboard
                    </button>
                    
                    <div style={{
                      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                      marginTop: '8px',
                      paddingTop: '8px'
                    }}>
                      <button
                        onClick={handleLogout}
                        style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          padding: '8px 16px',
                          fontSize: '14px',
                          color: '#f87171',
                          background: 'transparent',
                          border: 'none',
                          cursor: 'pointer',
                          textAlign: 'left',
                          transition: 'all 0.2s'
                        }}
                      >
                        <LogOutIcon />
                        Log Out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ) : (
            <>
              <button onClick={handleLogin} style={ghostButtonStyle}>
                Log In
              </button>
              <button onClick={handleSignup} style={primaryButtonStyle}>
                Start Free Trial
              </button>
            </>
          )}
        </div>

        <button
          style={{
            display: 'none',
            color: 'white',
            padding: '8px',
            borderRadius: '8px',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer'
          }}
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <XIcon /> : <MenuIcon />}
        </button>
      </div>

      <style>{`
        @media (max-width: 1024px) {
          nav > div > div:nth-child(2) {
            display: none !important;
          }
          nav > div > div:nth-child(3) {
            display: none !important;
          }
          nav > div > button:last-child {
            display: block !important;
          }
        }
      `}</style>
    </nav>
  )
}