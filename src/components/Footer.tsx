import { motion } from "framer-motion";
import { Mail, Github, FileText, Twitter, Linkedin, ExternalLink } from "lucide-react";
import agsaLogo from "@/assets/agsa-logo.jpg";

const Footer = () => {
  const links = {
    product: [
      { name: "Features", href: "#features" },
      { name: "Demo", href: "#demo" },
      { name: "Pricing", href: "#pricing" },
      { name: "API Docs", href: "#docs", external: true }
    ],
    company: [
      { name: "About", href: "#about" },
      { name: "Blog", href: "#blog", external: true },
      { name: "Careers", href: "#careers", external: true },
      { name: "Contact", href: "#contact" }
    ],
    resources: [
      { name: "Documentation", href: "#docs", external: true },
      { name: "GitHub", href: "#github", external: true },
      { name: "Support", href: "#support" },
      { name: "Status", href: "#status", external: true }
    ],
    legal: [
      { name: "Privacy Policy", href: "#privacy" },
      { name: "Terms of Service", href: "#terms" },
      { name: "Cookie Policy", href: "#cookies" },
      { name: "Accessibility", href: "#accessibility" }
    ]
  };

  const socialLinks = [
    { name: "Twitter", icon: Twitter, href: "#twitter" },
    { name: "LinkedIn", icon: Linkedin, href: "#linkedin" },
    { name: "GitHub", icon: Github, href: "#github" },
    { name: "Email", icon: Mail, href: "mailto:contact@agsa.gov.in" }
  ];

  return (
    <footer className="bg-muted-light border-t border-border">
      <div className="container mx-auto px-4">
        {/* Main Footer Content */}
        <div className="py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="flex items-center gap-3"
            >
              <img 
                src={agsaLogo} 
                alt="AGSA Logo" 
                className="w-12 h-12 rounded-xl shadow-soft"
              />
              <div>
                <h3 className="text-xl font-bold text-foreground">AGSA</h3>
                <p className="text-sm text-muted-foreground">Automated Government Service Agent</p>
              </div>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              className="text-muted-foreground leading-relaxed"
            >
              Your Agentic AI for Government Services. Simplifying access to government schemes and services through intelligent AI assistance that understands your needs and speaks your language.
            </motion.p>

            {/* Social Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="flex gap-3"
            >
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  className="w-10 h-10 bg-background rounded-lg flex items-center justify-center hover:bg-primary hover:text-white transition-all duration-200 shadow-soft hover:shadow-medium hover:translate-y-[-1px] group"
                  aria-label={social.name}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </motion.div>
          </div>

          {/* Links Sections */}
          {Object.entries(links).map(([category, categoryLinks], categoryIndex) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 + categoryIndex * 0.1 }}
              viewport={{ once: true }}
              className="space-y-4"
            >
              <h4 className="font-semibold text-foreground capitalize">
                {category}
              </h4>
              <ul className="space-y-3">
                {categoryLinks.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-muted-foreground hover:text-primary transition-colors duration-200 flex items-center gap-1 group"
                      {...(link.external && { target: "_blank", rel: "noopener noreferrer" })}
                    >
                      <span className="group-hover:underline">{link.name}</span>
                      {link.external && (
                        <ExternalLink className="w-3 h-3 opacity-60" />
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Bottom Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          viewport={{ once: true }}
          className="py-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <div className="flex flex-col md:flex-row items-center gap-4 text-sm text-muted-foreground">
            <p>© 2024 AGSA. All rights reserved.</p>
            <div className="flex items-center gap-4">
              <span className="hidden md:block">|</span>
              <span>Built with ❤️ for Digital India</span>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm">
            <a
              href="#github"
              className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors duration-200"
            >
              <Github className="w-4 h-4" />
              <span>Open Source</span>
            </a>
            <a
              href="#docs"
              className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors duration-200"
            >
              <FileText className="w-4 h-4" />
              <span>Documentation</span>
            </a>
          </div>
        </motion.div>

        {/* Status Indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
          viewport={{ once: true }}
          className="pb-6"
        >
          <div className="bg-primary-light rounded-lg p-4 text-center">
            <div className="flex items-center justify-center gap-2 text-sm">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <span className="text-primary font-medium">
                All systems operational
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </footer>
  );
};

export default Footer;