"use client"

import { useRef, useState, useEffect } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Sphere, Float, Cylinder, Box } from "@react-three/drei"
import { UserPlus, Settings, Sparkles, Calendar, TrendingUp, ArrowRight, Check, Clock } from "lucide-react"

function ConveyorBelt() {
  const beltRef = useRef()

  useFrame((state) => {
    if (beltRef.current) {
      beltRef.current.position.x = ((state.clock.elapsedTime * 0.5) % 10) - 5
    }
  })

  return (
    <group>
      <Box args={[20, 0.2, 2]} position={[0, -2, 0]}>
        <meshStandardMaterial color="#1a1625" metalness={0.8} roughness={0.2} />
      </Box>
      <group ref={beltRef}>
        {[...Array(20)].map((_, i) => (
          <Box key={i} args={[0.1, 0.1, 2]} position={[-10 + i, -1.85, 0]}>
            <meshStandardMaterial color="#8B5CF6" emissive="#8B5CF6" emissiveIntensity={0.3} />
          </Box>
        ))}
      </group>
    </group>
  )
}

function ProcessNode({ position, color, isActive, index }) {
  const nodeRef = useRef()
  const glowRef = useRef()

  useFrame((state) => {
    if (nodeRef.current) {
      nodeRef.current.rotation.y = state.clock.elapsedTime * 0.5
      if (isActive) {
        nodeRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2) * 0.2
      }
    }
    if (glowRef.current && isActive) {
      glowRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.2)
    }
  })

  return (
    <group position={position}>
      <Float speed={isActive ? 2 : 0.5} floatIntensity={isActive ? 1 : 0.3}>
        <Sphere ref={nodeRef} args={[0.6, 32, 32]}>
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isActive ? 0.8 : 0.3}
            metalness={0.6}
            roughness={0.3}
          />
        </Sphere>
      </Float>
      {isActive && (
        <Sphere ref={glowRef} args={[0.9, 16, 16]}>
          <meshBasicMaterial color={color} transparent opacity={0.2} />
        </Sphere>
      )}
      <Cylinder args={[0.05, 0.05, 2, 8]} position={[0, -1.5, 0]}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={isActive ? 0.5 : 0.1} />
      </Cylinder>
    </group>
  )
}

function DataParticles({ startPos, endPos, color }) {
  const particlesRef = useRef()
  const count = 20

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array
      for (let i = 0; i < count; i++) {
        const t = (state.clock.elapsedTime * 0.5 + i * 0.1) % 1
        positions[i * 3] = startPos[0] + (endPos[0] - startPos[0]) * t
        positions[i * 3 + 1] = startPos[1] + (endPos[1] - startPos[1]) * t + Math.sin(t * Math.PI) * 0.5
        positions[i * 3 + 2] = startPos[2] + (endPos[2] - startPos[2]) * t
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
      <pointsMaterial size={0.08} color={color} transparent opacity={0.8} />
    </points>
  )
}

function HowItWorksScene({ activeStep }) {
  const colors = ["#8B5CF6", "#A855F7", "#06B6D4", "#22D3EE", "#3B82F6"]
  const positions = [
    [-4, 0, 0],
    [-2, 0, 0],
    [0, 0, 0],
    [2, 0, 0],
    [4, 0, 0],
  ]

  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 5, 5]} intensity={1.5} color="#8B5CF6" />
      <pointLight position={[-5, 3, 3]} intensity={0.8} color="#06B6D4" />
      <ConveyorBelt />
      {positions.map((pos, i) => (
        <ProcessNode key={i} position={pos} color={colors[i]} isActive={activeStep === i} index={i} />
      ))}
      {positions.slice(0, -1).map((pos, i) => (
        <DataParticles key={`particles-${i}`} startPos={pos} endPos={positions[i + 1]} color={colors[i]} />
      ))}
    </>
  )
}

