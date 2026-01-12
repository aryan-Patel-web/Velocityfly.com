import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

const YouTubeFeatures3D = () => {
  const canvasContainerRef = useRef(null);
  const [activeFeature, setActiveFeature] = useState(0);

  const features = [
    { title: "AI Video Content Generator", description: "Generate viral YouTube content with AI", highlights: ["Shorts & long videos", "SEO optimized", "Multi-language"], stat: "50,000+ videos generated", icon: "📹" },
    { title: "Thumbnail Studio", description: "High CTR thumbnails", highlights: ["3 designs", "CTR optimized"], stat: "10%+ CTR", icon: "🖼️" },
    { title: "Image Slideshow Videos", description: "Create Shorts from images", highlights: ["2–6 images", "Auto transitions"], stat: "Perfect for affiliates", icon: "🎬" },
    { title: "Smart Scheduling", description: "Best time auto-upload", highlights: ["Indian timings"], stat: "3x more views", icon: "📅" },
    { title: "Auto Replies", description: "AI comment replies", highlights: ["Human-like"], stat: "40% more engagement", icon: "💬" },
    { title: "Analytics", description: "Growth insights", highlights: ["Realtime"], stat: "2x growth", icon: "📊" },
    { title: "Community Automation", description: "Auto posts", highlights: ["Polls"], stat: "50% boost", icon: "👥" },
    { title: "Full Automation", description: "Set & forget", highlights: ["Everything automated"], stat: "20+ hrs saved/week", icon: "⚡" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature(prev => (prev + 1) % 8);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!canvasContainerRef.current) return;

    const container = canvasContainerRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 5, 12);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambientLight);
    const pointLight1 = new THREE.PointLight(0xef4444, 1, 100);
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);
    const pointLight2 = new THREE.PointLight(0x8b5cf6, 0.5, 100);
    pointLight2.position.set(-10, -10, -10);
    scene.add(pointLight2);

    const colors = [0xef4444, 0xf97316, 0xeab308, 0x22c55e, 0x06b6d4, 0x8b5cf6, 0xec4899, 0xf43f5e];
    const platforms = [];
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const geometry = new THREE.CylinderGeometry(0.8, 1, 0.5, 6);
      const material = new THREE.MeshStandardMaterial({
        color: colors[i],
        emissive: colors[i],
        emissiveIntensity: 0.3,
        metalness: 0.8,
        roughness: 0.2
      });
      const platform = new THREE.Mesh(geometry, material);
      platform.position.set(Math.cos(angle) * 4, 0, Math.sin(angle) * 4);
      platform.userData = { angle: angle, index: i };
      scene.add(platform);
      platforms.push(platform);
    }

    const hologramGeom = new THREE.BoxGeometry(1.8, 1.2, 0.15);
    const hologramMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,
      emissive: 0xef4444,
      emissiveIntensity: 0.8,
      transparent: true,
      opacity: 0.9,
      metalness: 0.7,
      roughness: 0.3
    });
    const hologram = new THREE.Mesh(hologramGeom, hologramMat);
    hologram.position.set(0, 2.5, 0);
    scene.add(hologram);

    const rings = [];
    for (let i = 0; i < 4; i++) {
      const ringGeom = new THREE.RingGeometry(0.9 + i * 0.35, 1.0 + i * 0.35, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0xef4444,
        transparent: true,
        opacity: 0.3 - i * 0.06,
        side: THREE.DoubleSide
      });
      const ring = new THREE.Mesh(ringGeom, ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.set(0, 2.5 - 0.6 - i * 0.4, 0);
      scene.add(ring);
      rings.push(ring);
    }

    const particleCount = 400;
    const particleGeom = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const particleColors = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 18;
      positions[i * 3 + 1] = Math.random() * 10 - 2;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 12;
      const color = Math.random() > 0.5 ? [0.937, 0.267, 0.267] : [0.545, 0.361, 0.965];
      particleColors[i * 3] = color[0];
      particleColors[i * 3 + 1] = color[1];
      particleColors[i * 3 + 2] = color[2];
    }
    
    particleGeom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeom.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));
    
    const particleMat = new THREE.PointsMaterial({
      size: 0.1,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true
    });
    
    const particles = new THREE.Points(particleGeom, particleMat);
    scene.add(particles);

    const clock = new THREE.Clock();
    let animationId;

    function animate() {
      const t = clock.getElapsedTime();

      platforms.forEach((platform, i) => {
        const angle = platform.userData.angle + t * 0.08;
        platform.position.x = Math.cos(angle) * 4;
        platform.position.z = Math.sin(angle) * 4;
        platform.position.y = Math.sin(t * 2 + i) * 0.3;
        
        const isActive = activeFeature === i;
        platform.material.emissiveIntensity += (isActive ? 1.2 : 0.3 - platform.material.emissiveIntensity) * 0.1;
        const targetScale = isActive ? 2.5 : 1;
        platform.scale.y += (targetScale - platform.scale.y) * 0.1;
      });

      hologram.rotation.y = t * 0.4;
      hologram.rotation.z = Math.sin(t * 0.5) * 0.1;
      hologram.position.y = 2.5 + Math.sin(t * 2.5) * 0.5;

      rings.forEach((ring, i) => {
        ring.rotation.z = t * (0.4 + i * 0.15);
        const scale = 1 + Math.sin(t * 2 + i) * 0.1;
        ring.scale.set(scale, scale, 1);
      });

      particles.rotation.y = t * 0.03;
      const pos = particles.geometry.attributes.position.array;
      for (let i = 0; i < particleCount; i++) {
        pos[i * 3 + 1] += Math.sin(t + i) * 0.002;
      }
      particles.geometry.attributes.position.needsUpdate = true;

      renderer.render(scene, camera);
      animationId = requestAnimationFrame(animate);
    }
    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationId);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, [activeFeature]);

  return (
    <div style={{ margin: 0, overflowX: 'hidden', fontFamily: 'system-ui, -apple-system, sans-serif', background: 'linear-gradient(to bottom, #000000, #111827, #000000)' }}>
      <section className="relative min-h-screen py-20">
        <div ref={canvasContainerRef} style={{ position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none' }} />

        <div className="relative z-10 container mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
              </svg>
              <span className="text-sm font-medium text-red-500">AI-Powered Features</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Everything You Need to
              <span className="block" style={{ background: 'linear-gradient(to right, #ef4444, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                Dominate YouTube
              </span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              8 powerful tools working together to automate your entire YouTube channel
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {features.map((feature, index) => (
              <div
                key={index}
                onClick={() => setActiveFeature(index)}
                className="group relative p-6 rounded-2xl cursor-pointer transition-all duration-500"
                style={{
                  transform: activeFeature === index ? 'scale(1.05)' : 'scale(1)',
                  background: activeFeature === index ? 'linear-gradient(to bottom right, rgba(239, 68, 68, 0.2), rgba(168, 85, 247, 0.2))' : 'rgba(17, 24, 39, 0.5)',
                  border: activeFeature === index ? '2px solid #ef4444' : '1px solid #1f2937',
                  boxShadow: activeFeature === index ? '0 25px 50px -12px rgba(239, 68, 68, 0.2)' : 'none'
                }}
              >
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-all duration-300"
                  style={{
                    backgroundColor: activeFeature === index ? '#ef4444' : '#1f2937',
                    boxShadow: activeFeature === index ? '0 10px 15px -3px rgba(239, 68, 68, 0.5)' : 'none'
                  }}
                >
                  <span className="text-2xl">{feature.icon}</span>
                </div>
                <h3 className="text-lg font-bold mb-2 transition-colors" style={{ color: activeFeature === index ? '#ffffff' : '#d1d5db' }}>
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-400 mb-3">{feature.description}</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {feature.highlights.map((h, i) => (
                    <span key={i} className="text-xs px-2 py-1 rounded-full text-gray-400" style={{ backgroundColor: 'rgba(31, 41, 55, 0.5)' }}>
                      {h}
                    </span>
                  ))}
                </div>
                <div className="text-sm font-semibold" style={{ color: activeFeature === index ? '#f87171' : '#6b7280' }}>
                  {feature.stat}
                </div>
              </div>
            ))}
          </div>

          <div className="max-w-4xl mx-auto rounded-3xl p-8 border border-gray-700" style={{ background: 'linear-gradient(to bottom right, rgba(17, 24, 39, 0.8), rgba(31, 41, 55, 0.8))', backdropFilter: 'blur(40px)' }}>
            <div className="flex flex-col md:flex-row items-start gap-6">
              <div 
                className="w-20 h-20 rounded-2xl flex items-center justify-center flex-shrink-0"
                style={{
                  background: 'linear-gradient(to bottom right, #ef4444, #a855f7)',
                  boxShadow: '0 25px 50px -12px rgba(239, 68, 68, 0.3)',
                  animation: 'float 3s ease-in-out infinite'
                }}
              >
                <span className="text-4xl">{features[activeFeature].icon}</span>
              </div>
              <div className="flex-1">
                <h3 className="text-3xl font-bold text-white mb-3">{features[activeFeature].title}</h3>
                <p className="text-lg text-gray-300 mb-4">{features[activeFeature].description}</p>
                <div className="flex flex-wrap gap-3 mb-6">
                  {features[activeFeature].highlights.map((h, i) => (
                    <div key={i} className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-700" style={{ backgroundColor: 'rgba(31, 41, 55, 0.5)' }}>
                      <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span className="text-sm text-gray-300">{h}</span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-2 text-red-400 font-semibold text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
                  </svg>
                  {features[activeFeature].stat}
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-16">
            <button className="group px-8 py-4 rounded-full text-white font-bold text-lg transition-all duration-300 hover:scale-105" style={{ background: 'linear-gradient(to right, #ef4444, #a855f7)', boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.5)' }}>
              Start Automating Now
              <svg className="inline-block ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
};

export default YouTubeFeatures3D;