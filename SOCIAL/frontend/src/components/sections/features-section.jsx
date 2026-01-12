"use client"

import { useRef, useState, useMemo } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Float, MeshDistortMaterial, Ring } from "@react-three/drei"
import * as THREE from "three"
import { Brain, Zap, BarChart3, Target, Link2, TrendingUp } from "lucide-react"

function DNAHelix() {
  const groupRef = useRef()
  const count = 30

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })

  const spheres = useMemo(() => {
    const items = []
    for (let i = 0; i < count; i++) {
      const t = (i / count) * Math.PI * 4
      const radius = 2
      items.push(
        { position: [Math.cos(t) * radius, (i - count / 2) * 0.3, Math.sin(t) * radius], color: "#8B5CF6" },
        {
          position: [Math.cos(t + Math.PI) * radius, (i - count / 2) * 0.3, Math.sin(t + Math.PI) * radius],
          color: "#06B6D4",
        },
      )
    }
    return items
  }, [])

  return (
    <group ref={groupRef} position={[0, 0, -5]}>
      {spheres.map((sphere, i) => (
        <mesh key={i} position={sphere.position}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color={sphere.color} emissive={sphere.color} emissiveIntensity={0.5} />
        </mesh>
      ))}
    </group>
  )
}

function HolographicCubes() {
  const cubesRef = useRef([])

  useFrame((state) => {
    cubesRef.current.forEach((cube, i) => {
      if (cube) {
        cube.rotation.x = state.clock.elapsedTime * 0.3 + i
        cube.rotation.y = state.clock.elapsedTime * 0.2 + i
        cube.position.y = Math.sin(state.clock.elapsedTime + i * 2) * 0.5 + (i - 2) * 2
      }
    })
  })

  const positions = [
    [-5, 3, -3],
    [5, -2, -4],
    [-4, -3, -2],
    [4, 2, -5],
    [0, 4, -6],
  ]

  return (
    <>
      {positions.map((pos, i) => (
        <Float key={i} speed={1.5} floatIntensity={0.5}>
          <mesh ref={(el) => (cubesRef.current[i] = el)} position={pos}>
            <boxGeometry args={[0.5, 0.5, 0.5]} />
            <meshStandardMaterial color={i % 2 === 0 ? "#8B5CF6" : "#06B6D4"} transparent opacity={0.3} wireframe />
          </mesh>
          <Ring args={[0.4, 0.5, 32]} position={pos} rotation={[Math.PI / 2, 0, 0]}>
            <meshBasicMaterial color={i % 2 === 0 ? "#8B5CF6" : "#06B6D4"} transparent opacity={0.2} />
          </Ring>
        </Float>
      ))}
    </>
  )
}

function EnergyWaves() {
  const waveRefs = useRef([])

  useFrame((state) => {
    waveRefs.current.forEach((wave, i) => {
      if (wave) {
        const scale = 1 + Math.sin(state.clock.elapsedTime * 2 + i * 0.5) * 0.3
        wave.scale.set(scale, scale, 1)
        wave.material.opacity = 0.3 - (scale - 1) * 0.5
      }
    })
  })

  return (
    <group position={[0, 0, -8]}>
      {[0, 1, 2, 3].map((i) => (
        <Ring
          key={i}
          ref={(el) => (waveRefs.current[i] = el)}
          args={[2 + i * 0.8, 2.1 + i * 0.8, 64]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <meshBasicMaterial color="#8B5CF6" transparent opacity={0.3} side={THREE.DoubleSide} />
        </Ring>
      ))}
    </group>
  )
}

function ParticleNebula({ count = 500 }) {
  const pointsRef = useRef()
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const colors = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      const r = 8 + Math.random() * 4
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.5
      pos[i * 3 + 2] = r * Math.cos(phi)

      const color = Math.random() > 0.5 ? [0.545, 0.361, 0.965] : [0.024, 0.714, 0.831]
      colors[i * 3] = color[0]
      colors[i * 3 + 1] = color[1]
      colors[i * 3 + 2] = color[2]
    }
    return { pos, colors }
  }, [count])

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.03
      pointsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions.pos} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={count} array={positions.colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.08} vertexColors transparent opacity={0.8} />
    </points>
  )
}

function FloatingShape({ position, color, shape = "sphere", scale = 0.5 }) {
  const meshRef = useRef()

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime + position[0]) * 0.5
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3
    }
  })

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={1.5}>
      <mesh ref={meshRef} position={position}>
        {shape === "sphere" && <sphereGeometry args={[scale, 32, 32]} />}
        {shape === "box" && <boxGeometry args={[scale, scale, scale]} />}
        {shape === "torus" && <torusGeometry args={[scale, scale * 0.4, 16, 32]} />}
        {shape === "icosahedron" && <icosahedronGeometry args={[scale]} />}
        <MeshDistortMaterial
          color={color}
          distort={0.4}
          speed={2}
          roughness={0.2}
          metalness={0.8}
          emissive={color}
          emissiveIntensity={0.4}
        />
      </mesh>
    </Float>
  )
}

