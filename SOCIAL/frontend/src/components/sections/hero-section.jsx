"use client"

import { useEffect, useRef, useState } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Stars, Float, Sphere, MeshDistortMaterial, Trail } from "@react-three/drei"
import { Button } from "@/components/ui/button"
import { ArrowRight, Play, Sparkles, Users, Clock, TrendingUp, Zap } from "lucide-react"

function AnimatedSphere({ position, color, speed = 1, distort = 0.3, scale = 1 }) {
  const meshRef = useRef()

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2 * speed
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3 * speed
    }
  })

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere ref={meshRef} args={[scale, 64, 64]} position={position}>
        <MeshDistortMaterial
          color={color}
          attach="material"
          distort={distort}
          speed={2}
          roughness={0.2}
          metalness={0.8}
        />
      </Sphere>
    </Float>
  )
}

function FloatingParticles({ count = 500 }) {
  const points = useRef()
  const particlesPosition = useRef(new Float32Array(count * 3))
  const particlesVelocity = useRef(new Float32Array(count * 3))

  useEffect(() => {
    for (let i = 0; i < count; i++) {
      particlesPosition.current[i * 3] = (Math.random() - 0.5) * 30
      particlesPosition.current[i * 3 + 1] = (Math.random() - 0.5) * 30
      particlesPosition.current[i * 3 + 2] = (Math.random() - 0.5) * 30
      particlesVelocity.current[i * 3] = (Math.random() - 0.5) * 0.02
      particlesVelocity.current[i * 3 + 1] = (Math.random() - 0.5) * 0.02
      particlesVelocity.current[i * 3 + 2] = (Math.random() - 0.5) * 0.02
    }
  }, [count])

  useFrame(() => {
    if (points.current) {
      const positions = points.current.geometry.attributes.position.array
      for (let i = 0; i < count; i++) {
        positions[i * 3] += particlesVelocity.current[i * 3]
        positions[i * 3 + 1] += particlesVelocity.current[i * 3 + 1]
        positions[i * 3 + 2] += particlesVelocity.current[i * 3 + 2]

        if (Math.abs(positions[i * 3]) > 15) particlesVelocity.current[i * 3] *= -1
        if (Math.abs(positions[i * 3 + 1]) > 15) particlesVelocity.current[i * 3 + 1] *= -1
        if (Math.abs(positions[i * 3 + 2]) > 15) particlesVelocity.current[i * 3 + 2] *= -1
      }
      points.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={particlesPosition.current} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#8B5CF6" transparent opacity={0.6} sizeAttenuation />
    </points>
  )
}

function GlobeWithOrbitingIcons() {
  const globeRef = useRef()
  const orbitRef = useRef()
  const innerOrbitRef = useRef()

  useFrame((state) => {
    if (globeRef.current) {
      globeRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
    if (orbitRef.current) {
      orbitRef.current.rotation.y = state.clock.elapsedTime * 0.25
      orbitRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.15) * 0.1
    }
    if (innerOrbitRef.current) {
      innerOrbitRef.current.rotation.y = -state.clock.elapsedTime * 0.35
    }
  })

  const platformColors = ["#3B82F6", "#EC4899", "#22C55E", "#EF4444", "#F97316"]
  const platformNames = ["Facebook", "Instagram", "WhatsApp", "YouTube", "Reddit"]

  return (
    <group>
      <Sphere ref={globeRef} args={[2, 64, 64]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#1a1625" wireframe transparent opacity={0.4} />
      </Sphere>
      <Sphere args={[2.1, 64, 64]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#8B5CF6" transparent opacity={0.1} emissive="#8B5CF6" emissiveIntensity={0.3} />
      </Sphere>
      <Sphere args={[2.2, 32, 32]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#06B6D4" transparent opacity={0.05} emissive="#06B6D4" emissiveIntensity={0.1} />
      </Sphere>

      <group ref={orbitRef}>
        {platformColors.map((color, i) => {
          const angle = (i / 5) * Math.PI * 2
          const radius = 3.8
          return (
            <Float key={i} speed={1.5} floatIntensity={0.5}>
              <Trail width={0.5} length={8} color={color} attenuation={(t) => t * t}>
                <Sphere
                  args={[0.25, 16, 16]}
                  position={[Math.cos(angle) * radius, Math.sin(angle * 2) * 0.5, Math.sin(angle) * radius]}
                >
                  <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} />
                </Sphere>
              </Trail>
            </Float>
          )
        })}
      </group>

      <group ref={innerOrbitRef}>
        {[0, 1, 2].map((i) => {
          const angle = (i / 3) * Math.PI * 2
          const radius = 2.8
          return (
            <Sphere
              key={`inner-${i}`}
              args={[0.1, 8, 8]}
              position={[Math.cos(angle) * radius, 0, Math.sin(angle) * radius]}
            >
              <meshStandardMaterial
                color="#06B6D4"
                emissive="#06B6D4"
                emissiveIntensity={1}
                transparent
                opacity={0.8}
              />
            </Sphere>
          )
        })}
      </group>
    </group>
  )
}

function GridFloor() {
  return (
    <group position={[0, -5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <gridHelper args={[50, 50, "#8B5CF6", "#1a1625"]} rotation={[Math.PI / 2, 0, 0]} />
    </group>
  )
}

function Scene() {
  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[10, 10, 10]} intensity={1.5} color="#8B5CF6" />
      <pointLight position={[-10, -10, -10]} intensity={0.8} color="#06B6D4" />
      <pointLight position={[0, 5, 0]} intensity={0.5} color="#ffffff" />
      <Stars radius={100} depth={50} count={8000} factor={4} saturation={0} fade speed={0.5} />
      <FloatingParticles count={500} />
      <GlobeWithOrbitingIcons />
      <AnimatedSphere position={[-7, 3, -8]} color="#8B5CF6" speed={0.5} distort={0.5} scale={1.2} />
      <AnimatedSphere position={[7, -2, -10]} color="#06B6D4" speed={0.7} distort={0.4} scale={0.8} />
      <AnimatedSphere position={[-5, -3, -6]} color="#6D28D9" speed={0.6} distort={0.3} scale={0.6} />
      <GridFloor />
    </>
  )
}

function CountUpAnimation({ end, duration = 2000, suffix = "" }) {
  const [count, setCount] = useState(0)
  const [hasStarted, setHasStarted] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasStarted) {
          setHasStarted(true)
        }
      },
      { threshold: 0.5 },
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [hasStarted])

  useEffect(() => {
    if (!hasStarted) return
    let startTime
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      const easeOut = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(easeOut * end))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [hasStarted, end, duration])

  return (
    <span ref={ref}>
      {count.toLocaleString()}
      {suffix}
    </span>
  )
}

export default function HeroSection() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      })
    }
    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  const stats = [
    { icon: Users, value: 50, suffix: "K+", label: "Active Users" },
    { icon: Sparkles, value: 10, suffix: "M+", label: "Posts Automated" },
    { icon: TrendingUp, value: 300, suffix: "%", label: "More Engagement" },
    { icon: Clock, value: 20, suffix: "+", label: "Hours Saved/Week" },
  ]

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20 snap-section"
    >
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 12], fov: 60 }}>
          <Scene />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0a0a0f]/30 to-[#0a0a0f] z-10 pointer-events-none" />

      <div className="relative z-20 max-w-6xl mx-auto px-6 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass glow-border mb-8 animate-pulse-glow">
          <Zap className="w-4 h-4 text-[#06b6d4]" />
          <span className="text-sm text-[#06b6d4] font-medium">NEW: AI-POWERED SOCIAL MEDIA AUTOMATION</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
          <span className="text-white">Automate Your</span>
          <br />
          <span className="gradient-text glow-text">Social Media Empire</span>
          <br />
          <span className="text-white">With VelocityPost</span>
        </h1>

        <p className="text-base sm:text-lg md:text-xl text-white/60 max-w-2xl mx-auto mb-10 leading-relaxed">
          Stop posting manually. Let AI create viral content, schedule posts, and grow your audience across all
          platforms—while you sleep.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
          <Button
            size="lg"
            className="bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] hover:opacity-90 text-white px-8 py-6 text-lg glow-box group relative overflow-hidden"
          >
            <span className="relative z-10 flex items-center gap-2">
              Start Free Trial
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </span>
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-[#8b5cf6]/50 text-white hover:bg-[#8b5cf6]/10 px-8 py-6 text-lg group bg-transparent"
          >
            <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
            Watch Demo
          </Button>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-white/50 mb-16">
          <span className="flex items-center gap-1">
            <Sparkles className="w-4 h-4 text-[#06b6d4]" /> 14-Day Free Trial
          </span>
          <span className="hidden sm:inline text-white/30">•</span>
          <span>No Credit Card Required</span>
          <span className="hidden sm:inline text-white/30">•</span>
          <span>Cancel Anytime</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="glass rounded-2xl p-4 md:p-6 glow-border hover:scale-105 transition-all duration-300 cursor-default"
              style={{
                transform: `translate(${mousePosition.x * (index % 2 === 0 ? -3 : 3)}px, ${mousePosition.y * (index < 2 ? -3 : 3)}px)`,
              }}
            >
              <stat.icon className="w-5 h-5 md:w-6 md:h-6 text-[#8b5cf6] mb-2 md:mb-3 mx-auto" />
              <div className="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-1">
                <CountUpAnimation end={stat.value} suffix={stat.suffix} />
              </div>
              <div className="text-xs md:text-sm text-white/50">{stat.label}</div>
            </div>
          ))}
        </div>

        <p className="mt-8 text-white/40 text-sm">#1 Choice of Indian Content Creators & Businesses</p>
      </div>

      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 animate-bounce">
        <div className="w-6 h-10 rounded-full border-2 border-[#8b5cf6]/50 flex justify-center pt-2">
          <div className="w-1 h-3 bg-[#8b5cf6] rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  )
}
