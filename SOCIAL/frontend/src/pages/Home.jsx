// import Navbar from "../components/navbar"
// import HeroSection from "../components/sections/hero-section"
// import PlatformsSection from "../components/sections/platforms-section"
// import FeaturesSection from "../components/sections/features-section"
// import YouTubeSection from "../components/sections/youtube-section"
// import YouTubeFeaturesSection from "../components/sections/youtube-features-section"
// import StatsSection from "../components/sections/stats-section"
// import TestimonialsSection from "../components/sections/testimonials-section"
// import PricingSection from "../components/sections/pricing-section"
// import HowItWorksSection from "../components/sections/how-it-works-section"
// import CTASection from "../components/sections/cta-section"
// import Footer from "../components/footer"
// import ScrollProgress from "../components/scroll-progress"

// export default function Home() {
//   return (
//     <main className="min-h-screen bg-[#0a0a0f] overflow-x-hidden snap-container">
//       <Navbar />
//       <ScrollProgress />
//       <HeroSection />
//       <PlatformsSection />
//       <FeaturesSection />
//       <YouTubeSection />
//       <YouTubeFeaturesSection />
//       <StatsSection />
//       <TestimonialsSection />
//       <PricingSection />
//       <HowItWorksSection />
//       <CTASection />
//       <Footer />
//     </main>
//   )
// }

import { useState, useEffect, useRef } from "react"
import { useAuth } from "../quickpage/AuthContext"

// Simple Navbar Component (inline)
function TestNavbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const [showMenu, setShowMenu] = useState(false)

  const handleLogout = () => {
    logout()
    window.location.href = "/"
  }

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 50,
      background: 'rgba(10, 10, 15, 0.9)',
      backdropFilter: 'blur(40px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
      padding: '16px 0'
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <a href="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          textDecoration: 'none',
          color: 'white',
          fontSize: '20px',
          fontWeight: 'bold'
        }}>
          ⚡ VelocityPost
        </a>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {isAuthenticated && user ? (
            <>
              <span style={{ color: 'white', fontSize: '14px' }}>
                {user.email}
              </span>
              <button
                onClick={() => window.location.href = '/youtube'}
                style={{
                  padding: '8px 16px',
                  background: 'linear-gradient(to right, #8b5cf6, #06b6d4)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Dashboard
              </button>
              <button
                onClick={handleLogout}
                style={{
                  padding: '8px 16px',
                  background: '#dc2626',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => window.location.href = '/login'}
                style={{
                  padding: '8px 16px',
                  background: 'transparent',
                  color: 'rgba(255, 255, 255, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Log In
              </button>
              <button
                onClick={() => window.location.href = '/register'}
                style={{
                  padding: '8px 16px',
                  background: 'linear-gradient(to right, #8b5cf6, #06b6d4)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Start Free Trial
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

// Simple Hero Section
function TestHero() {
  return (
    <section style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%)',
      padding: '80px 24px'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '800px' }}>
        <h1 style={{
          fontSize: '64px',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #8b5cf6, #06b6d4)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '24px'
        }}>
          Automate Your Social Media
        </h1>
        <p style={{
          fontSize: '20px',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '32px'
        }}>
          Post to YouTube, Reddit, Instagram, Facebook, and WhatsApp with AI-powered automation
        </p>
        <button
          onClick={() => window.location.href = '/register'}
          style={{
            padding: '16px 32px',
            background: 'linear-gradient(to right, #8b5cf6, #06b6d4)',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '18px',
            fontWeight: 'bold'
          }}
        >
          Get Started Free
        </button>
      </div>
    </section>
  )
}

// Simple Features Section
function TestFeatures() {
  const features = [
    { emoji: '📺', title: 'YouTube Automation', desc: 'Auto-upload videos with AI' },
    { emoji: '🔴', title: 'Reddit Posts', desc: 'Schedule and post automatically' },
    { emoji: '📸', title: 'Instagram', desc: 'Stories, posts, and reels' },
    { emoji: '📘', title: 'Facebook', desc: 'Pages and groups automation' },
    { emoji: '💬', title: 'WhatsApp', desc: 'Bulk messaging made easy' }
  ]

  return (
    <section style={{
      minHeight: '100vh',
      padding: '80px 24px',
      background: '#0a0a0f'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{
          fontSize: '48px',
          fontWeight: 'bold',
          textAlign: 'center',
          color: 'white',
          marginBottom: '64px'
        }}>
          All Platforms, One Dashboard
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '24px'
        }}>
          {features.map((feature, i) => (
            <div key={i} style={{
              padding: '32px',
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '16px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>
                {feature.emoji}
              </div>
              <h3 style={{ color: 'white', fontSize: '20px', marginBottom: '8px' }}>
                {feature.title}
              </h3>
              <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '14px' }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Simple Footer
function TestFooter() {
  return (
    <footer style={{
      padding: '40px 24px',
      background: '#000',
      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
      textAlign: 'center',
      color: 'rgba(255, 255, 255, 0.5)'
    }}>
      <p>© 2025 VelocityPost. All rights reserved.</p>
    </footer>
  )
}

// Main Home Component
export default function Home() {
  return (
    <main style={{ minHeight: '100vh', background: '#0a0a0f' }}>
      <TestNavbar />
      <TestHero />
      <TestFeatures />
      <TestFooter />
    </main>
  )
}