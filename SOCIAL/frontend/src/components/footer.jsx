"use client"

import { Zap, Twitter, Linkedin, Youtube, Instagram, Mail, Phone, MapPin } from "lucide-react"

export default function Footer() {
  const footerLinks = [
    {
      title: "Product",
      links: ["Features", "Pricing", "Integrations", "API Docs", "Roadmap", "Status Page"],
    },
    {
      title: "Company",
      links: ["About Us", "Careers", "Contact", "Blog", "Press Kit", "Partners"],
    },
    {
      title: "Legal",
      links: ["Privacy Policy", "Terms of Service", "Refund Policy", "GDPR", "Cookie Policy"],
    },
  ]

  const socialLinks = [
    { icon: Twitter, href: "#", label: "Twitter" },
    { icon: Linkedin, href: "#", label: "LinkedIn" },
    { icon: Instagram, href: "#", label: "Instagram" },
    { icon: Youtube, href: "#", label: "YouTube" },
  ]

  return (
    <footer className="relative py-16 border-t border-white/10 bg-[#0a0a0f]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          <div className="col-span-2">
            <a href="#hero" className="flex items-center gap-2 mb-4">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
              </div>
              <span className="text-xl font-bold text-white">VelocityPost</span>
            </a>
            <p className="text-white/50 text-sm mb-4 max-w-xs">
              Automate. Grow. Dominate.
              <br />
              AI-powered social media automation for Indian creators.
            </p>

            <div className="space-y-2 text-sm text-white/50 mb-6">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#8b5cf6]" />
                <span>Bangalore, Karnataka, India</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-[#8b5cf6]" />
                <span>hello@velocitypost.ai</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-[#8b5cf6]" />
                <span>+91-98765-43210</span>
              </div>
            </div>

            <div className="flex gap-3">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  aria-label={social.label}
                  className="w-10 h-10 rounded-xl glass flex items-center justify-center text-white/50 hover:text-white hover:glow-box transition-all duration-300"
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>

          {footerLinks.map((section, index) => (
            <div key={index}>
              <h4 className="text-white font-semibold mb-4">{section.title}</h4>
              <ul className="space-y-2">
                {section.links.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <a href="#" className="text-white/50 hover:text-white transition-colors text-sm">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-white/40 text-sm">© 2026 VelocityPost. All rights reserved.</p>
          <div className="flex items-center gap-2 text-sm text-white/40">
            <span>🇮🇳</span>
            <span>Proudly Made in India for Indian Creators</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
