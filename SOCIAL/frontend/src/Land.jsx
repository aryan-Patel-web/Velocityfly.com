import Navbar from "../components/navbar"
import HeroSection from "../components/sections/hero-section"
import PlatformsSection from "../components/sections/platforms-section"
import FeaturesSection from "../components/sections/features-section"
import YouTubeSection from "../components/sections/youtube-section"
import YouTubeFeaturesSection from "../components/sections/youtube-features-section"
import StatsSection from "../components/sections/stats-section"
import TestimonialsSection from "../components/sections/testimonials-section"
import PricingSection from "../components/sections/pricing-section"
import HowItWorksSection from "../components/sections/how-it-works-section"
import CTASection from "../components/sections/cta-section"
import Footer from "../components/footer"
import ScrollProgress from "../components/scroll-progress"

export default function Land() {
  return (
    <main className="min-h-screen bg-[#0a0a0f] overflow-x-hidden snap-container">
      <Navbar />
      <ScrollProgress />
      <HeroSection />
      <PlatformsSection />
      <FeaturesSection />
      <YouTubeSection />
      <YouTubeFeaturesSection />
      <StatsSection />
      <TestimonialsSection />
      <PricingSection />
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </main>
  )
}
