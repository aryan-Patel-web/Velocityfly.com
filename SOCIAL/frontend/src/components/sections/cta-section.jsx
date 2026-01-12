"use client"

import { useRef, useState, useEffect } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Torus, Sphere, Float, MeshDistortMaterial } from "@react-three/drei"
import { Button } from "@/components/ui/button"
import { ArrowRight, Shield, FileCheck, Award, CreditCard, Headphones, Clock, Gift } from "lucide-react"

function PortalRing() {
  const ringRef = useRef()
  const innerRingRef = useRef()
  const outerRingRef = useRef()

  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.x = state.clock.elapsedTime * 0.3
      ringRef.current.rotation.y = state.clock.elapsedTime * 0.2
    }
    if (innerRingRef.current) {
      innerRingRef.current.rotation.x = -state.clock.elapsedTime * 0.4
      innerRingRef.current.rotation.z = state.clock.elapsedTime * 0.2
    }
    if (outerRingRef.current) {
      outerRingRef.current.rotation.y = state.clock.elapsedTime * 0.15
    }
  })

  return (
    <group>
      <Torus ref={outerRingRef} args={[4, 0.08, 16, 100]}>
        <meshStandardMaterial
          color="#3B82F6"
          emissive="#3B82F6"
          emissiveIntensity={0.3}
          metalness={0.8}
          roughness={0.2}
        />
      </Torus>
      <Torus ref={ringRef} args={[3, 0.12, 16, 100]}>
        <meshStandardMaterial
          color="#8B5CF6"
          emissive="#8B5CF6"
          emissiveIntensity={0.6}
          metalness={0.8}
          roughness={0.2}
        />
      </Torus>
      <Torus ref={innerRingRef} args={[2.2, 0.1, 16, 100]}>
        <meshStandardMaterial
          color="#06B6D4"
          emissive="#06B6D4"
          emissiveIntensity={0.6}
          metalness={0.8}
          roughness={0.2}
        />
      </Torus>
    </group>
  )
}

function EnergyVortex() {
  const particlesRef = useRef()
  const count = 800

  useFrame((state) => {
    if (particlesRef.current) {
      const pos = particlesRef.current.geometry.attributes.position.array
      for (let i = 0; i < count; i++) {
        const angle = (i / count) * Math.PI * 2 + state.clock.elapsedTime * 2
        const radius = 0.5 + (i / count) * 3
        const spiralOffset = (i / count) * Math.PI * 6 + state.clock.elapsedTime * 3
        pos[i * 3] = Math.cos(angle + spiralOffset) * radius
        pos[i * 3 + 1] = Math.sin(angle + spiralOffset) * radius
        pos[i * 3 + 2] = Math.sin(spiralOffset * 0.3) * 1
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  const positions = new Float32Array(count * 3)

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.04} color="#C084FC" transparent opacity={0.7} />
    </points>
  )
}

function CenterOrb() {
  const orbRef = useRef()
  const glowRef = useRef()

  useFrame((state) => {
    if (orbRef.current) {
      orbRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.15)
    }
    if (glowRef.current) {
      glowRef.current.scale.setScalar(1.5 + Math.sin(state.clock.elapsedTime * 1.5) * 0.2)
    }
  })

  return (
    <group>
      <Float speed={2} floatIntensity={0.5}>
        <Sphere ref={orbRef} args={[1.2, 64, 64]}>
          <MeshDistortMaterial
            color="#8B5CF6"
            distort={0.5}
            speed={4}
            roughness={0.1}
            metalness={0.9}
            emissive="#8B5CF6"
            emissiveIntensity={0.6}
          />
        </Sphere>
      </Float>
      <Sphere ref={glowRef} args={[1.8, 32, 32]}>
        <meshBasicMaterial color="#8B5CF6" transparent opacity={0.15} />
      </Sphere>
    </group>
  )
}

function PortalScene() {
  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 0, 5]} intensity={2.5} color="#8B5CF6" />
      <pointLight position={[0, 0, -5]} intensity={1.5} color="#06B6D4" />
      <pointLight position={[5, 5, 0]} intensity={0.8} color="#A855F7" />
      <PortalRing />
      <EnergyVortex />
      <CenterOrb />
    </>
  )
}

