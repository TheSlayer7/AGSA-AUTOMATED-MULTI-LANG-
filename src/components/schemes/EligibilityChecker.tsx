import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertCircle, Users, Calculator } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { schemesService } from '@/services/schemes';
import type { EligibilityCheck, EligibilityResponse } from '@/services/schemes';

interface EligibilityCheckerProps {
  onClose: () => void;
}

const EligibilityChecker: React.FC<EligibilityCheckerProps> = ({ onClose }) => {
  const navigate = useNavigate();
  const [criteria, setCriteria] = useState<EligibilityCheck>({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<EligibilityResponse | null>(null);
  const { toast } = useToast();

  const handleInputChange = (field: keyof EligibilityCheck, value: any) => {
    setCriteria(prev => ({
      ...prev,
      [field]: value === '' ? undefined : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (Object.keys(criteria).length === 0) {
      toast({
        title: "Please fill at least one field",
        description: "Enter some eligibility criteria to check schemes.",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const response = await schemesService.checkEligibility(criteria);
      setResults(response);
    } catch (error) {
      console.error('Error checking eligibility:', error);
      toast({
        title: "Error",
        description: "Failed to check eligibility. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setCriteria({});
    setResults(null);
  };

  const getEligibilityIcon = (status: string) => {
    switch (status) {
      case 'eligible':
        return <CheckCircle className="text-green-600" size={16} />;
      case 'not_eligible':
        return <XCircle className="text-red-600" size={16} />;
      case 'partially_eligible':
        return <AlertCircle className="text-orange-600" size={16} />;
      default:
        return <AlertCircle className="text-gray-600" size={16} />;
    }
  };

  const getEligibilityColor = (status: string) => {
    switch (status) {
      case 'eligible':
        return 'bg-green-100 text-green-800';
      case 'not_eligible':
        return 'bg-red-100 text-red-800';
      case 'partially_eligible':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center text-xl">
            <Users className="mr-2" size={24} />
            Eligibility Checker
          </DialogTitle>
          <DialogDescription>
            Enter your details to find schemes you're eligible for
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Eligibility Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Age */}
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  type="number"
                  placeholder="Enter your age"
                  value={criteria.age || ''}
                  onChange={(e) => handleInputChange('age', e.target.value ? parseInt(e.target.value) : undefined)}
                  min="0"
                  max="150"
                />
              </div>

              {/* Gender */}
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select
                  value={criteria.gender || ''}
                  onValueChange={(value) => handleInputChange('gender', value || undefined)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Not specified</SelectItem>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Annual Income */}
              <div className="space-y-2">
                <Label htmlFor="income">Annual Income (₹)</Label>
                <Input
                  id="income"
                  type="number"
                  placeholder="Enter annual income"
                  value={criteria.income || ''}
                  onChange={(e) => handleInputChange('income', e.target.value ? parseInt(e.target.value) : undefined)}
                  min="0"
                />
              </div>

              {/* State */}
              <div className="space-y-2">
                <Label htmlFor="state">State</Label>
                <Input
                  id="state"
                  placeholder="Enter your state"
                  value={criteria.state || ''}
                  onChange={(e) => handleInputChange('state', e.target.value)}
                />
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={criteria.category || ''}
                  onValueChange={(value) => handleInputChange('category', value || undefined)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Not specified</SelectItem>
                    <SelectItem value="general">General</SelectItem>
                    <SelectItem value="obc">OBC</SelectItem>
                    <SelectItem value="sc">SC</SelectItem>
                    <SelectItem value="st">ST</SelectItem>
                    <SelectItem value="ews">EWS</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Occupation */}
              <div className="space-y-2">
                <Label htmlFor="occupation">Occupation</Label>
                <Input
                  id="occupation"
                  placeholder="Enter your occupation"
                  value={criteria.occupation || ''}
                  onChange={(e) => handleInputChange('occupation', e.target.value)}
                />
              </div>

              {/* Education */}
              <div className="space-y-2">
                <Label htmlFor="education">Education Level</Label>
                <Input
                  id="education"
                  placeholder="Enter education level"
                  value={criteria.education || ''}
                  onChange={(e) => handleInputChange('education', e.target.value)}
                />
              </div>
            </div>

            {/* Rural/Urban */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="is_rural"
                checked={criteria.is_rural || false}
                onCheckedChange={(checked) => handleInputChange('is_rural', checked || undefined)}
              />
              <Label htmlFor="is_rural" className="cursor-pointer">
                I live in a rural area
              </Label>
            </div>

            {/* Submit Buttons */}
            <div className="flex justify-between pt-4">
              <Button type="button" variant="outline" onClick={clearForm}>
                Clear Form
              </Button>
              <div className="space-x-2">
                <Button type="button" variant="outline" onClick={onClose}>
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Calculator className="mr-2 animate-spin" size={16} />
                      Checking...
                    </>
                  ) : (
                    <>
                      <Calculator className="mr-2" size={16} />
                      Check Eligibility
                    </>
                  )}
                </Button>
              </div>
            </div>
          </form>

          {/* Results */}
          {results && (
            <div className="space-y-4 pt-6 border-t">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Eligibility Results</h3>
                <Badge variant="outline" className="text-sm">
                  {results.eligible_schemes?.length || 0} eligible schemes found
                </Badge>
              </div>

              {/* Summary */}
              {results.user_criteria && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Your Criteria</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries(results.user_criteria).map(([key, value]) => {
                        if (value === undefined || value === null) return null;
                        return (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                            <span className="font-medium">{value.toString()}</span>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Eligible Schemes */}
              {results.eligible_schemes && results.eligible_schemes.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-green-800">Eligible Schemes</h4>
                  <div className="grid gap-3">
                    {results.eligible_schemes.map((result, index) => (
                      <Card key={index} className="border-l-4 border-l-green-500">
                        <CardContent className="pt-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                {getEligibilityIcon('eligible')}
                                <h5 className="font-medium">{result.scheme.scheme_name}</h5>
                                <Badge className={getEligibilityColor('eligible')}>
                                  {result.eligible ? 'Eligible' : 'Not Eligible'}
                                </Badge>
                              </div>
                              {result.eligibility_text && (
                                <p className="text-sm text-gray-600 mb-2">{result.eligibility_text}</p>
                              )}
                              {result.matches && result.matches.length > 0 && (
                                <div className="text-xs text-gray-500 mb-2">
                                  <strong>Matches:</strong> {result.matches.join(', ')}
                                </div>
                              )}
                              {result.confidence !== undefined && (
                                <div className="text-xs text-gray-500">
                                  Confidence: {Math.round(result.confidence * 100)}%
                                </div>
                              )}
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                onClose();
                                navigate(`/schemes/${result.scheme.slug}`);
                              }}
                            >
                              View Details
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* No Results */}
              {(!results.eligible_schemes || results.eligible_schemes.length === 0) && (
                <Card>
                  <CardContent className="pt-6 text-center">
                    <div className="text-gray-500 mb-2">
                      <AlertCircle size={48} className="mx-auto mb-4 text-gray-400" />
                      <p>No schemes found matching your criteria.</p>
                      <p className="text-sm mt-2">
                        Try adjusting your criteria or check back later for new schemes.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EligibilityChecker;