function FeatureScene() {
  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[5, 5, 5]} intensity={2} color="#8B5CF6" />
      <pointLight position={[-5, -5, 5]} intensity={1} color="#06B6D4" />
      <pointLight position={[0, 0, 10]} intensity={0.5} color="#A855F7" />

      <DNAHelix />
      <HolographicCubes />
      <EnergyWaves />
      <ParticleNebula count={600} />

      <FloatingShape position={[-4, 2, -2]} color="#8B5CF6" shape="sphere" scale={0.6} />
      <FloatingShape position={[4, -1, -3]} color="#06B6D4" shape="box" scale={0.5} />
      <FloatingShape position={[0, 3, -1]} color="#A855F7" shape="torus" scale={0.4} />
      <FloatingShape position={[-3, -2, -2]} color="#22D3EE" shape="icosahedron" scale={0.4} />
    </>
  )
}

function FeatureCard({ icon: Icon, title, description, stats, index, isHovered, onHover }) {
  return (
    <div
      className={`relative group cursor-pointer transition-all duration-500 opacity-0 animate-slide-up`}
      style={{ animationDelay: `${index * 100}ms`, animationFillMode: "forwards" }}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
    >
      <div
        className={`glass rounded-2xl p-8 h-full glow-border transition-all duration-300 ${
          isHovered ? "glow-box translate-y-[-10px]" : ""
        }`}
      >
        <div className="relative mb-6">
          <div
            className={`w-16 h-16 rounded-2xl bg-gradient-to-br from-[#8b5cf6]/20 to-[#06b6d4]/20 flex items-center justify-center transition-all duration-300 ${
              isHovered ? "scale-110 rotate-6" : ""
            }`}
          >
            <Icon className="w-8 h-8 text-[#8b5cf6]" />
          </div>
          {isHovered && <div className="absolute -inset-4 bg-[#8b5cf6]/20 blur-2xl rounded-full animate-pulse-glow" />}
        </div>

        <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
        <p className="text-white/60 mb-6 leading-relaxed">{description}</p>

        <div className="flex items-center gap-4 text-sm">
          <span className="text-[#8b5cf6] font-bold text-lg">{stats.value}</span>
          <span className="text-white/50">{stats.label}</span>
        </div>

        <div
          className={`absolute -bottom-1 left-1/2 -translate-x-1/2 h-1 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] rounded-full transition-all duration-300 ${
            isHovered ? "w-1/2" : "w-0"
          }`}
        />
      </div>
    </div>
  )
}

export default function FeaturesSection() {
  const [hoveredIndex, setHoveredIndex] = useState(null)

  const features = [
    {
      icon: Brain,
      title: "AI Content Generation",
      description: "GPT-4 powered content creation in 12+ languages with 95% engagement rate optimization.",
      stats: { value: "95%", label: "Engagement Rate" },
    },
    {
      icon: Zap,
      title: "Smart Scheduling",
      description: "AI predicts optimal posting times based on your audience behavior for 5x more reach.",
      stats: { value: "5x", label: "More Reach" },
    },
    {
      icon: BarChart3,
      title: "Real-Time Analytics",
      description: "Track every metric that matters with 300% better insights and actionable recommendations.",
      stats: { value: "300%", label: "Better Insights" },
    },
    {
      icon: Target,
      title: "Complete Automation",
      description: "Set it and forget it. Save 20+ hours weekly with intelligent content workflows.",
      stats: { value: "20+", label: "Hours Saved/Week" },
    },
    {
      icon: Link2,
      title: "Multi-Platform Sync",
      description: "5 platforms, 1 dashboard, 1-click posting. Seamless synchronization across all channels.",
      stats: { value: "5", label: "Platforms Connected" },
    },
    {
      icon: TrendingUp,
      title: "AI Growth Engine",
      description: "AI-driven audience growth strategies with 10x faster results.",
      stats: { value: "10x", label: "Faster Growth" },
    },
  ]

  return (
    <section id="features" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 12], fov: 50 }}>
          <FeatureScene />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/70 via-[#0a0a0f]/50 to-[#0a0a0f]/70 z-10" />

      <div className="relative z-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6 border border-[#06b6d4]/30">
            HOLOGRAPHIC LAB
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">Powered by</span>
            <br />
            <span className="gradient-text">Advanced AI Automation</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Six powerful tools working together to transform your social media presence
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              {...feature}
              index={index}
              isHovered={hoveredIndex === index}
              onHover={(isHovered) => setHoveredIndex(isHovered ? index : null)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
