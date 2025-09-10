import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Phone, ArrowLeft, Check, Loader2, UserPlus, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import agsaLogo from "@/assets/agsa-logo.jpg";

const Auth = () => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otp, setOtp] = useState("");
  const [requestId, setRequestId] = useState("");
  const [showOTP, setShowOTP] = useState(false);
  const [otpTimer, setOtpTimer] = useState(0);
  const [activeTab, setActiveTab] = useState("signin");
  const [isSignUp, setIsSignUp] = useState(false);
  
  // Sign-up specific states
  const [signUpData, setSignUpData] = useState({
    name: "",
    email: "",
    dateOfBirth: "",
    gender: "",
    address: ""
  });
  
  const navigate = useNavigate();
  const { toast } = useToast();
  const { login, verifyOTP, signUp, verifySignUpOTP, isLoading, isAuthenticated } = useAuth();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/chat");
    }
  }, [isAuthenticated, navigate]);

  // OTP timer countdown
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (otpTimer > 0) {
      interval = setInterval(() => {
        setOtpTimer((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [otpTimer]);

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!phoneNumber.trim()) {
      toast({
        title: "Error",
        description: "Please enter your phone number.",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await login(phoneNumber);
      setRequestId(response.request_id);
      setShowOTP(true);
      setOtpTimer(300); // 5 minutes countdown
      
      toast({
        title: "OTP Sent Successfully",
        description: response.message || "Please check your phone for the verification code.",
      });
    } catch (error) {
      console.error("Login error:", error);
      
      // Check if user needs to sign up
      if (error instanceof Error && error.message === 'SIGNUP_REQUIRED') {
        toast({
          title: "Account Not Found",
          description: "This phone number is not registered. Please sign up to create an account.",
          variant: "destructive",
        });
        // Automatically switch to sign up tab
        setActiveTab('signup');
        return;
      }
      
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send OTP. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSignUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!phoneNumber.trim() || !signUpData.name.trim() || !signUpData.dateOfBirth || !signUpData.gender) {
      toast({
        title: "Error",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await signUp({
        phone_number: phoneNumber,
        name: signUpData.name,
        email: signUpData.email,
        date_of_birth: signUpData.dateOfBirth,
        gender: signUpData.gender as 'M' | 'F' | 'O',
        address: signUpData.address
      });
      
      setRequestId(response.request_id);
      setShowOTP(true);
      setOtpTimer(300); // 5 minutes
      setIsSignUp(true);
      
      toast({
        title: "Registration Initiated",
        description: "Please check your phone for the verification code to complete registration.",
      });
    } catch (error) {
      console.error("Sign up error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to initiate registration. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp.trim() || otp.length !== 6) {
      toast({
        title: "Error",
        description: "Please enter a valid 6-digit OTP.",
        variant: "destructive",
      });
      return;
    }

    try {
      if (isSignUp) {
        await verifySignUpOTP(requestId, otp);
        toast({
          title: "Registration Successful!",
          description: "Welcome to AGSA. Your account has been created successfully.",
        });
      } else {
        await verifyOTP(requestId, otp);
        toast({
          title: "Login Successful!",
          description: "Welcome to AGSA. Redirecting to your dashboard...",
        });
      }

      // Navigate to KYC or Chat based on user profile completeness
      navigate("/kyc");
    } catch (error) {
      console.error("OTP verification error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Invalid OTP. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleResendOTP = async () => {
    if (otpTimer > 0) return;
    
    try {
      if (isSignUp) {
        const response = await signUp({
          phone_number: phoneNumber,
          name: signUpData.name,
          email: signUpData.email,
          date_of_birth: signUpData.dateOfBirth,
          gender: signUpData.gender as 'M' | 'F' | 'O',
          address: signUpData.address
        });
        setRequestId(response.request_id);
      } else {
        const response = await login(phoneNumber);
        setRequestId(response.request_id);
      }
      
      setOtpTimer(300);
      setOtp("");
      
      toast({
        title: "OTP Resent",
        description: "A new OTP has been sent to your phone.",
      });
    } catch (error) {
      console.error("Resend OTP error:", error);
      toast({
        title: "Error",
        description: "Failed to resend OTP. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleBackToPhone = () => {
    setShowOTP(false);
    setOtp("");
    setRequestId("");
    setOtpTimer(0);
    setIsSignUp(false);
  };

  const formatPhoneNumber = (value: string) => {
    // Remove all non-numeric characters
    const cleaned = value.replace(/\D/g, "");
    
    // Handle different input patterns
    if (cleaned.length <= 10) {
      // Format as Indian mobile number
      const match = cleaned.match(/^(\d{0,5})(\d{0,5})$/);
      if (match) {
        const formatted = [match[1], match[2]].filter(Boolean).join(" ");
        return formatted;
      }
    }
    
    return cleaned;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const formatted = formatPhoneNumber(value);
    setPhoneNumber(formatted);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
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
              {showOTP ? (isSignUp ? "Complete Registration" : "Verify Phone Number") : "Welcome to AGSA"}
            </CardTitle>
            <CardDescription>
              {showOTP 
                ? "Enter the 6-digit code sent to your phone" 
                : "Sign in to your account or create a new one"}
            </CardDescription>
          </CardHeader>

          <CardContent>
            {!showOTP ? (
              // Sign In / Sign Up Tabs
              <Tabs defaultValue="signin" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="signin" className="flex items-center gap-2">
                    <LogIn className="w-4 h-4" />
                    Sign In
                  </TabsTrigger>
                  <TabsTrigger value="signup" className="flex items-center gap-2">
                    <UserPlus className="w-4 h-4" />
                    Sign Up
                  </TabsTrigger>
                </TabsList>

                {/* Sign In Tab */}
                <TabsContent value="signin" className="mt-6">
                  <form onSubmit={handlePhoneSubmit} className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number</Label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <span className="text-gray-500 text-sm">+91</span>
                        </div>
                        <Input
                          id="phone"
                          type="tel"
                          placeholder="98765 43210"
                          value={phoneNumber}
                          onChange={handlePhoneChange}
                          required
                          maxLength={11}
                          className="floating-input pl-12"
                          disabled={isLoading}
                        />
                        <Phone className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      </div>
                      <p className="text-xs text-gray-500">
                        Enter your 10-digit Indian mobile number
                      </p>
                    </div>

                    <Button
                      type="submit"
                      className="w-full"
                      disabled={isLoading || !phoneNumber.trim()}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Sending OTP...
                        </>
                      ) : (
                        <>
                          <Phone className="w-4 h-4 mr-2" />
                          Send OTP
                        </>
                      )}
                    </Button>
                  </form>
                </TabsContent>

                {/* Sign Up Tab */}
                <TabsContent value="signup" className="mt-6">
                  <form onSubmit={handleSignUpSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="signup-phone">Phone Number</Label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <span className="text-gray-500 text-sm">+91</span>
                        </div>
                        <Input
                          id="signup-phone"
                          type="tel"
                          placeholder="98765 43210"
                          value={phoneNumber}
                          onChange={handlePhoneChange}
                          required
                          maxLength={11}
                          className="floating-input pl-12"
                          disabled={isLoading}
                        />
                        <Phone className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name *</Label>
                      <Input
                        id="name"
                        type="text"
                        placeholder="Enter your full name"
                        value={signUpData.name}
                        onChange={(e) => setSignUpData(prev => ({ ...prev, name: e.target.value }))}
                        required
                        className="floating-input"
                        disabled={isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email (Optional)</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email address"
                        value={signUpData.email}
                        onChange={(e) => setSignUpData(prev => ({ ...prev, email: e.target.value }))}
                        className="floating-input"
                        disabled={isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="dob">Date of Birth *</Label>
                      <Input
                        id="dob"
                        type="date"
                        value={signUpData.dateOfBirth}
                        onChange={(e) => setSignUpData(prev => ({ ...prev, dateOfBirth: e.target.value }))}
                        required
                        className="floating-input"
                        disabled={isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="gender">Gender *</Label>
                      <select
                        id="gender"
                        value={signUpData.gender}
                        onChange={(e) => setSignUpData(prev => ({ ...prev, gender: e.target.value }))}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:opacity-50"
                        disabled={isLoading}
                      >
                        <option value="">Select Gender</option>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                        <option value="O">Other</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="address">Address *</Label>
                      <Input
                        id="address"
                        type="text"
                        placeholder="Enter your address"
                        value={signUpData.address}
                        onChange={(e) => setSignUpData(prev => ({ ...prev, address: e.target.value }))}
                        required
                        className="floating-input"
                        disabled={isLoading}
                      />
                    </div>

                    <Button
                      type="submit"
                      className="w-full"
                      disabled={isLoading || !phoneNumber.trim() || !signUpData.name.trim() || !signUpData.dateOfBirth || !signUpData.gender || !signUpData.address.trim()}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Creating Account...
                        </>
                      ) : (
                        <>
                          <UserPlus className="w-4 h-4 mr-2" />
                          Create Account
                        </>
                      )}
                    </Button>
                  </form>
                </TabsContent>
              </Tabs>
            ) : (
              // OTP Verification Form
              <form onSubmit={handleOTPSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="otp">Enter OTP</Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="123456"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    maxLength={6}
                    required
                    className="floating-input text-center text-lg tracking-wider"
                    disabled={isLoading}
                    autoComplete="one-time-code"
                  />
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>Code sent to +91 {phoneNumber}</span>
                    {otpTimer > 0 ? (
                      <span className="text-primary font-medium">
                        Resend in {formatTime(otpTimer)}
                      </span>
                    ) : (
                      <Button
                        type="button"
                        variant="link"
                        size="sm"
                        onClick={handleResendOTP}
                        disabled={isLoading}
                        className="h-auto p-0 text-xs"
                      >
                        Resend OTP
                      </Button>
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isLoading || otp.length !== 6}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        <Check className="w-4 h-4 mr-2" />
                        Verify & Continue
                      </>
                    )}
                  </Button>

                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleBackToPhone}
                    className="w-full"
                    disabled={isLoading}
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Change Phone Number
                  </Button>
                </div>
              </form>
            )}

            {/* Security Notice */}
            <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-xs text-blue-700 text-center">
                🔒 Your phone number is encrypted and secure. We'll never share it with third parties.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Help Section */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Having trouble? Contact support at{" "}
            <a href="mailto:support@agsa.gov.in" className="text-primary hover:underline">
              support@agsa.gov.in
            </a>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default Auth;