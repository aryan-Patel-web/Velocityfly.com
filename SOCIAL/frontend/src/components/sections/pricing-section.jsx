"use client"

import { useState, useRef } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Float, Cylinder, MeshDistortMaterial } from "@react-three/drei"
import { Button } from "@/components/ui/button"
import { Check, Sparkles, Zap, Crown, Building2, Clock } from "lucide-react"

function FloatingPlatform({ position, scale, color, isHighlighted }) {
  const platformRef = useRef()
  const beamRef = useRef()

  useFrame((state) => {
    if (platformRef.current) {
      platformRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + position[0]) * 0.3
      platformRef.current.rotation.y = state.clock.elapsedTime * 0.15
    }
    if (beamRef.current && isHighlighted) {
      beamRef.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.3
    }
  })

  return (
    <group>
      <Float speed={1} floatIntensity={0.5}>
        <Cylinder ref={platformRef} args={[1.5 * scale, 1.8 * scale, 0.4, 32]} position={position}>
          <MeshDistortMaterial
            color={color}
            distort={0.15}
            speed={2}
            roughness={0.3}
            metalness={0.7}
            emissive={color}
            emissiveIntensity={isHighlighted ? 0.6 : 0.2}
          />
        </Cylinder>
      </Float>
      {isHighlighted && (
        <Cylinder ref={beamRef} args={[0.3, 0.3, 6, 16]} position={[position[0], position[1] - 3, position[2]]}>
          <meshBasicMaterial color={color} transparent opacity={0.3} />
        </Cylinder>
      )}
    </group>
  )
}

function ParticleFountain({ position, color }) {
  const particlesRef = useRef()
  const count = 50

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array
      for (let i = 0; i < count; i++) {
        positions[i * 3 + 1] += 0.02
        if (positions[i * 3 + 1] > 3) {
          positions[i * 3 + 1] = 0
        }
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  const positions = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    positions[i * 3] = position[0] + (Math.random() - 0.5) * 0.5
    positions[i * 3 + 1] = Math.random() * 3
    positions[i * 3 + 2] = position[2] + (Math.random() - 0.5) * 0.5
  }

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.05} color={color} transparent opacity={0.6} />
    </points>
  )
}

function PricingScene({ highlightedTier }) {
  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 10, 5]} intensity={1.5} color="#8B5CF6" />
      <pointLight position={[-5, 5, 5]} intensity={0.8} color="#06B6D4" />
      <FloatingPlatform position={[-5, -1, 0]} scale={0.7} color="#8B5CF6" isHighlighted={highlightedTier === 0} />
      <FloatingPlatform position={[-1.7, 1.5, 0]} scale={1.1} color="#A855F7" isHighlighted={highlightedTier === 1} />
      <FloatingPlatform position={[1.7, 0.5, 0]} scale={0.9} color="#06B6D4" isHighlighted={highlightedTier === 2} />
      <FloatingPlatform position={[5, 0, 0]} scale={0.8} color="#3B82F6" isHighlighted={highlightedTier === 3} />
      {highlightedTier !== null && (
        <ParticleFountain
          position={[[-5, -1.7, 1.7, 5][highlightedTier], 0, 0]}
          color={["#8B5CF6", "#A855F7", "#06B6D4", "#3B82F6"][highlightedTier]}
        />
      )}
    </>
  )
}

function PricingCard({ plan, isPopular, isHovered, onHover, index }) {
  const {
    name,
    priceINR,
    priceUSD,
    period,
    yearlyINR,
    weeklyINR,
    description,
    features,
    icon: Icon,
    cta,
    target,
  } = plan

  return (
    <div
      className={`relative group transition-all duration-500 ${isHovered ? "scale-105 z-10" : ""} ${isPopular ? "lg:-mt-4" : ""}`}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
    >
      {isPopular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] rounded-full text-xs font-bold text-white flex items-center gap-1 z-10">
          <Sparkles className="w-3 h-3" /> MOST POPULAR
        </div>
      )}

      <div
        className={`glass rounded-3xl p-6 lg:p-8 h-full ${isPopular ? "glow-box border-[#8b5cf6]/50" : "glow-border"} transition-all duration-300`}
      >
        <div className="flex items-center gap-3 mb-4">
          <div
            className={`w-12 h-12 rounded-xl ${isPopular ? "bg-gradient-to-br from-[#8b5cf6] to-[#06b6d4]" : "bg-[#8b5cf6]/20"} flex items-center justify-center`}
          >
            <Icon className={`w-6 h-6 ${isPopular ? "text-white" : "text-[#8b5cf6]"}`} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">{name}</h3>
            <p className="text-sm text-white/50">{description}</p>
          </div>
        </div>

        <div className="mb-2">
          <span className="text-4xl lg:text-5xl font-bold gradient-text">{priceINR}</span>
          {period && <span className="text-white/50">/{period}</span>}
        </div>
        {priceUSD && <p className="text-sm text-white/40 mb-1">{priceUSD}/month</p>}
        {yearlyINR && <p className="text-xs text-[#06b6d4] mb-1">{yearlyINR}/year (Save 17%)</p>}
        {weeklyINR && <p className="text-xs text-white/40 mb-4">{weeklyINR}/week (Trial)</p>}

        <ul className="space-y-3 mb-6 mt-4">
          {features.map((feature, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <div className="w-5 h-5 rounded-full bg-[#8b5cf6]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Check className="w-3 h-3 text-[#8b5cf6]" />
              </div>
              <span className="text-white/70 text-sm">{feature}</span>
            </li>
          ))}
        </ul>

        <div className="mb-4 p-3 bg-[#1a1625]/50 rounded-xl">
          <div className="flex items-center gap-2 text-xs text-white/50">
            <Clock className="w-3 h-3" />
            <span>{target}</span>
          </div>
        </div>

        <Button
          className={`w-full py-5 text-base ${
            isPopular
              ? "bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] hover:opacity-90"
              : "bg-[#1a1625] hover:bg-[#1a1625]/80 border border-[#8b5cf6]/30"
          }`}
        >
          {cta}
        </Button>
      </div>
    </div>
  )
}

