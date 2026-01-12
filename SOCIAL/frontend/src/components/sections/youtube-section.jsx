"use client"

import { useRef, useState, useMemo } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Float, RoundedBox, Sphere, Ring } from "@react-three/drei"
import * as THREE from "three"
import {
  Youtube,
  Video,
  ImageIcon,
  Calendar,
  MessageSquare,
  BarChart2,
  Sparkles,
  Clock,
  TrendingUp,
  Play,
} from "lucide-react"

function YouTubePlayButton() {
  const groupRef = useRef()
  const ringsRef = useRef([])

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.2
    }
    ringsRef.current.forEach((ring, i) => {
      if (ring) {
        ring.rotation.z = state.clock.elapsedTime * (0.5 + i * 0.2)
        const scale = 1 + Math.sin(state.clock.elapsedTime * 2 + i) * 0.1
        ring.scale.set(scale, scale, 1)
      }
    })
  })

  return (
    <group ref={groupRef}>
      <Float speed={2} floatIntensity={0.3}>
        {/* Main YouTube box */}
        <RoundedBox args={[3, 2.1, 0.4]} radius={0.2} smoothness={4}>
          <meshStandardMaterial
            color="#EF4444"
            emissive="#EF4444"
            emissiveIntensity={0.6}
            metalness={0.4}
            roughness={0.3}
          />
        </RoundedBox>
        {/* Play triangle */}
        <mesh position={[0.15, 0, 0.25]} rotation={[0, 0, -Math.PI / 2]}>
          <coneGeometry args={[0.5, 0.8, 3]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.3} />
        </mesh>
      </Float>

      {/* Energy rings */}
      {[0, 1, 2].map((i) => (
        <Ring
          key={i}
          ref={(el) => (ringsRef.current[i] = el)}
          args={[1.8 + i * 0.5, 1.9 + i * 0.5, 64]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <meshBasicMaterial color="#EF4444" transparent opacity={0.2 - i * 0.05} side={THREE.DoubleSide} />
        </Ring>
      ))}

      {/* Glow sphere */}
      <Sphere args={[2.5, 32, 32]}>
        <meshBasicMaterial color="#EF4444" transparent opacity={0.08} />
      </Sphere>
    </group>
  )
}

function FloatingVideoScreens() {
  const screensRef = useRef([])

  const screens = useMemo(
    () => [
      { position: [-4, 2, -2], rotation: [0, 0.3, 0], scale: 1 },
      { position: [4, 1, -3], rotation: [0, -0.3, 0], scale: 0.9 },
      { position: [-3, -1.5, -2], rotation: [0, 0.2, 0], scale: 0.8 },
      { position: [3, -2, -3], rotation: [0, -0.2, 0], scale: 0.85 },
      { position: [0, 3, -4], rotation: [0, 0, 0], scale: 0.7 },
    ],
    [],
  )

  useFrame((state) => {
    screensRef.current.forEach((screen, i) => {
      if (screen) {
        screen.position.y = screens[i].position[1] + Math.sin(state.clock.elapsedTime + i * 2) * 0.3
        screen.rotation.y = screens[i].rotation[1] + Math.sin(state.clock.elapsedTime * 0.5 + i) * 0.1
      }
    })
  })

  return (
    <>
      {screens.map((screen, i) => (
        <group key={i} ref={(el) => (screensRef.current[i] = el)} position={screen.position} scale={screen.scale}>
          <RoundedBox args={[2, 1.2, 0.08]} radius={0.05} smoothness={4}>
            <meshStandardMaterial color="#1a1625" emissive="#EF4444" emissiveIntensity={0.05} />
          </RoundedBox>
          {/* Screen glow */}
          <RoundedBox args={[1.8, 1, 0.01]} radius={0.02} position={[0, 0, 0.05]}>
            <meshBasicMaterial color="#EF4444" transparent opacity={0.1} />
          </RoundedBox>
          {/* Play icon on screen */}
          <mesh position={[0, 0, 0.06]}>
            <circleGeometry args={[0.15, 32]} />
            <meshBasicMaterial color="#EF4444" transparent opacity={0.5} />
          </mesh>
        </group>
      ))}
    </>
  )
}

function StreamingData() {
  const particlesRef = useRef()
  const count = 200

  const { positions, velocities } = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const vel = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 12
      pos[i * 3 + 1] = Math.random() * 10 - 5
      pos[i * 3 + 2] = (Math.random() - 0.5) * 8
      vel[i * 3 + 1] = -0.02 - Math.random() * 0.03
    }
    return { positions: pos, velocities: vel }
  }, [])

  useFrame(() => {
    if (particlesRef.current) {
      const pos = particlesRef.current.geometry.attributes.position.array
      for (let i = 0; i < count; i++) {
        pos[i * 3 + 1] += velocities[i * 3 + 1]
        if (pos[i * 3 + 1] < -5) {
          pos[i * 3 + 1] = 5
        }
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.06} color="#EF4444" transparent opacity={0.6} />
    </points>
  )
}

function OrbitingElements() {
  const groupRef = useRef()

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.2
    }
  })

  return (
    <group ref={groupRef}>
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const angle = (i / 6) * Math.PI * 2
        const radius = 5
        return (
          <Float key={i} speed={2} floatIntensity={0.5}>
            <Sphere
              args={[0.15, 16, 16]}
              position={[Math.cos(angle) * radius, Math.sin(angle * 2) * 0.5, Math.sin(angle) * radius]}
            >
              <meshStandardMaterial
                color={i % 2 === 0 ? "#EF4444" : "#8B5CF6"}
                emissive={i % 2 === 0 ? "#EF4444" : "#8B5CF6"}
                emissiveIntensity={0.5}
              />
            </Sphere>
          </Float>
        )
      })}
    </group>
  )
}

