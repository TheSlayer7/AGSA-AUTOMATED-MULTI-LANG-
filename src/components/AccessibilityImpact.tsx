import { motion } from "framer-motion";
import { Wifi, TrendingDown, Globe, Users, MapPin, Smartphone, BarChart3, Heart } from "lucide-react";

const stats = [
  {
    id: 1,
    value: "37%",
    label: "Villages with Broadband",
    description: "Rural connectivity still a challenge",
    icon: Wifi,
    color: "text-muted"
  },
  {
    id: 2,
    value: "60%",
    label: "Scheme Drop-off Rate",
    description: "Citizens abandon applications due to complexity",
    icon: TrendingDown,
    color: "text-destructive"
  },
  {
    id: 3,
    value: "88%",
    label: "Regional Language Demand",
    description: "Prefer services in their native language",
    icon: Globe,
    color: "text-primary"
  }
];

const impacts = [
  {
    id: 1,
    title: "Bridging the Digital Divide",
    description: "Making government services accessible to citizens regardless of their technical expertise or internet connectivity.",
    icon: Smartphone,
    metric: "2x faster access"
  },
  {
    id: 2,
    title: "Language Inclusivity",
    description: "Breaking down language barriers with support for 22+ Indian languages, ensuring no citizen is left behind.",
    icon: Globe,
    metric: "22+ languages"
  },
  {
    id: 3,
    title: "Simplified User Experience",
    description: "Reducing complex government processes to simple conversations, increasing completion rates dramatically.",
    icon: Users,
    metric: "80% less complexity"
  },
  {
    id: 4,
    title: "Rural Accessibility",
    description: "Optimized for low-bandwidth environments, bringing services to the remotest corners of India.",
    icon: MapPin,
    metric: "Works on 2G"
  }
];

const AccessibilityImpact = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-muted-light to-background">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-6">
            Accessibility & Impact
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Understanding the challenges and creating solutions that truly serve every citizen of India.
          </p>
        </motion.div>

        {/* Statistics */}
        <div className="grid md:grid-cols-3 gap-8 mb-20 max-w-4xl mx-auto">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="text-center group"
            >
              <div className="bg-card rounded-2xl p-8 shadow-soft hover:shadow-medium transition-all duration-300 hover:translate-y-[-2px]">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-muted-light rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                  <stat.icon className={`w-8 h-8 ${stat.color}`} />
                </div>
                
                <div className="text-4xl md:text-5xl font-bold text-foreground mb-2">
                  {stat.value}
                </div>
                
                <div className="text-lg font-semibold text-foreground mb-2">
                  {stat.label}
                </div>
                
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {stat.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Impact Areas */}
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {impacts.map((impact, index) => (
            <motion.div
              key={impact.id}
              initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="flex gap-6 p-6 bg-card rounded-2xl shadow-soft hover:shadow-medium transition-all duration-300 hover:translate-y-[-2px] group"
            >
              <div className="flex-shrink-0">
                <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <impact.icon className="w-8 h-8 text-white" />
                </div>
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xl font-bold text-foreground">
                    {impact.title}
                  </h3>
                  <span className="text-sm font-semibold text-primary bg-primary-light px-3 py-1 rounded-full">
                    {impact.metric}
                  </span>
                </div>
                
                <p className="text-muted-foreground leading-relaxed">
                  {impact.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-primary to-secondary rounded-2xl p-8 md:p-12 text-white max-w-4xl mx-auto">
            <Heart className="w-12 h-12 mx-auto mb-6 text-white/80" />
            <h3 className="text-3xl md:text-4xl font-serif font-bold mb-4">
              Building an Inclusive Digital India
            </h3>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto leading-relaxed">
              Every citizen deserves equal access to government services. AGSA is committed to creating a barrier-free experience for all.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-primary font-semibold px-8 py-3 rounded-xl hover:bg-white/90 transition-colors duration-200">
                Join the Movement
              </button>
              <button className="border-2 border-white/30 text-white font-semibold px-8 py-3 rounded-xl hover:bg-white/10 transition-colors duration-200">
                Learn More
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default AccessibilityImpact;