export default function PricingSection() {
  const [hoveredIndex, setHoveredIndex] = useState(null)

  const plans = [
    {
      name: "Basic",
      priceINR: "₹349",
      priceUSD: "$4",
      period: "mo",
      yearlyINR: "₹3,490",
      weeklyINR: "₹99",
      description: "For beginners",
      icon: Zap,
      cta: "Start Free Trial",
      target: "Perfect for: Solo creators, Students, Beginners",
      features: [
        "1 Social Account",
        "50 Posts per Month",
        "AI Content Generator",
        "YouTube Automation",
        "Smart Scheduling",
        "Basic Analytics",
        "Email Support",
        "5 hours saved/week",
      ],
    },
    {
      name: "Pro",
      priceINR: "₹749",
      priceUSD: "$9",
      period: "mo",
      yearlyINR: "₹7,490",
      weeklyINR: "₹199",
      description: "Most Popular",
      icon: Sparkles,
      cta: "Start Free Trial",
      target: "Perfect for: Growing YouTubers, Small business, Marketers",
      features: [
        "3 Social Accounts",
        "500 Posts per Month",
        "Everything in Basic +",
        "AI Thumbnails (3 designs)",
        "Comment Auto-Reply",
        "Multi-Platform Sync",
        "Image Slideshow Creator",
        "Schedule 100 posts at once",
        "Priority Support 24/7",
        "15 hours saved/week",
      ],
    },
    {
      name: "Advance",
      priceINR: "₹1,499",
      priceUSD: "$18",
      period: "mo",
      yearlyINR: "₹14,990",
      weeklyINR: "₹399",
      description: "For pros",
      icon: Crown,
      cta: "Start Free Trial",
      target: "Perfect for: Pro creators, Agencies, Teams",
      features: [
        "10 Social Accounts",
        "Unlimited Posts",
        "Everything in Pro +",
        "Priority Support (24/7)",
        "Advanced Analytics",
        "Team Collaboration (5 users)",
        "Instagram Reels Auto",
        "Reddit + WhatsApp Auto",
        "Bulk Upload (500/day)",
        "A/B Testing",
        "30 hours saved/week",
      ],
    },
    {
      name: "Enterprise",
      priceINR: "Custom",
      priceUSD: null,
      period: null,
      yearlyINR: null,
      weeklyINR: null,
      description: "For large teams",
      icon: Building2,
      cta: "Contact Sales",
      target: "Perfect for: Agencies, Large brands, 100+ accounts",
      features: [
        "Unlimited Accounts",
        "Unlimited Everything",
        "Dedicated Account Manager",
        "Custom AI Training",
        "White Label Options",
        "API Access",
        "Custom Integrations",
        "SLA Guarantee",
        "Onboarding Training",
      ],
    },
  ]

  return (
    <section id="pricing" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0 opacity-40">
        <Canvas camera={{ position: [0, 5, 14], fov: 50 }}>
          <PricingScene highlightedTier={hoveredIndex} />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-transparent to-[#0a0a0f] z-10" />

      <div className="relative z-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6">
            ELEVATION PLATFORMS
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">Simple Pricing for</span>
            <br />
            <span className="gradient-text">Every Creator</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">Start free. Scale as you grow. Cancel anytime.</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan, index) => (
            <PricingCard
              key={index}
              plan={plan}
              index={index}
              isPopular={index === 1}
              isHovered={hoveredIndex === index}
              onHover={(isHovered) => setHoveredIndex(isHovered ? index : null)}
            />
          ))}
        </div>

        <div className="mt-12 text-center">
          <div className="glass rounded-2xl p-6 max-w-3xl mx-auto">
            <p className="text-white font-medium mb-4">All Plans Include:</p>
            <div className="flex flex-wrap justify-center gap-4 text-sm text-white/60">
              <span className="flex items-center gap-1">
                <Check className="w-4 h-4 text-[#06b6d4]" /> 14-Day Free Trial
              </span>
              <span className="flex items-center gap-1">
                <Check className="w-4 h-4 text-[#06b6d4]" /> No Credit Card Required
              </span>
              <span className="flex items-center gap-1">
                <Check className="w-4 h-4 text-[#06b6d4]" /> Cancel Anytime
              </span>
              <span className="flex items-center gap-1">
                <Check className="w-4 h-4 text-[#06b6d4]" /> 24/7 Uptime
              </span>
              <span className="flex items-center gap-1">
                <Check className="w-4 h-4 text-[#06b6d4]" /> Indian Payment Support
              </span>
            </div>
            <p className="text-xs text-white/40 mt-4">
              🔒 Secure Payment • 🇮🇳 Made for India • 💳 UPI, Cards, Net Banking • GST Invoice Available
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
