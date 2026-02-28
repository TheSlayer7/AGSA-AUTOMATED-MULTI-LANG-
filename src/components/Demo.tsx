import { useState } from "react";
import { motion } from "framer-motion";
import { Play, Pause, Volume2, VolumeX, Maximize, Subtitles } from "lucide-react";

const Demo = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [showCaptions, setShowCaptions] = useState(false);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleCaptions = () => {
    setShowCaptions(!showCaptions);
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
            See AGSA in Action
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Watch how AGSA transforms the government service experience with intelligent automation and multilingual support.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          {/* Video Container */}
          <div className="relative bg-card rounded-2xl shadow-large overflow-hidden group">
            {/* Video Placeholder */}
            <div className="relative bg-gradient-to-br from-primary to-secondary aspect-video flex items-center justify-center">
              {/* Placeholder Content */}
              <div className="text-center text-white">
                <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  {isPlaying ? (
                    <Pause className="w-12 h-12" />
                  ) : (
                    <Play className="w-12 h-12 ml-1" />
                  )}
                </div>
                <h3 className="text-2xl font-bold mb-2">AGSA Demo Video</h3>
                <p className="text-white/80">See how citizens interact with government services</p>
              </div>

              {/* Play Button Overlay */}
              <button
                onClick={togglePlay}
                className="absolute inset-0 bg-black/20 hover:bg-black/30 transition-colors duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100"
              >
                <div className="w-20 h-20 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors duration-200">
                  {isPlaying ? (
                    <Pause className="w-8 h-8 text-primary" />
                  ) : (
                    <Play className="w-8 h-8 text-primary ml-1" />
                  )}
                </div>
              </button>

              {/* Captions Overlay */}
              {showCaptions && (
                <div className="absolute bottom-4 left-4 right-4 bg-black/80 backdrop-blur rounded-lg p-3">
                  <p className="text-white text-sm text-center">
                    "मुझे अपने बच्चे के लिए शिक्षा योजना चाहिए" - User asks for education scheme in Hindi
                  </p>
                </div>
              )}
            </div>

            {/* Video Controls */}
            <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={togglePlay}
                  className="w-10 h-10 bg-white/90 hover:bg-white rounded-full flex items-center justify-center transition-colors duration-200"
                >
                  {isPlaying ? (
                    <Pause className="w-5 h-5 text-primary" />
                  ) : (
                    <Play className="w-5 h-5 text-primary ml-0.5" />
                  )}
                </button>

                <button
                  onClick={toggleMute}
                  className="w-10 h-10 bg-white/90 hover:bg-white rounded-full flex items-center justify-center transition-colors duration-200"
                >
                  {isMuted ? (
                    <VolumeX className="w-5 h-5 text-primary" />
                  ) : (
                    <Volume2 className="w-5 h-5 text-primary" />
                  )}
                </button>

                <button
                  onClick={toggleCaptions}
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors duration-200 ${
                    showCaptions 
                      ? "bg-primary text-white" 
                      : "bg-white/90 hover:bg-white text-primary"
                  }`}
                >
                  <Subtitles className="w-5 h-5" />
                </button>
              </div>

              <button className="w-10 h-10 bg-white/90 hover:bg-white rounded-full flex items-center justify-center transition-colors duration-200">
                <Maximize className="w-5 h-5 text-primary" />
              </button>
            </div>
          </div>

          {/* Video Info */}
          <div className="mt-8 grid md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-card rounded-xl shadow-soft">
              <div className="w-12 h-12 bg-primary-light rounded-xl flex items-center justify-center mx-auto mb-4">
                <Play className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-bold text-foreground mb-2">Interactive Demo</h3>
              <p className="text-sm text-muted-foreground">
                Real user scenarios showing AGSA's capabilities
              </p>
            </div>

            <div className="text-center p-6 bg-card rounded-xl shadow-soft">
              <div className="w-12 h-12 bg-secondary-light rounded-xl flex items-center justify-center mx-auto mb-4">
                <Subtitles className="w-6 h-6 text-secondary" />
              </div>
              <h3 className="font-bold text-foreground mb-2">Multilingual</h3>
              <p className="text-sm text-muted-foreground">
                Available with subtitles in multiple languages
              </p>
            </div>

            <div className="text-center p-6 bg-card rounded-xl shadow-soft">
              <div className="w-12 h-12 bg-accent-light rounded-xl flex items-center justify-center mx-auto mb-4">
                <Volume2 className="w-6 h-6 text-accent-foreground" />
              </div>
              <h3 className="font-bold text-foreground mb-2">Voice Enabled</h3>
              <p className="text-sm text-muted-foreground">
                Demonstrates voice interaction capabilities
              </p>
            </div>
          </div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="text-center mt-12"
          >
            <button className="btn-hero">
              Try AGSA Now
            </button>
            <p className="text-muted-foreground text-sm mt-4">
              Experience the future of government services today
            </p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default Demo;