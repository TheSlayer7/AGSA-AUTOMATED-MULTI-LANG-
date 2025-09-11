import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Calendar, MapPin, Building2, FileText, Users, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { schemesService } from '@/services/schemes';
import type { SchemeDetail } from '@/services/schemes';

const SchemeDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [scheme, setScheme] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    if (!slug) {
      navigate('/schemes');
      return;
    }

    const fetchScheme = async () => {
      try {
        setLoading(true);
        const data = await schemesService.getSchemeDetail(slug);
        setScheme(data);
      } catch (error) {
        console.error('Error fetching scheme:', error);
        toast({
          title: "Error",
          description: "Failed to load scheme details. Please try again.",
          variant: "destructive",
        });
        navigate('/schemes');
      } finally {
        setLoading(false);
      }
    };

    fetchScheme();
  }, [slug, navigate, toast]);

  const getCategoryColor = (category: string) => {
    const colors = {
      'AGRICULTURE': 'bg-green-100 text-green-800',
      'EDUCATION': 'bg-blue-100 text-blue-800',
      'HEALTH': 'bg-red-100 text-red-800',
      'EMPLOYMENT': 'bg-purple-100 text-purple-800',
      'SOCIAL_WELFARE': 'bg-pink-100 text-pink-800',
      'FINANCIAL': 'bg-yellow-100 text-yellow-800',
      'HOUSING': 'bg-indigo-100 text-indigo-800',
      'SKILL_DEVELOPMENT': 'bg-orange-100 text-orange-800',
      'WOMEN_EMPOWERMENT': 'bg-rose-100 text-rose-800',
      'INFRASTRUCTURE': 'bg-gray-100 text-gray-800',
      'OTHER': 'bg-gray-100 text-gray-800',
    };
    return colors[category.toUpperCase() as keyof typeof colors] || colors.OTHER;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Skeleton className="h-8 w-32 mb-6" />
          <Card>
            <CardHeader>
              <Skeleton className="h-8 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!scheme) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Button
          variant="outline"
          onClick={() => navigate('/schemes')}
          className="mb-6 flex items-center space-x-2"
        >
          <ArrowLeft size={16} />
          <span>Back to Schemes</span>
        </Button>

        {/* Scheme Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                  {scheme.scheme_name}
                </CardTitle>
                <CardDescription className="text-lg">
                  {scheme.ministry_department}
                </CardDescription>
              </div>
              <div className="flex flex-col space-y-2">
                <Badge 
                  className={`text-sm ${getCategoryColor(scheme.scheme_category)}`}
                  variant="secondary"
                >
                  {scheme.category_display || scheme.scheme_category}
                </Badge>
                <Badge 
                  variant={scheme.is_active ? "default" : "secondary"}
                  className="text-sm"
                >
                  {scheme.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>

            <div className="flex items-center space-x-6 mt-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <MapPin size={16} />
                <span>{scheme.level_display || scheme.level}</span>
              </div>
              {scheme.state && (
                <div className="flex items-center space-x-1">
                  <Building2 size={16} />
                  <span>{scheme.state}</span>
                </div>
              )}
              {scheme.launch_date && (
                <div className="flex items-center space-x-1">
                  <Calendar size={16} />
                  <span>Launched {new Date(scheme.launch_date).getFullYear()}</span>
                </div>
              )}
            </div>
          </CardHeader>
        </Card>

        {/* Scheme Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            {scheme.details && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Description</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {scheme.details}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Benefits */}
            {scheme.benefits && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <CheckCircle className="mr-2 text-green-600" size={20} />
                    Benefits
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {scheme.benefits}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Eligibility */}
            {scheme.eligibility && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <Users className="mr-2 text-blue-600" size={20} />
                    Eligibility Criteria
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {scheme.eligibility}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Application Process */}
            {scheme.application && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <FileText className="mr-2 text-purple-600" size={20} />
                    How to Apply
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {scheme.application}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-600">Scheme ID:</span>
                  <p className="text-sm text-gray-900">{scheme.scheme_id}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Level:</span>
                  <p className="text-sm text-gray-900">{scheme.level_display}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Category:</span>
                  <p className="text-sm text-gray-900">{scheme.category_display}</p>
                </div>
                {scheme.state && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">State:</span>
                    <p className="text-sm text-gray-900">{scheme.state}</p>
                  </div>
                )}
                <div>
                  <span className="text-sm font-medium text-gray-600">Documents:</span>
                  <p className="text-sm text-gray-900">{scheme.document_count} available</p>
                </div>
              </CardContent>
            </Card>

            {/* Required Documents */}
            {scheme.required_documents_list && scheme.required_documents_list.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Required Documents</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {scheme.required_documents_list.map((doc, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        {doc}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full">
                  <Users className="mr-2" size={16} />
                  Check Eligibility
                </Button>
                
                {scheme.website_url && (
                  <Button variant="outline" className="w-full" asChild>
                    <a
                      href={scheme.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center"
                    >
                      <ExternalLink className="mr-2" size={16} />
                      Official Website
                    </a>
                  </Button>
                )}
                
                <Button variant="outline" className="w-full">
                  <FileText className="mr-2" size={16} />
                  Download Forms
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemeDetail;
