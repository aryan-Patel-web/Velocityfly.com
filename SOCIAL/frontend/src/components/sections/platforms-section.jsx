"use client"

import { useRef, useState } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Sphere, Ring, Float, MeshDistortMaterial, Trail } from "@react-three/drei"
import { Facebook, Instagram, MessageCircle, Youtube, Hash } from "lucide-react"
import * as THREE from "three"

function CentralSun() {
  const sunRef = useRef()
  const glowRef = useRef()
  const coronaRef = useRef()

  useFrame((state) => {
    if (sunRef.current) {
      sunRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
    if (glowRef.current) {
      glowRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.15)
    }
    if (coronaRef.current) {
      coronaRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 1.5) * 0.1)
    }
  })

  return (
    <group>
      <Sphere ref={sunRef} args={[1.5, 64, 64]}>
        <MeshDistortMaterial
          color="#8B5CF6"
          distort={0.3}
          speed={3}
          roughness={0.1}
          metalness={0.9}
          emissive="#8B5CF6"
          emissiveIntensity={0.8}
        />
      </Sphere>
      <Sphere ref={glowRef} args={[1.8, 32, 32]}>
        <meshBasicMaterial color="#8B5CF6" transparent opacity={0.3} />
      </Sphere>
      <Sphere ref={coronaRef} args={[2.2, 32, 32]}>
        <meshBasicMaterial color="#06B6D4" transparent opacity={0.1} />
      </Sphere>
    </group>
  )
}

function OrbitingPlanet({ radius, speed, color, size = 0.3, offset = 0, name }) {
  const planetRef = useRef()
  const trailRef = useRef()

  useFrame((state) => {
    const angle = state.clock.elapsedTime * speed + offset
    if (planetRef.current) {
      planetRef.current.position.x = Math.cos(angle) * radius
      planetRef.current.position.z = Math.sin(angle) * radius
      planetRef.current.position.y = Math.sin(angle * 2) * 0.5
    }
  })

  return (
    <group>
      <Ring args={[radius - 0.02, radius + 0.02, 64]} rotation={[Math.PI / 2, 0, 0]}>
        <meshBasicMaterial color={color} transparent opacity={0.2} side={THREE.DoubleSide} />
      </Ring>
      <Float speed={1} floatIntensity={0.3}>
        <Trail width={0.3} length={6} color={color} attenuation={(t) => t * t}>
          <Sphere ref={planetRef} args={[size, 32, 32]}>
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={0.8}
              roughness={0.2}
              metalness={0.8}
            />
          </Sphere>
        </Trail>
      </Float>
    </group>
  )
}

function Nebula() {
  const nebulaRef = useRef()
  const count = 300

  useFrame((state) => {
    if (nebulaRef.current) {
      nebulaRef.current.rotation.y = state.clock.elapsedTime * 0.02
    }
  })

  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)

  for (let i = 0; i < count; i++) {
    const radius = 8 + Math.random() * 5
    const theta = Math.random() * Math.PI * 2
    const phi = Math.random() * Math.PI
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = (Math.random() - 0.5) * 4
    positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta)

    const colorChoice = Math.random()
    if (colorChoice < 0.5) {
      colors[i * 3] = 0.545
      colors[i * 3 + 1] = 0.361
      colors[i * 3 + 2] = 0.965
    } else {
      colors[i * 3] = 0.024
      colors[i * 3 + 1] = 0.714
      colors[i * 3 + 2] = 0.831
    }
  }

  return (
    <points ref={nebulaRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={count} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.08} vertexColors transparent opacity={0.6} />
    </points>
  )
}

function SolarSystemScene() {
  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 0, 0]} intensity={3} color="#8B5CF6" distance={25} />
      <CentralSun />
      <OrbitingPlanet radius={3} speed={0.5} color="#3B82F6" size={0.4} offset={0} name="Facebook" />
      <OrbitingPlanet radius={4} speed={0.4} color="#EC4899" size={0.35} offset={Math.PI * 0.4} name="Instagram" />
      <OrbitingPlanet radius={5} speed={0.3} color="#22C55E" size={0.3} offset={Math.PI * 0.8} name="WhatsApp" />
      <OrbitingPlanet radius={6} speed={0.25} color="#EF4444" size={0.5} offset={Math.PI * 1.2} name="YouTube" />
      <OrbitingPlanet radius={7} speed={0.2} color="#F97316" size={0.35} offset={Math.PI * 1.6} name="Reddit" />
      <Nebula />
    </>
  )
}

