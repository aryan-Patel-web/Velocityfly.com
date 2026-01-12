"use client"

import { useRef, useEffect, useState } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Box } from "@react-three/drei"
import * as THREE from "three"

function MatrixRain({ count = 200 }) {
  const points = useRef()
  const positions = useRef(new Float32Array(count * 3))
  const velocities = useRef(new Float32Array(count))

  useEffect(() => {
    for (let i = 0; i < count; i++) {
      positions.current[i * 3] = (Math.random() - 0.5) * 25
      positions.current[i * 3 + 1] = Math.random() * 25
      positions.current[i * 3 + 2] = (Math.random() - 0.5) * 15
      velocities.current[i] = Math.random() * 0.15 + 0.05
    }
  }, [count])

  useFrame(() => {
    if (points.current) {
      const pos = points.current.geometry.attributes.position.array
      for (let i = 0; i < count; i++) {
        pos[i * 3 + 1] -= velocities.current[i]
        if (pos[i * 3 + 1] < -12) {
          pos[i * 3 + 1] = 12
        }
      }
      points.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions.current} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.08} color="#8B5CF6" transparent opacity={0.7} />
    </points>
  )
}

function FloatingBar({ position, height, color, delay = 0 }) {
  const barRef = useRef()
  const [currentHeight, setCurrentHeight] = useState(0.1)

  useFrame((state) => {
    if (barRef.current) {
      const targetHeight = height * (0.8 + Math.sin(state.clock.elapsedTime * 2 + delay) * 0.2)
      setCurrentHeight(THREE.MathUtils.lerp(currentHeight, targetHeight, 0.05))
      barRef.current.scale.y = currentHeight
      barRef.current.position.y = currentHeight / 2
    }
  })

  return (
    <group position={position}>
      <Box ref={barRef} args={[0.5, 1, 0.5]}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} metalness={0.8} roughness={0.2} />
      </Box>
      <Box args={[0.6, 0.05, 0.6]} position={[0, 0, 0]}>
        <meshStandardMaterial color={color} transparent opacity={0.3} />
      </Box>
    </group>
  )
}

function StatsScene() {
  const bars = [
    { position: [-4, 0, 0], height: 3, color: "#8B5CF6" },
    { position: [-2, 0, 0], height: 5, color: "#06B6D4" },
    { position: [0, 0, 0], height: 6, color: "#A855F7" },
    { position: [2, 0, 0], height: 4, color: "#3B82F6" },
    { position: [4, 0, 0], height: 3.5, color: "#22D3EE" },
  ]

  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[0, 10, 5]} intensity={1.5} color="#8B5CF6" />
      <pointLight position={[-5, 5, 5]} intensity={0.8} color="#06B6D4" />
      <MatrixRain count={300} />
      {bars.map((bar, index) => (
        <FloatingBar key={index} {...bar} delay={index * 0.5} />
      ))}
    </>
  )
}

function AnimatedCounter({ end, suffix = "", prefix = "", duration = 2500 }) {
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
      { threshold: 0.3 },
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
      const easeOutQuart = 1 - Math.pow(1 - progress, 4)
      setCount(Math.floor(easeOutQuart * end))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [hasStarted, end, duration])

  return (
    <span ref={ref}>
      {prefix}
      {count.toLocaleString()}
      {suffix}
    </span>
  )
}

function ActivityFeed() {
  const activities = [
    { name: "Rajesh K.", action: "automated 50 posts across 3 platforms", location: "Mumbai", avatar: "👨‍💼" },
    { name: "Priya S.", action: "scheduled 100 YouTube Shorts", location: "Bangalore", avatar: "👩‍💻" },
    { name: "Aryan P.", action: "boosted engagement by 150%", location: "Delhi", avatar: "👨‍🎨" },
    { name: "Sneha M.", action: "uploaded 25 Instagram Reels", location: "Pune", avatar: "👩‍🔬" },
    { name: "Vikram T.", action: "generated ₹45,000 in affiliate revenue", location: "Hyderabad", avatar: "👨‍🚀" },
  ]

  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % activities.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [activities.length])

  return (
    <div className="glass rounded-2xl p-6 glow-border overflow-hidden">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-sm text-white/60">Live Activity Feed</span>
      </div>
      <div className="relative h-28 overflow-hidden">
        {activities.map((activity, index) => (
          <div
            key={index}
            className={`absolute inset-x-0 transition-all duration-500 ${
              index === currentIndex
                ? "opacity-100 translate-y-0"
                : index === (currentIndex - 1 + activities.length) % activities.length
                  ? "opacity-0 -translate-y-full"
                  : "opacity-0 translate-y-full"
            }`}
          >
            <div className="flex items-center gap-4 p-4 bg-[#1a1625]/50 rounded-xl">
              <div className="text-3xl">{activity.avatar}</div>
              <div>
                <p className="text-white font-medium">
                  {activity.name} <span className="text-white/60 font-normal">{activity.action}</span>
                </p>
                <p className="text-sm text-[#06b6d4]">📍 {activity.location} • just now</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function StatsSection() {
  const stats = [
    { value: 10, suffix: "M+", label: "Posts Automated", subtext: "+287% YoY" },
    { value: 50, suffix: "K+", label: "Active Users", subtext: "+150% YoY" },
    { value: 20, suffix: "+", label: "Hours Saved Weekly", subtext: "Per User" },
    { value: 300, suffix: "%", label: "Engagement Increase", subtext: "Average" },
    { value: 98.5, suffix: "%", label: "Uptime Guarantee", subtext: "24/7 Active" },
    { value: 50, prefix: "₹", suffix: "Cr+", label: "Revenue Generated", subtext: "For Users (2024)" },
  ]

  return (
    <section id="stats" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0 opacity-60">
        <Canvas camera={{ position: [0, 3, 12], fov: 50 }}>
          <StatsScene />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-transparent to-[#0a0a0f] z-10" />

      <div className="relative z-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6">
            DATA MATRIX REALM
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">The Numbers</span>
            <br />
            <span className="gradient-text">Speak For Themselves</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Real results from real Indian businesses using VelocityPost
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="glass rounded-2xl p-6 md:p-8 text-center glow-border hover:glow-box transition-all duration-300 group"
            >
              <div className="text-3xl md:text-5xl lg:text-6xl font-bold gradient-text mb-2 group-hover:scale-110 transition-transform">
                <AnimatedCounter end={stat.value} prefix={stat.prefix} suffix={stat.suffix} />
              </div>
              <div className="text-base md:text-lg text-white font-medium mb-1">{stat.label}</div>
              <div className="text-sm text-[#06b6d4]">{stat.subtext}</div>
            </div>
          ))}
        </div>

        <div className="max-w-lg mx-auto">
          <ActivityFeed />
        </div>

        <p className="text-center text-white/40 mt-8">🇮🇳 Trusted by India's Top Content Creators</p>
      </div>
    </section>
  )
}
