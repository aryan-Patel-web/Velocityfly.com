import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../quickpage/AuthContext";

function NavParticles() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;
    let particles = [];

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = 80;
    };

    const createParticles = () => {
      particles = [];
      for (let i = 0; i < 50; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          size: Math.random() * 2 + 0.5,
          speedX: (Math.random() - 0.5) * 0.5,
          speedY: (Math.random() - 0.5) * 0.3,
          opacity: Math.random() * 0.5 + 0.2,
        });
      }
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((particle) => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        const gradient = ctx.createRadialGradient(
          particle.x,
          particle.y,
          0,
          particle.x,
          particle.y,
          particle.size * 2
        );
        gradient.addColorStop(0, `rgba(139, 92, 246, ${particle.opacity})`);
        gradient.addColorStop(1, `rgba(6, 182, 212, 0)`);

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    resizeCanvas();
    createParticles();
    animate();

    const handleResize = () => {
      resizeCanvas();
      createParticles();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
    />
  );
}

const MenuIcon = () => (
  <svg
    style={{ width: "24px", height: "24px" }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M4 6h16M4 12h16M4 18h16"
    />
  </svg>
);

const XIcon = () => (
  <svg
    style={{ width: "24px", height: "24px" }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);

const ZapIcon = () => (
  <svg
    style={{ width: "24px", height: "24px", color: "white" }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M13 10V3L4 14h7v7l9-11h-7z"
    />
  </svg>
);

const ChevronDownIcon = ({ size = "16px" }) => (
  <svg
    style={{ width: size, height: size }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M19 9l-7 7-7-7"
    />
  </svg>
);

const UserIcon = () => (
  <svg
    style={{ width: "16px", height: "16px", color: "white" }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
    />
  </svg>
);

const LayoutDashboardIcon = () => (
  <svg
    style={{ width: "16px", height: "16px" }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
    />
  </svg>
);

const LogOutIcon = () => (
  <svg
    style={{ width: "16px", height: "16px" }}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
    />
  </svg>
);

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
    setIsMobileMenuOpen(false);
    navigate("/");
  };

  const handleLogin = () => {
    navigate("/login");
  };

  const handleSignup = () => {
    navigate("/register");
  };

  const handleDashboard = () => {
    navigate("/youtube");
  };

  const navLinks = [
    { name: "Platforms", href: "#platforms" },
    { name: "Features", href: "#features" },
    {
      name: "YouTube",
      href: "#youtube",
      dropdown: [
        { name: "YouTube Studio", href: "#youtube" },
        { name: "Deep Dive Features", href: "#youtube-features" },
      ],
    },
    { name: "Pricing", href: "#pricing" },
    { name: "How It Works", href: "#how-it-works" },
  ];

  const navStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 50,
    transition: "all 0.5s",
    backgroundColor: isScrolled ? "rgba(10, 10, 15, 0.9)" : "transparent",
    backdropFilter: isScrolled ? "blur(40px)" : "none",
    borderBottom: isScrolled ? "1px solid rgba(255, 255, 255, 0.05)" : "none",
    padding: isScrolled ? "8px 0" : "16px 0",
  };

  const buttonStyle = {
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontWeight: "600",
    transition: "all 0.2s",
  };

  const primaryButtonStyle = {
    ...buttonStyle,
    background: "linear-gradient(to right, #8b5cf6, #06b6d4)",
    color: "white",
  };

  const ghostButtonStyle = {
    ...buttonStyle,
    background: "transparent",
    color: "rgba(255, 255, 255, 0.7)",
    border: "1px solid transparent",
  };

  return (
    <>
      <nav style={navStyle}>
        {isScrolled && <NavParticles />}

        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "1px",
            background:
              "linear-gradient(to right, transparent, rgba(139, 92, 246, 0.5), transparent)",
          }}
        />

        <div
          style={{
            position: "relative",
            maxWidth: "1280px",
            margin: "0 auto",
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <a
            href="/"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              textDecoration: "none",
            }}
          >
            <div style={{ position: "relative" }}>
              <div
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "12px",
                  background: "linear-gradient(to bottom right, #8b5cf6, #06b6d4)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <ZapIcon />
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span
                style={{
                  fontSize: "20px",
                  fontWeight: "bold",
                  background:
                    "linear-gradient(to right, white, rgba(255, 255, 255, 0.8))",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                VelocityPost
              </span>
              <span
                style={{
                  fontSize: "10px",
                  color: "#06b6d4",
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                }}
              >
                AI Automation
              </span>
            </div>
          </a>

          {/* Desktop Navigation */}
          <div
            className="desktop-nav"
            style={{ display: "flex", alignItems: "center", gap: "4px" }}
          >
            {navLinks.map((link) => (
              <div
                key={link.name}
                style={{ position: "relative" }}
                onMouseEnter={() => link.dropdown && setActiveDropdown(link.name)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <a
                  href={link.href}
                  style={{
                    padding: "8px 16px",
                    color: "rgba(255, 255, 255, 0.7)",
                    textDecoration: "none",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    borderRadius: "8px",
                    transition: "all 0.2s",
                  }}
                  className="nav-link"
                >
                  {link.name}
                  {link.dropdown && <ChevronDownIcon size="12px" />}
                </a>

                {link.dropdown && activeDropdown === link.name && (
                  <div
                    style={{
                      position: "absolute",
                      top: "100%",
                      left: 0,
                      marginTop: "8px",
                      width: "192px",
                      padding: "8px 0",
                      background: "rgba(19, 17, 28, 0.95)",
                      backdropFilter: "blur(40px)",
                      borderRadius: "12px",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                    }}
                  >
                    {link.dropdown.map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                        style={{
                          display: "block",
                          padding: "8px 16px",
                          fontSize: "14px",
                          color: "rgba(255, 255, 255, 0.7)",
                          textDecoration: "none",
                          transition: "all 0.2s",
                        }}
                        className="dropdown-link"
                      >
                        {item.name}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Desktop Actions */}
          <div
            className="desktop-actions"
            style={{ display: "flex", alignItems: "center", gap: "12px" }}
          >
            {isAuthenticated && user ? (
              <div style={{ position: "relative" }}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 16px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.05)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  className="user-menu-btn"
                >
                  <div
                    style={{
                      width: "32px",
                      height: "32px",
                      borderRadius: "50%",
                      background:
                        "linear-gradient(to bottom right, #8b5cf6, #06b6d4)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <UserIcon />
                  </div>
                  <span
                    style={{
                      color: "rgba(255, 255, 255, 0.8)",
                      fontSize: "14px",
                      maxWidth: "150px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {user.email || user.name}
                  </span>
                  <ChevronDownIcon size="16px" />
                </button>

                {showUserMenu && (
                  <>
                    <div
                      style={{ position: "fixed", inset: 0, zIndex: 40 }}
                      onClick={() => setShowUserMenu(false)}
                    />
                    <div
                      style={{
                        position: "absolute",
                        top: "100%",
                        right: 0,
                        marginTop: "8px",
                        width: "224px",
                        padding: "8px 0",
                        background: "rgba(19, 17, 28, 0.95)",
                        backdropFilter: "blur(40px)",
                        borderRadius: "12px",
                        border: "1px solid rgba(255, 255, 255, 0.1)",
                        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                        zIndex: 50,
                      }}
                    >
                      <div
                        style={{
                          padding: "8px 16px",
                          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
                        }}
                      >
                        <p
                          style={{
                            fontSize: "12px",
                            color: "rgba(255, 255, 255, 0.5)",
                            margin: 0,
                          }}
                        >
                          Signed in as
                        </p>
                        <p
                          style={{
                            fontSize: "14px",
                            color: "white",
                            margin: "4px 0 0 0",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {user.email || user.name}
                        </p>
                      </div>

                      <button
                        onClick={handleDashboard}
                        style={{
                          width: "100%",
                          display: "flex",
                          alignItems: "center",
                          gap: "12px",
                          padding: "8px 16px",
                          fontSize: "14px",
                          color: "rgba(255, 255, 255, 0.7)",
                          background: "transparent",
                          border: "none",
                          cursor: "pointer",
                          textAlign: "left",
                          transition: "all 0.2s",
                        }}
                        className="menu-item"
                      >
                        <LayoutDashboardIcon />
                        Dashboard
                      </button>

                      <div
                        style={{
                          borderTop: "1px solid rgba(255, 255, 255, 0.1)",
                          marginTop: "8px",
                          paddingTop: "8px",
                        }}
                      >
                        <button
                          onClick={handleLogout}
                          style={{
                            width: "100%",
                            display: "flex",
                            alignItems: "center",
                            gap: "12px",
                            padding: "8px 16px",
                            fontSize: "14px",
                            color: "#f87171",
                            background: "transparent",
                            border: "none",
                            cursor: "pointer",
                            textAlign: "left",
                            transition: "all 0.2s",
                          }}
                          className="menu-item"
                        >
                          <LogOutIcon />
                          Log Out
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <>
                <button onClick={handleLogin} style={ghostButtonStyle} className="ghost-btn">
                  Log In
                </button>
                <button onClick={handleSignup} style={primaryButtonStyle} className="primary-btn">
                  Start Free Trial
                </button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="mobile-menu-btn"
            style={{
              display: "none",
              color: "white",
              padding: "8px",
              borderRadius: "8px",
              border: "none",
              background: "transparent",
              cursor: "pointer",
            }}
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <XIcon /> : <MenuIcon />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div
            style={{
              position: "absolute",
              top: "100%",
              left: 0,
              right: 0,
              background: "rgba(10, 10, 15, 0.98)",
              backdropFilter: "blur(40px)",
              borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
              padding: "16px",
            }}
          >
            {navLinks.map((link) => (
              <div key={link.name} style={{ marginBottom: "8px" }}>
                <a
                  href={link.href}
                  style={{
                    display: "block",
                    padding: "12px 16px",
                    color: "rgba(255, 255, 255, 0.8)",
                    textDecoration: "none",
                    borderRadius: "8px",
                    transition: "all 0.2s",
                  }}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.name}
                </a>
                {link.dropdown && (
                  <div style={{ paddingLeft: "16px" }}>
                    {link.dropdown.map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                        style={{
                          display: "block",
                          padding: "8px 16px",
                          color: "rgba(255, 255, 255, 0.6)",
                          textDecoration: "none",
                          fontSize: "14px",
                        }}
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        {item.name}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}

            <div style={{ marginTop: "16px", paddingTop: "16px", borderTop: "1px solid rgba(255, 255, 255, 0.1)" }}>
              {isAuthenticated && user ? (
                <>
                  <div style={{ padding: "12px 16px", marginBottom: "8px" }}>
                    <p style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.5)", margin: 0 }}>
                      Signed in as
                    </p>
                    <p style={{ fontSize: "14px", color: "white", margin: "4px 0 0 0" }}>
                      {user.email || user.name}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      handleDashboard();
                      setIsMobileMenuOpen(false);
                    }}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      marginBottom: "8px",
                      background: "linear-gradient(to right, #8b5cf6, #06b6d4)",
                      color: "white",
                      border: "none",
                      borderRadius: "8px",
                      cursor: "pointer",
                      fontWeight: "600",
                    }}
                  >
                    Go to Dashboard
                  </button>
                  <button
                    onClick={handleLogout}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      background: "transparent",
                      color: "#f87171",
                      border: "1px solid #f87171",
                      borderRadius: "8px",
                      cursor: "pointer",
                      fontWeight: "600",
                    }}
                  >
                    Log Out
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => {
                      handleLogin();
                      setIsMobileMenuOpen(false);
                    }}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      marginBottom: "8px",
                      background: "transparent",
                      color: "rgba(255, 255, 255, 0.8)",
                      border: "1px solid rgba(255, 255, 255, 0.2)",
                      borderRadius: "8px",
                      cursor: "pointer",
                      fontWeight: "600",
                    }}
                  >
                    Log In
                  </button>
                  <button
                    onClick={() => {
                      handleSignup();
                      setIsMobileMenuOpen(false);
                    }}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      background: "linear-gradient(to right, #8b5cf6, #06b6d4)",
                      color: "white",
                      border: "none",
                      borderRadius: "8px",
                      cursor: "pointer",
                      fontWeight: "600",
                    }}
                  >
                    Start Free Trial
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </nav>

      <style>{`
        .nav-link:hover {
          background: rgba(255, 255, 255, 0.05);
          color: white;
        }

        .dropdown-link:hover {
          background: rgba(255, 255, 255, 0.05);
          color: white;
        }

        .user-menu-btn:hover {
          background: rgba(255, 255, 255, 0.08);
        }

        .menu-item:hover {
          background: rgba(255, 255, 255, 0.05);
        }

        .ghost-btn:hover {
          background: rgba(255, 255, 255, 0.05);
          border-color: rgba(255, 255, 255, 0.2);
        }

        .primary-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(139, 92, 246, 0.3);
        }

        @media (max-width: 1024px) {
          .desktop-nav {
            display: none !important;
          }
          .desktop-actions {
            display: none !important;
          }
          .mobile-menu-btn {
            display: block !important;
          }
        }
      `}</style>
    </>
  );
}