function StepCard({ step, index, isActive, onClick }) {
  const { icon: Icon, title, description, details, time } = step

  return (
    <div
      className={`glass rounded-2xl p-6 transition-all duration-500 cursor-pointer ${
        isActive ? "glow-box border-[#8b5cf6]/50 scale-105" : "glow-border hover:border-[#8b5cf6]/30"
      }`}
      onClick={onClick}
    >
      <div className="flex items-start gap-4">
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-all ${
            isActive ? "bg-gradient-to-br from-[#8b5cf6] to-[#06b6d4]" : "bg-[#8b5cf6]/20"
          }`}
        >
          <Icon className={`w-6 h-6 ${isActive ? "text-white" : "text-[#8b5cf6]"}`} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[#06b6d4] text-sm font-mono">Step {index + 1}</span>
            <div className="flex items-center gap-1 text-white/40 text-xs">
              <Clock className="w-3 h-3" />
              {time}
            </div>
          </div>
          <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
          <p className="text-sm text-white/60 mb-3">{description}</p>

          {isActive && (
            <div className="space-y-2 animate-fade-in">
              {details.map((detail, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-white/70">
                  <Check className="w-4 h-4 text-[#06b6d4] flex-shrink-0" />
                  {detail}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function HowItWorksSection() {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 5)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const steps = [
    {
      icon: UserPlus,
      title: "Sign Up & Connect Accounts",
      description: "Create your free account and connect your social platforms",
      time: "30 seconds",
      details: [
        "Create free account (email or Google)",
        "Connect YouTube, Instagram, Facebook, WhatsApp",
        "One-click OAuth authentication",
        "Secure 256-bit SSL encryption",
      ],
    },
    {
      icon: Settings,
      title: "Set Your Preferences",
      description: "Configure your content strategy and brand voice",
      time: "1 minute",
      details: [
        "Choose content type (Shorts, Reels, Posts)",
        "Select posting frequency (1-10 per day)",
        "Set target audience & language (Hindi/English)",
        "Define content topics & keywords",
      ],
    },
    {
      icon: Sparkles,
      title: "AI Generates Your Content",
      description: "Watch AI create viral-worthy content instantly",
      time: "10 seconds/video",
      details: [
        "GPT-4 creates viral content ideas",
        "AI generates titles, descriptions, tags",
        "Creates 3 thumbnail options per video",
        "Predicts engagement score (1-100)",
      ],
    },
    {
      icon: Calendar,
      title: "Review & Schedule",
      description: "Approve content or enable full autopilot mode",
      time: "1 minute (or 0 if autopilot)",
      details: [
        "Preview all generated content",
        "Edit anything you want (or trust AI 100%)",
        "Schedule at AI-predicted best times",
        "Batch schedule 100+ posts at once",
      ],
    },
    {
      icon: TrendingUp,
      title: "Track Growth & Scale",
      description: "Monitor results and let AI optimize continuously",
      time: "Set it and forget it",
      details: [
        "Monitor views, engagement, subscribers",
        "AI suggests improvements based on data",
        "Auto-adjusts posting times for max reach",
        "Watch your audience grow on autopilot",
      ],
    },
  ]

  return (
    <section id="how-it-works" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0 opacity-50">
        <Canvas camera={{ position: [0, 3, 10], fov: 50 }}>
          <HowItWorksScene activeStep={activeStep} />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-[#0a0a0f]/90 to-[#0a0a0f] z-10" />

      <div className="relative z-20 max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6">
            PROCESS PIPELINE
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="text-white">Get Started in</span>
            <br />
            <span className="gradient-text">3 Minutes</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">From zero to fully automated in 5 simple steps</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {steps.slice(0, 3).map((step, index) => (
            <StepCard
              key={index}
              step={step}
              index={index}
              isActive={activeStep === index}
              onClick={() => setActiveStep(index)}
            />
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-12">
          {steps.slice(3).map((step, index) => (
            <StepCard
              key={index + 3}
              step={step}
              index={index + 3}
              isActive={activeStep === index + 3}
              onClick={() => setActiveStep(index + 3)}
            />
          ))}
        </div>

        <div className="text-center">
          <div className="glass rounded-2xl p-8 max-w-xl mx-auto glow-box">
            <div className="text-5xl font-bold gradient-text mb-2">3 Minutes</div>
            <p className="text-white/60 mb-4">Total Setup Time</p>
            <p className="text-[#06b6d4] font-medium mb-6">Then 20+ hours saved every week</p>
            <button className="px-8 py-4 bg-gradient-to-r from-[#8b5cf6] to-[#06b6d4] hover:opacity-90 text-white rounded-xl font-semibold transition-all inline-flex items-center gap-2 glow-box">
              Start Your 14-Day Free Trial
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