function YouTubeScene() {
  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 5, 5]} intensity={2} color="#EF4444" />
      <pointLight position={[-5, -5, 5]} intensity={0.8} color="#8B5CF6" />
      <pointLight position={[5, 0, 3]} intensity={0.5} color="#06B6D4" />

      <YouTubePlayButton />
      <FloatingVideoScreens />
      <StreamingData />
      <OrbitingElements />
    </>
  )
}

function FeatureCard({ icon: Icon, title, features, isHovered, onHover }) {
  return (
    <div
      className={`glass rounded-2xl p-6 transition-all duration-300 cursor-pointer ${
        isHovered ? "glow-red scale-105 border-red-500/50" : "glow-border hover:border-red-500/30"
      }`}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
    >
      <div className="flex items-center gap-3 mb-4">
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all ${
            isHovered ? "bg-red-500 text-white" : "bg-red-500/20 text-red-500"
          }`}
        >
          <Icon className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-white">{title}</h3>
      </div>
      <ul className="space-y-2">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center gap-2 text-sm text-white/70">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
            {feature}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function YouTubeSection() {
  const [hoveredCard, setHoveredCard] = useState(null)

  const youtubeFeatures = [
    {
      icon: Video,
      title: "AI Content Generation",
      features: ["Shorts & Long-form videos", "Hindi + English + 10 more", "Viral topic suggestions", "SEO optimized"],
    },
    {
      icon: ImageIcon,
      title: "Thumbnail Creator",
      features: ["3 AI-generated designs", "Frame extraction", "Custom upload support", "Text overlays"],
    },
    {
      icon: Calendar,
      title: "Smart Scheduler",
      features: ["Best time predictions", "Auto-upload queue", "Multi-video batch", "Peak hour posting"],
    },
    {
      icon: Sparkles,
      title: "Image Slideshow",
      features: ["2-6 images to video", "Product videos", "Auto-add music", "Shorts optimized"],
    },
    {
      icon: MessageSquare,
      title: "Comment Auto-Reply",
      features: ["24/7 AI replies", "Friendly tone", "Engagement boost", "Custom style"],
    },
    {
      icon: BarChart2,
      title: "YouTube Analytics",
      features: ["View tracking", "Engagement stats", "Growth insights", "Subscriber trends"],
    },
  ]

  return (
    <section id="youtube" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
          <YouTubeScene />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/60 via-[#0a0a0f]/40 to-[#0a0a0f]/60 z-10" />

      <div className="relative z-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-2 rounded-full bg-red-500/20 text-sm text-red-400 mb-6 border border-red-500/30 animate-pulse">
            VIDEO COMMAND CENTER
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
            <span className="gradient-text-youtube">YouTube Automation Studio</span>
          </h2>
          <p className="text-xl text-white/60 mb-2">India's #1 Choice for YouTube Growth</p>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            Automate your entire YouTube workflow with AI magic. From content creation to comment replies.
          </p>
        </div>

        <div className="flex justify-center mb-12">
          <div className="glass rounded-2xl p-8 glow-red max-w-md text-center relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-r from-red-500/0 via-red-500/10 to-red-500/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4 relative">
                <Youtube className="w-10 h-10 text-red-500" />
                <div className="absolute inset-0 rounded-full border-2 border-red-500/30 animate-ping" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Complete YouTube Automation</h3>
              <p className="text-white/60 mb-4">Everything you need to dominate YouTube on autopilot</p>
              <div className="flex items-center justify-center gap-6 text-sm">
                <div className="flex items-center gap-2 text-red-400">
                  <TrendingUp className="w-4 h-4" />
                  <span>15K+ Indian YouTubers</span>
                </div>
                <div className="flex items-center gap-2 text-red-400">
                  <Clock className="w-4 h-4" />
                  <span>20+ Hours Saved/Week</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {youtubeFeatures.map((feature, index) => (
            <FeatureCard
              key={index}
              {...feature}
              isHovered={hoveredCard === index}
              onHover={(isHovered) => setHoveredCard(isHovered ? index : null)}
            />
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-white/50 mb-4">Join 15,000+ Indian YouTubers Already Growing</p>
          <button className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white rounded-xl font-semibold transition-all glow-red inline-flex items-center gap-2 group">
            <Play className="w-5 h-5 group-hover:scale-110 transition-transform" />
            Explore YouTube Features
          </button>
        </div>
      </div>
    </section>
  )
}