function PlatformCard({ platform, isSelected, onClick }) {
  const { name, icon: Icon, color, description, features } = platform

  return (
    <button
      onClick={onClick}
      className={`w-full text-left glass rounded-2xl p-6 transition-all duration-500 ${
        isSelected ? "glow-box scale-105" : "hover:scale-102"
      } glow-border`}
      style={{
        borderColor: isSelected ? color : "rgba(139, 92, 246, 0.3)",
        boxShadow: isSelected ? `0 0 30px ${color}40, 0 0 60px ${color}20` : undefined,
      }}
    >
      <div className="flex items-center gap-4 mb-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: `${color}20` }}
        >
          <Icon className="w-6 h-6" style={{ color }} />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">{name}</h3>
          <p className="text-sm text-white/60">{description}</p>
        </div>
      </div>

      {isSelected && (
        <div className="space-y-2 mt-4 pt-4 border-t border-white/10 animate-fade-in">
          {features.map((feature, index) => (
            <div key={index} className="flex items-center gap-2 text-sm text-white/70">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
              {feature}
            </div>
          ))}
        </div>
      )}
    </button>
  )
}

export default function PlatformsSection() {
  const [selectedPlatform, setSelectedPlatform] = useState(3)

  const platforms = [
    {
      name: "Facebook",
      icon: Facebook,
      color: "#3B82F6",
      description: "Reach billions of users",
      features: ["Auto-post to pages & groups", "Story automation", "Ad campaign integration", "Audience insights"],
    },
    {
      name: "Instagram",
      icon: Instagram,
      color: "#EC4899",
      description: "Visual content automation",
      features: ["Feed & Reels posting", "Story scheduling", "Hashtag optimization", "Engagement analytics"],
    },
    {
      name: "WhatsApp",
      icon: MessageCircle,
      color: "#22C55E",
      description: "Business messaging at scale",
      features: ["Broadcast messages", "Auto-replies", "Customer segmentation", "Message templates"],
    },
    {
      name: "YouTube",
      icon: Youtube,
      color: "#EF4444",
      description: "Video content empire",
      features: ["Video scheduling", "Shorts automation", "AI Thumbnail generation", "SEO optimization"],
    },
    {
      name: "Reddit",
      icon: Hash,
      color: "#F97316",
      description: "Community engagement",
      features: ["Subreddit posting", "Comment automation", "Karma tracking", "Trend detection"],
    },
  ]

  return (
    <section id="platforms" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 5, 15], fov: 50 }}>
          <SolarSystemScene />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-transparent to-[#0a0a0f] z-10" />

      <div className="relative z-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6">
            SOLAR SYSTEM CONTROL
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">One Dashboard.</span>
            <br />
            <span className="gradient-text">Five Platforms.</span>
            <br />
            <span className="text-white">Infinite Growth.</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Manage all your social media from a single control center. Click any platform to explore automation
            features.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 items-center">
          <div className="space-y-4">
            {platforms.map((platform, index) => (
              <PlatformCard
                key={index}
                platform={platform}
                isSelected={selectedPlatform === index}
                onClick={() => setSelectedPlatform(index)}
              />
            ))}
          </div>

          <div className="relative aspect-square hidden lg:flex items-center justify-center">
            <div className="relative w-80 h-80">
              <div className="absolute inset-0 bg-gradient-to-br from-[#8b5cf6]/20 to-[#06b6d4]/20 rounded-full blur-3xl animate-pulse" />
              <div className="absolute inset-8 glass rounded-full flex items-center justify-center glow-box">
                <span className="text-4xl font-bold gradient-text">VP</span>
              </div>

              {platforms.map((platform, index) => {
                const angle = (index / platforms.length) * Math.PI * 2 - Math.PI / 2
                const radius = 150
                const x = Math.cos(angle) * radius
                const y = Math.sin(angle) * radius

                return (
                  <button
                    key={index}
                    onClick={() => setSelectedPlatform(index)}
                    className={`absolute w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-500 ${
                      selectedPlatform === index ? "scale-125" : "scale-100 hover:scale-110"
                    }`}
                    style={{
                      left: `calc(50% + ${x}px - 28px)`,
                      top: `calc(50% + ${y}px - 28px)`,
                      backgroundColor: `${platform.color}20`,
                      border: `2px solid ${selectedPlatform === index ? platform.color : "transparent"}`,
                      boxShadow: selectedPlatform === index ? `0 0 20px ${platform.color}60` : undefined,
                    }}
                  >
                    <platform.icon className="w-6 h-6" style={{ color: platform.color }} />
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
