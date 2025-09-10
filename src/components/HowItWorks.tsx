import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, MessageCircle, Search, FolderOpen, FileText, Mic, Globe, Lock, Zap } from "lucide-react";

const steps = [
  {
    id: 1,
    title: "Ask in Your Language",
    description: "Speak or type your query in any Indian language. Our AI understands context and helps you find the right government services.",
    icon: MessageCircle,
    features: ["Voice & Text Input", "22+ Indian Languages", "Natural Conversation"],
    visual: "typing"
  },
  {
    id: 2,
    title: "AI Finds Schemes",
    description: "Our intelligent agents search through thousands of government schemes and services to find exactly what you need.",
    icon: Search,
    features: ["Smart Discovery", "Personalized Results", "Real-time Updates"],
    visual: "cards"
  },
  {
    id: 3,
    title: "Fetches Documents",
    description: "Automatically retrieves your documents from DigiLocker and other government databases with your permission.",
    icon: FolderOpen,
    features: ["DigiLocker Integration", "Secure Access", "Automatic Retrieval"],
    visual: "documents"
  },
  {
    id: 4,
    title: "Prefills & Submits",
    description: "Forms are automatically filled with your information and submitted to the appropriate government departments.",
    icon: FileText,
    features: ["Auto Form Fill", "Secure Submission", "Application Tracking"],
    visual: "forms"
  }
];

const HowItWorks = () => {
  const [currentStep, setCurrentStep] = useState(0);

  const nextStep = () => {
    setCurrentStep((prev) => (prev + 1) % steps.length);
  };

  const prevStep = () => {
    setCurrentStep((prev) => (prev - 1 + steps.length) % steps.length);
  };

  const TypingAnimation = () => (
    <div className="bg-white/10 backdrop-blur rounded-2xl p-6 w-full max-w-md">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
          <Mic className="w-4 h-4 text-white" />
        </div>
        <span className="text-white/80 text-sm">You</span>
      </div>
      <div className="text-white text-left">
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          मुझे अपने बच्चे के लिए शिक्षा योजना चाहिए
        </motion.span>
        <motion.span
          animate={{ opacity: [0, 1, 0] }}
          transition={{ duration: 1, repeat: Infinity, delay: 1.5 }}
          className="inline-block w-1 h-4 bg-primary ml-1"
        />
      </div>
    </div>
  );

  const CardsAnimation = () => (
    <div className="space-y-3 w-full max-w-md">
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: i * 0.2 }}
          className="bg-white/10 backdrop-blur rounded-xl p-4 flex items-center gap-3"
        >
          <div className="w-10 h-10 bg-accent rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-accent-foreground" />
          </div>
          <div className="text-left">
            <div className="text-white font-medium text-sm">Education Scheme {i}</div>
            <div className="text-white/60 text-xs">90% Match</div>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const DocumentsAnimation = () => (
    <div className="relative w-full max-w-md">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-white/10 backdrop-blur rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Lock className="w-5 h-5 text-accent" />
          <span className="text-white text-sm">DigiLocker</span>
        </div>
        <div className="space-y-2">
          {["Aadhaar Card", "Birth Certificate", "Income Certificate"].map((doc, i) => (
            <motion.div
              key={doc}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 + i * 0.2 }}
              className="flex items-center gap-2 p-2 bg-white/5 rounded-lg"
            >
                      <div className="w-2 h-2 bg-primary rounded-full" />
                      <span className="text-white/80 text-xs">{doc}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const FormsAnimation = () => (
    <div className="bg-white/10 backdrop-blur rounded-2xl p-6 w-full max-w-md">
      <div className="text-white text-sm mb-4">Application Form</div>
      <div className="space-y-3">
        {["Name", "Address", "Documents"].map((field, i) => (
          <div key={field} className="space-y-1">
            <div className="text-white/60 text-xs">{field}</div>
            <div className="h-8 bg-white/5 rounded-lg relative overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ delay: i * 0.3, duration: 0.8 }}
                className="h-full bg-primary/30 rounded-lg"
              />
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.3 + 0.4 }}
                className="absolute inset-0 flex items-center px-3 text-xs text-white/80"
              >
                Auto-filled
              </motion.div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderVisual = (type: string) => {
    switch (type) {
      case "typing":
        return <TypingAnimation />;
      case "cards":
        return <CardsAnimation />;
      case "documents":
        return <DocumentsAnimation />;
      case "forms":
        return <FormsAnimation />;
      default:
        return null;
    }
  };

  return (
    <section className="py-20 bg-gradient-to-br from-background to-muted-light">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-6">
            How It Works
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Experience the future of government services with our AI-powered assistance that simplifies every step of your journey.
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          {/* Mobile Stepper */}
          <div className="md:hidden">
            <div className="bg-card rounded-2xl shadow-soft overflow-hidden">
              {/* Visual Area */}
              <div className="bg-gradient-hero p-8 flex items-center justify-center min-h-[300px]">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 0.3 }}
                  >
                    {renderVisual(steps[currentStep].visual)}
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Content Area */}
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center">
                    {(() => {
                      const Icon = steps[currentStep].icon;
                      return <Icon className="w-6 h-6 text-white" />;
                    })()}
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">
                      Step {currentStep + 1} of {steps.length}
                    </div>
                    <h3 className="text-xl font-bold text-foreground">
                      {steps[currentStep].title}
                    </h3>
                  </div>
                </div>

                <p className="text-muted-foreground mb-6 leading-relaxed">
                  {steps[currentStep].description}
                </p>

                <div className="space-y-2 mb-6">
                  {steps[currentStep].features.map((feature, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                      <span className="text-sm text-muted-foreground">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between">
                  <button
                    onClick={prevStep}
                    className="flex items-center gap-2 px-4 py-2 text-muted-foreground hover:text-primary transition-colors duration-200"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                  </button>

                  <div className="flex gap-2">
                    {steps.map((_, i) => (
                      <button
                        key={i}
                        onClick={() => setCurrentStep(i)}
                        className={`w-2 h-2 rounded-full transition-all duration-200 ${
                          i === currentStep ? "bg-primary w-6" : "bg-muted"
                        }`}
                      />
                    ))}
                  </div>

                  <button
                    onClick={nextStep}
                    className="flex items-center gap-2 px-4 py-2 text-muted-foreground hover:text-primary transition-colors duration-200"
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Desktop Grid */}
          <div className="hidden md:grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card-feature group"
              >
                <div className="flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                  <step.icon className="w-8 h-8 text-white" />
                </div>

                <h3 className="text-xl font-bold text-foreground mb-3">
                  {step.title}
                </h3>

                <p className="text-muted-foreground mb-4 leading-relaxed">
                  {step.description}
                </p>

                <div className="space-y-2">
                  {step.features.map((feature, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                      <span className="text-sm text-muted-foreground">{feature}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-6 text-right">
                  <span className="text-3xl font-bold text-primary/20">
                    0{index + 1}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;