"use client"

import { useState, useEffect, useRef } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Stars, Float, Sphere } from "@react-three/drei"
import { ChevronLeft, ChevronRight, Quote, Star, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"

function AuroraBackground() {
  const mesh1 = useRef()
  const mesh2 = useRef()
  const mesh3 = useRef()

  useFrame((state) => {
    if (mesh1.current) {
      mesh1.current.rotation.z = state.clock.elapsedTime * 0.05
      mesh1.current.position.x = Math.sin(state.clock.elapsedTime * 0.1) * 3
    }
    if (mesh2.current) {
      mesh2.current.rotation.z = -state.clock.elapsedTime * 0.03
      mesh2.current.position.x = Math.cos(state.clock.elapsedTime * 0.1) * 3
    }
    if (mesh3.current) {
      mesh3.current.rotation.y = state.clock.elapsedTime * 0.04
      mesh3.current.position.y = Math.sin(state.clock.elapsedTime * 0.15) * 2
    }
  })

  return (
    <>
      <Stars radius={100} depth={50} count={4000} factor={4} saturation={0} fade speed={0.5} />
      <Float speed={0.5} floatIntensity={2}>
        <Sphere ref={mesh1} args={[6, 32, 32]} position={[-6, 0, -12]}>
          <meshBasicMaterial color="#8B5CF6" transparent opacity={0.08} />
        </Sphere>
      </Float>
      <Float speed={0.3} floatIntensity={1.5}>
        <Sphere ref={mesh2} args={[5, 32, 32]} position={[6, 2, -10]}>
          <meshBasicMaterial color="#06B6D4" transparent opacity={0.08} />
        </Sphere>
      </Float>
      <Float speed={0.4} floatIntensity={1}>
        <Sphere ref={mesh3} args={[4, 32, 32]} position={[0, -3, -8]}>
          <meshBasicMaterial color="#A855F7" transparent opacity={0.06} />
        </Sphere>
      </Float>
    </>
  )
}

function TestimonialCard({ testimonial, position }) {
  const { name, role, subscribers, content, avatar, location, stats } = testimonial

  return (
    <div
      className={`absolute top-1/2 left-1/2 w-full max-w-2xl transition-all duration-700 ease-out ${
        position === "center"
          ? "z-20 opacity-100 scale-100 -translate-x-1/2 -translate-y-1/2"
          : position === "left"
            ? "z-10 opacity-40 scale-75 -translate-x-[130%] -translate-y-1/2"
            : "z-10 opacity-40 scale-75 translate-x-[30%] -translate-y-1/2"
      }`}
    >
      <div className={`glass rounded-3xl p-8 md:p-10 ${position === "center" ? "glow-box" : ""}`}>
        <Quote className="w-10 h-10 text-[#8b5cf6]/40 mb-4" />

        <p className="text-base md:text-lg text-white leading-relaxed mb-6">"{content}"</p>

        <div className="flex items-center gap-1 mb-6">
          {[...Array(5)].map((_, i) => (
            <Star key={i} className="w-5 h-5 fill-[#06b6d4] text-[#06b6d4]" />
          ))}
        </div>

        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center text-2xl ring-2 ring-[#8b5cf6]/30">
            {avatar}
          </div>
          <div>
            <h4 className="text-lg font-bold text-white">{name}</h4>
            <p className="text-white/60 text-sm">
              {role} • {subscribers}
            </p>
            <p className="text-[#06b6d4] text-sm flex items-center gap-1">
              <MapPin className="w-3 h-3" /> {location}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          {stats.map((stat, index) => (
            <div key={index} className="glass rounded-lg px-4 py-2">
              <span className="text-[#8b5cf6] font-bold">{stat.value}</span>
              <span className="text-white/50 ml-1 text-sm">{stat.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function TestimonialsSection() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isAutoPlaying, setIsAutoPlaying] = useState(true)

  const testimonials = [
    {
      name: "Rajesh Kumar",
      role: "Tech YouTuber",
      subscribers: "75K Subscribers",
      location: "Mumbai, Maharashtra",
      avatar: "👨‍💻",
      content:
        "VelocityPost completely transformed my YouTube channel. I went from 500 to 50,000 subscribers in just 6 months with automated Shorts. The AI thumbnail creator alone increased my CTR by 12%!",
      stats: [
        { value: "300%", label: "Engagement" },
        { value: "20hrs", label: "Saved/Week" },
        { value: "15", label: "Brand Deals" },
      ],
    },
    {
      name: "Priya Sharma",
      role: "Fashion Influencer",
      subscribers: "120K Followers",
      location: "Bangalore, Karnataka",
      avatar: "👩‍🎨",
      content:
        "Automated 500 Instagram posts in a month! As someone managing multiple brand collaborations, VelocityPost is my secret weapon. The multi-platform sync saves me 4+ hours daily.",
      stats: [
        { value: "500%", label: "ROI" },
        { value: "20+", label: "Brands" },
        { value: "4hrs", label: "Daily Save" },
      ],
    },
    {
      name: "Aryan Patel",
      role: "Digital Marketer",
      subscribers: "Agency Owner",
      location: "Delhi NCR",
      avatar: "👨‍💼",
      content:
        "₹2 lakh monthly revenue from automated content! I manage 15 client accounts and VelocityPost handles everything. Best investment I made for my agency.",
      stats: [
        { value: "₹2L+", label: "Monthly" },
        { value: "15", label: "Clients" },
        { value: "10x", label: "Growth" },
      ],
    },
    {
      name: "Sneha Mehta",
      role: "Food Blogger",
      subscribers: "90K Subscribers",
      location: "Pune, Maharashtra",
      avatar: "👩‍🍳",
      content:
        "YouTube Shorts automation = 10x faster growth! I post 5 Shorts daily without lifting a finger. The AI perfectly captures my cooking content style.",
      stats: [
        { value: "10x", label: "Growth" },
        { value: "5/day", label: "Shorts" },
        { value: "90K", label: "Subs" },
      ],
    },
    {
      name: "Vikram Singh",
      role: "Affiliate Marketer",
      subscribers: "50K+ Audience",
      location: "Jaipur, Rajasthan",
      avatar: "👨‍🚀",
      content:
        "Best ₹749/month I've ever spent! The image slideshow feature turns my product images into viral Shorts. Made ₹45,000 in affiliate commissions last month alone.",
      stats: [
        { value: "₹45K", label: "Commissions" },
        { value: "100+", label: "Videos/Mo" },
        { value: "5x", label: "ROI" },
      ],
    },
  ]

  useEffect(() => {
    if (!isAutoPlaying) return
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [isAutoPlaying, testimonials.length])

  const getPosition = (index) => {
    if (index === currentIndex) return "center"
    if (index === (currentIndex - 1 + testimonials.length) % testimonials.length) return "left"
    if (index === (currentIndex + 1) % testimonials.length) return "right"
    return "hidden"
  }

  return (
    <section id="testimonials" className="relative min-h-screen py-32 overflow-hidden snap-section">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
          <AuroraBackground />
        </Canvas>
      </div>

      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-transparent to-[#0a0a0f] z-10" />

      <div className="relative z-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full glass text-sm text-[#06b6d4] mb-6">VOICE DIMENSION</span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="gradient-text">Loved by 50,000+</span>
            <br />
            <span className="text-white">Indian Creators</span>
          </h2>
          <p className="text-lg text-white/60">Real stories. Real growth. Real results.</p>
        </div>

        <div
          className="relative h-[520px] md:h-[480px]"
          onMouseEnter={() => setIsAutoPlaying(false)}
          onMouseLeave={() => setIsAutoPlaying(true)}
        >
          {testimonials.map((testimonial, index) => (
            <TestimonialCard key={index} testimonial={testimonial} position={getPosition(index)} />
          ))}
        </div>

        <div className="flex items-center justify-center gap-4 mt-8">
          <Button
            variant="outline"
            size="icon"
            className="rounded-full border-[#8b5cf6]/50 hover:bg-[#8b5cf6]/10 bg-transparent text-white"
            onClick={() => setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length)}
          >
            <ChevronLeft className="w-5 h-5" />
          </Button>

          <div className="flex gap-2">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  index === currentIndex ? "bg-[#8b5cf6] w-8" : "bg-white/30 w-2 hover:bg-white/50"
                }`}
              />
            ))}
          </div>

          <Button
            variant="outline"
            size="icon"
            className="rounded-full border-[#8b5cf6]/50 hover:bg-[#8b5cf6]/10 bg-transparent text-white"
            onClick={() => setCurrentIndex((prev) => (prev + 1) % testimonials.length)}
          >
            <ChevronRight className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </section>
  )
}