function CountdownTimer() {
  const [time, setTime] = useState({ hours: 23, minutes: 45, seconds: 12 })

  useEffect(() => {
    const interval = setInterval(() => {
      setTime((prev) => {
        let { hours, minutes, seconds } = prev
        seconds--
        if (seconds < 0) {
          seconds = 59
          minutes--
        }
        if (minutes < 0) {
          minutes = 59
          hours--
        }
        if (hours < 0) {
          hours = 23
          minutes = 59
          seconds = 59
        }
        return { hours, minutes, seconds }
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2 text-2xl font-mono">
      <span className="bg-[#1a1625] px-3 py-2 rounded-lg text-white">{String(time.hours).padStart(2, "0")}</span>
      <span className="text-[#8b5cf6]">:</span>
      <span className="bg-[#1a1625] px-3 py-2 rounded-lg text-white">{String(time.minutes).padStart(2, "0")}</span>
      <span className="text-[#8b5cf6]">:</span>
      <span className="bg-[#1a1625] px-3 py-2 rounded-lg text-white">{String(time.seconds).padStart(2, "0")}</span>
    </div>
  )
}

export default function CTASection() {
  const trustBadges = [
    { icon: Shield, label: "256-bit SSL" },
    { icon: FileCheck, label: "GDPR Compliant" },
    { icon: Award, label: "30-Day Guarantee" },
    { icon: CreditCard, label: "UPI & Cards" },
    { icon: Headphones, label: "24/7 Support" },
    { icon: Clock, label: "99.9% Uptime" },
  ]

  return (
    <section id="cta" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
          <PortalScene />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/50 via-transparent to-[#0a0a0f] z-10" />

      <div className="relative z-20 max-w-4xl mx-auto px-6 text-center">
        <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6 animate-pulse-glow">
          PORTAL GATEWAY
        </span>

        <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
          <span className="text-white">Ready to</span>
          <br />
          <span className="gradient-text glow-text">Dominate Social Media?</span>
        </h2>

        <p className="text-lg text-white/60 max-w-2xl mx-auto mb-8">
          Join 50,000+ Indian creators already winning with AI automation. Start your free trial today.
        </p>

        <Button
          size="lg"
          className="bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] hover:opacity-90 text-white px-12 py-8 text-xl font-bold glow-box group relative overflow-hidden mb-8"
        >
          <span className="relative z-10 flex items-center gap-3">
            Start Free Trial
            <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
          </span>
        </Button>

        <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-white/50 mb-12">
          <span className="flex items-center gap-1">
            <span className="text-[#06b6d4]">✓</span> No credit card required
          </span>
          <span className="flex items-center gap-1">
            <span className="text-[#06b6d4]">✓</span> 14-day free trial
          </span>
          <span className="flex items-center gap-1">
            <span className="text-[#06b6d4]">✓</span> Cancel anytime
          </span>
          <span className="flex items-center gap-1">
            <span className="text-[#06b6d4]">✓</span> Setup in 3 minutes
          </span>
        </div>

        <div className="glass rounded-2xl p-6 mb-12 glow-border">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Gift className="w-5 h-5 text-[#06b6d4]" />
            <span className="text-white font-semibold">Special Launch Offer (Limited Time)</span>
          </div>
          <ul className="text-sm text-white/70 space-y-2 mb-4">
            <li>• First 1,000 users get PRO plan at BASIC price</li>
            <li>• Lifetime 30% discount for early adopters</li>
            <li>• Free 1-on-1 onboarding call (worth ₹5,000)</li>
            <li>• Bonus: 100 AI credits for thumbnail generation</li>
          </ul>
          <div className="flex items-center justify-center gap-2 text-white/50 text-sm">
            <Clock className="w-4 h-4" />
            Offer expires in:
          </div>
          <div className="flex justify-center mt-2">
            <CountdownTimer />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          {trustBadges.map((badge, index) => (
            <div
              key={index}
              className="glass rounded-xl px-4 py-3 flex items-center gap-2 glow-border hover:glow-box transition-all duration-300"
            >
              <badge.icon className="w-4 h-4 text-[#06b6d4]" />
              <span className="text-white text-sm font-medium">{badge.label}</span>
            </div>
          ))}
        </div>

        <div className="mt-12 glass rounded-2xl p-6">
          <p className="text-white/60 text-sm mb-4">Still have questions?</p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-white/70">
            <span>📧 support@velocitypost.ai</span>
            <span>💬 WhatsApp: +91-98765-43210</span>
            <span>🕒 Live Chat: 24/7</span>
          </div>
        </div>
      </div>
    </section>
  )
}
