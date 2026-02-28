import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MapPin, Calendar, Users, FileText } from 'lucide-react';
import type { Scheme } from '@/services/schemes';

interface SchemeCardProps {
  scheme: Scheme;
}

const SchemeCard: React.FC<SchemeCardProps> = ({ scheme }) => {
  const navigate = useNavigate();

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

  const getLevelColor = (level: string) => {
    const colors = {
      'central': 'bg-blue-50 text-blue-700 border-blue-200',
      'state': 'bg-green-50 text-green-700 border-green-200',
      'district': 'bg-purple-50 text-purple-700 border-purple-200',
      'block': 'bg-orange-50 text-orange-700 border-orange-200',
      'panchayat': 'bg-yellow-50 text-yellow-700 border-yellow-200',
    };
    return colors[level as keyof typeof colors] || colors.block;
  };

  const handleViewDetails = () => {
    navigate(`/schemes/${scheme.slug}`);
  };

  const handleCheckEligibility = () => {
    // This will be handled by parent component or context
    console.log('Check eligibility for:', scheme.scheme_name);
  };

  return (
    <Card className="h-full hover:shadow-lg transition-shadow duration-200 border-l-4 border-l-blue-500">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold line-clamp-2 text-gray-900">
              {scheme.scheme_name}
            </CardTitle>
            <CardDescription className="mt-1 text-sm text-gray-600">
              {scheme.state || 'National Scheme'}
            </CardDescription>
          </div>
          <Badge 
            className={`ml-2 text-xs ${getCategoryColor(scheme.scheme_category)}`}
            variant="secondary"
          >
            {scheme.category_display || scheme.scheme_category}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-3 mt-2">
          <Badge 
            variant="outline" 
            className={`text-xs ${getLevelColor(scheme.level)}`}
          >
            <MapPin size={10} className="mr-1" />
            {scheme.level_display || scheme.level}
          </Badge>
          <div className="flex items-center text-xs text-gray-500">
            <Calendar size={10} className="mr-1" />
            {new Date(scheme.created_at).toLocaleDateString()}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
            <span>ID: {scheme.scheme_id}</span>
            <span className={`px-2 py-1 rounded-full ${scheme.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {scheme.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>

        {scheme.document_count > 0 && (
          <div className="mb-4">
            <div className="flex items-center text-xs text-gray-600">
              <FileText size={10} className="mr-1" />
              {scheme.document_count} document{scheme.document_count !== 1 ? 's' : ''} available
            </div>
          </div>
        )}

        <div className="flex flex-col space-y-2 mt-4">
          <Button
            onClick={handleViewDetails}
            className="w-full text-sm"
            size="sm"
          >
            <FileText size={14} className="mr-2" />
            View Details
          </Button>
          
          <Button
            onClick={handleCheckEligibility}
            variant="outline"
            className="w-full text-sm"
            size="sm"
          >
            <Users size={14} className="mr-2" />
            Check Eligibility
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default SchemeCard;
