import { motion } from "framer-motion";
import { 
  Bot, 
  Globe, 
  Shield, 
  Smartphone, 
  Link, 
  Zap,
  Brain,
  Languages,
  Lock,
  Wifi,
  Database,
  MessageSquare
} from "lucide-react";

const features = [
  {
    id: 1,
    title: "Multi-Agent Orchestration",
    description: "Powered by IBM Granite models, our AI agents work together to understand your needs and provide comprehensive assistance across all government services.",
    icon: Bot,
    color: "primary",
    highlights: ["IBM Granite Models", "Intelligent Coordination", "Context Awareness"]
  },
  {
    id: 2,
    title: "Multilingual Voice & Text",
    description: "Communicate naturally in any of 22+ Indian languages through voice or text. Our Bhashini integration ensures accurate understanding and responses.",
    icon: Languages,
    color: "secondary",
    highlights: ["22+ Indian Languages", "Voice Recognition", "Bhashini Integration"]
  },
  {
    id: 3,
    title: "Secure AI Moderation",
    description: "Built with Granite Guardian for robust security. Your data is protected with enterprise-grade encryption and privacy-first architecture.",
    icon: Shield,
    color: "accent",
    highlights: ["Granite Guardian", "Enterprise Security", "Privacy First"]
  },
  {
    id: 4,
    title: "Low-Bandwidth Optimized",
    description: "Designed for India's diverse connectivity landscape. Works seamlessly even on slow internet connections with progressive enhancement.",
    icon: Wifi,
    color: "muted",
    highlights: ["Offline Capable", "Progressive Enhancement", "Data Efficient"]
  },
  {
    id: 5,
    title: "UMANG Integration",
    description: "Direct connection to UMANG platform for seamless access to 2000+ government services from central and state governments.",
    icon: Link,
    color: "primary",
    highlights: ["2000+ Services", "Central & State Gov", "Real-time Access"]
  },
  {
    id: 6,
    title: "DigiLocker Connectivity",
    description: "Secure integration with DigiLocker for automatic document retrieval and verification, eliminating the need for physical paperwork.",
    icon: Database,
    color: "secondary",
    highlights: ["Document Retrieval", "Auto Verification", "Paperless Process"]
  }
];

const Features = () => {
  const getColorClasses = (color: string) => {
    switch (color) {
      case "primary":
        return "bg-primary text-white";
      case "secondary":
        return "bg-secondary text-white";
      case "accent":
        return "bg-accent text-accent-foreground";
      case "muted":
        return "bg-muted text-muted-foreground";
      default:
        return "bg-primary text-white";
    }
  };

  return (
    <section className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-6">
            Powerful Features
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Built with cutting-edge technology to provide seamless, secure, and intelligent access to government services for every citizen.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="card-feature group"
            >
              {/* Icon */}
              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-6 ${getColorClasses(feature.color)} group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="w-8 h-8" />
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-foreground mb-4">
                {feature.title}
              </h3>

              <p className="text-muted-foreground mb-6 leading-relaxed">
                {feature.description}
              </p>

              {/* Highlights */}
              <div className="space-y-2">
                {feature.highlights.map((highlight, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                    <span className="text-sm text-muted-foreground font-medium">
                      {highlight}
                    </span>
                  </div>
                ))}
              </div>

              {/* Hover Effect Gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-primary-light to-secondary-light rounded-2xl p-8 max-w-2xl mx-auto">
            <Brain className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-foreground mb-3">
              AI-Powered Government Services
            </h3>
            <p className="text-muted-foreground mb-6">
              Experience the future of citizen services with intelligent automation that understands your needs and simplifies complex processes.
            </p>
            <button className="btn-accent">
              Learn More
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Features;