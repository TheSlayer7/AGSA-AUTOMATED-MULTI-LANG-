import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import Features from "@/components/Features";
import AccessibilityImpact from "@/components/AccessibilityImpact";
import Demo from "@/components/Demo";
import CallToAction from "@/components/CallToAction";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div id="home">
        <Hero />
      </div>
      <div id="how-it-works">
        <HowItWorks />
      </div>
      <div id="features">
        <Features />
      </div>
      <div id="impact">
        <AccessibilityImpact />
      </div>
      <div id="demo">
        <Demo />
      </div>
      <CallToAction />
      <Footer />
    </div>
  );
};

export default Index;
