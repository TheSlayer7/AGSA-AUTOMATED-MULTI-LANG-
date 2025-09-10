import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Calendar, MapPin, DollarSign, Shield, CheckCircle, XCircle, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const KYC = () => {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [integrationStatus, setIntegrationStatus] = useState<{
    digilocker: "idle" | "loading" | "success" | "error";
    aadhaar: "idle" | "loading" | "success" | "error";
    umang: "idle" | "loading" | "success" | "error";
  }>({
    digilocker: "idle",
    aadhaar: "idle",
    umang: "idle"
  });

  const navigate = useNavigate();
  const { toast } = useToast();

  const handleIntegration = async (service: keyof typeof integrationStatus) => {
    setIntegrationStatus(prev => ({ ...prev, [service]: "loading" }));
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Random success/failure for demo
    const success = Math.random() > 0.3;
    
    setIntegrationStatus(prev => ({ 
      ...prev, 
      [service]: success ? "success" : "error" 
    }));

    toast({
      title: success ? "Integration Successful!" : "Integration Failed",
      description: success 
        ? `Successfully connected to ${service.charAt(0).toUpperCase() + service.slice(1)}`
        : `Failed to connect to ${service.charAt(0).toUpperCase() + service.slice(1)}. Please try again.`,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    toast({
      title: "KYC Submitted Successfully!",
      description: "Your information has been verified. Proceeding to chat assistant.",
    });

    navigate("/chat");
    setIsLoading(false);
  };

  const incomeRanges = [
    "Below ₹2.5 Lakh",
    "₹2.5 - 5 Lakh",
    "₹5 - 10 Lakh",
    "₹10 - 25 Lakh",
    "₹25 - 50 Lakh",
    "Above ₹50 Lakh"
  ];

  const integrations = [
    {
      key: "digilocker" as const,
      name: "DigiLocker",
      description: "Access your digital documents securely",
      icon: Shield,
      color: "bg-blue-500"
    },
    {
      key: "aadhaar" as const,
      name: "Aadhaar",
      description: "Verify your identity with Aadhaar",
      icon: CheckCircle,
      color: "bg-green-500"
    },
    {
      key: "umang" as const,
      name: "UMANG",
      description: "Connect to government services",
      icon: ExternalLink,
      color: "bg-orange-500"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-subtle p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/auth")}
            className="text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          
          <div className="text-center">
            <h1 className="text-2xl font-display font-bold text-gray-900">
              Complete Your Profile
            </h1>
            <p className="text-gray-600 text-sm">
              Step {step} of 2 - KYC Verification
            </p>
          </div>
          
          <div className="w-16" /> {/* Spacer */}
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm text-gray-500">{step}/2</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-primary h-2 rounded-full"
              initial={{ width: "0%" }}
              animate={{ width: `${(step / 2) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {step === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="premium-card">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2 text-primary" />
                  Basic Information
                </CardTitle>
                <CardDescription>
                  Please provide your basic details for account verification
                </CardDescription>
              </CardHeader>

              <CardContent>
                <form onSubmit={(e) => { e.preventDefault(); setStep(2); }} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="firstName">First Name</Label>
                      <Input
                        id="firstName"
                        placeholder="Enter your first name"
                        required
                        className="floating-input"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="lastName">Last Name</Label>
                      <Input
                        id="lastName"
                        placeholder="Enter your last name"
                        required
                        className="floating-input"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth</Label>
                    <Input
                      id="dob"
                      type="date"
                      required
                      className="floating-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="address">Address</Label>
                    <Input
                      id="address"
                      placeholder="Enter your full address"
                      required
                      className="floating-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="income">Annual Income Range</Label>
                    <Select required>
                      <SelectTrigger className="floating-input">
                        <SelectValue placeholder="Select your income range" />
                      </SelectTrigger>
                      <SelectContent>
                        {incomeRanges.map((range) => (
                          <SelectItem key={range} value={range}>
                            {range}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button type="submit" className="w-full premium-button">
                    Continue
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            <Card className="premium-card">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-primary" />
                  Connect Your Accounts
                </CardTitle>
                <CardDescription>
                  Link your government accounts for seamless service access (Optional but recommended)
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                {integrations.map((integration) => {
                  const status = integrationStatus[integration.key];
                  const Icon = integration.icon;
                  
                  return (
                    <div
                      key={integration.key}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary/20 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${integration.color} text-white`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{integration.name}</h3>
                          <p className="text-sm text-gray-600">{integration.description}</p>
                        </div>
                      </div>

                      <Button
                        onClick={() => handleIntegration(integration.key)}
                        disabled={status === "loading" || status === "success"}
                        variant={status === "success" ? "secondary" : "outline"}
                        size="sm"
                        className="min-w-[100px]"
                      >
                        {status === "loading" && (
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-primary mr-2" />
                        )}
                        {status === "success" && <CheckCircle className="w-4 h-4 mr-2 text-green-600" />}
                        {status === "error" && <XCircle className="w-4 h-4 mr-2 text-red-600" />}
                        
                        {status === "idle" && "Connect"}
                        {status === "loading" && "Connecting..."}
                        {status === "success" && "Connected"}
                        {status === "error" && "Retry"}
                      </Button>
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            <div className="flex space-x-4">
              <Button
                variant="outline"
                onClick={() => setStep(1)}
                className="flex-1"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              
              <Button
                onClick={handleSubmit}
                disabled={isLoading}
                className="flex-1 premium-button"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    Completing...
                  </div>
                ) : (
                  <div className="flex items-center">
                    Complete Setup
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </div>
                )}
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default KYC;