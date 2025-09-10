import { useState } from "react";
import { motion } from "framer-motion";
import { Phone, Mail, ArrowLeft, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import agsaLogo from "@/assets/agsa-logo.jpg";

const Auth = () => {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [method, setMethod] = useState<"phone" | "email">("phone");
  const [isLoading, setIsLoading] = useState(false);
  const [showOTP, setShowOTP] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    if (method === "phone" && !showOTP) {
      setShowOTP(true);
      toast({
        title: "OTP Sent",
        description: "Please check your phone for the verification code.",
      });
    } else {
      toast({
        title: "Success!",
        description: mode === "login" ? "Welcome back!" : "Account created successfully!",
      });
      navigate("/kyc");
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-subtle flex items-center justify-center p-4">
      <motion.div
        className="w-full max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="mb-6 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          
          <motion.div
            className="flex justify-center mb-4"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <img src={agsaLogo} alt="AGSA" className="h-16 w-16 rounded-full shadow-lg" />
          </motion.div>
          
          <h1 className="text-2xl font-display font-bold text-gray-900 mb-2">
            Welcome to AGSA
          </h1>
          <p className="text-gray-600 text-sm">
            Your Agentic AI for Government Services
          </p>
        </div>

        {/* Auth Card */}
        <Card className="premium-card">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">
              {mode === "login" ? "Sign In" : "Create Account"}
            </CardTitle>
            <CardDescription>
              {mode === "login" 
                ? "Welcome back! Please sign in to continue." 
                : "Get started with your AGSA account today."}
            </CardDescription>
          </CardHeader>

          <CardContent>
            {/* Mode Toggle */}
            <div className="flex mb-6 p-1 bg-gray-100 rounded-lg">
              <button
                onClick={() => setMode("login")}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                  mode === "login"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setMode("register")}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                  mode === "register"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Register
              </button>
            </div>

            {/* Method Toggle */}
            <div className="flex mb-6 p-1 bg-gray-50 rounded-lg">
              <button
                onClick={() => setMethod("phone")}
                className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all flex items-center justify-center ${
                  method === "phone"
                    ? "bg-primary text-white shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Phone className="w-4 h-4 mr-2" />
                Phone
              </button>
              <button
                onClick={() => setMethod("email")}
                className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all flex items-center justify-center ${
                  method === "email"
                    ? "bg-primary text-white shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Mail className="w-4 h-4 mr-2" />
                Email
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {method === "phone" ? (
                <>
                  {!showOTP ? (
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="+91 98765 43210"
                        required
                        className="floating-input"
                      />
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Label htmlFor="otp">Enter OTP</Label>
                      <Input
                        id="otp"
                        type="text"
                        placeholder="Enter 6-digit code"
                        maxLength={6}
                        required
                        className="floating-input text-center text-lg tracking-wider"
                      />
                      <p className="text-xs text-gray-500 text-center">
                        Code sent to your phone number
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      required
                      className="floating-input"
                    />
                  </div>
                  
                  {mode === "register" && (
                    <div className="space-y-2">
                      <Label htmlFor="phone-reg">Phone Number</Label>
                      <Input
                        id="phone-reg"
                        type="tel"
                        placeholder="+91 98765 43210"
                        required
                        className="floating-input"
                      />
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter your password"
                      required
                      className="floating-input"
                    />
                  </div>
                </>
              )}

              <Button
                type="submit"
                className="w-full premium-button"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    {method === "phone" && !showOTP ? "Sending OTP..." : "Verifying..."}
                  </div>
                ) : (
                  <div className="flex items-center">
                    {method === "phone" && !showOTP ? "Send OTP" : "Continue"}
                    <Check className="w-4 h-4 ml-2" />
                  </div>
                )}
              </Button>
            </form>

            {/* Footer Links */}
            <div className="mt-6 text-center text-sm text-gray-600">
              {mode === "login" ? (
                <p>
                  Don't have an account?{" "}
                  <button
                    onClick={() => setMode("register")}
                    className="text-primary hover:underline font-medium"
                  >
                    Sign up
                  </button>
                </p>
              ) : (
                <p>
                  Already have an account?{" "}
                  <button
                    onClick={() => setMode("login")}
                    className="text-primary hover:underline font-medium"
                  >
                    Sign in
                  </button>
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Auth;