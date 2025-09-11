import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Users, MapPin, Building2, Activity, Calendar } from 'lucide-react';
import type { SchemeStats } from '@/services/schemes';

interface StatsOverviewProps {
  stats: SchemeStats;
}

const StatsOverview: React.FC<StatsOverviewProps> = ({ stats }) => {
  const statCards = [
    {
      title: 'Total Schemes',
      value: stats.total_schemes,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Active Schemes',
      value: stats.active_schemes,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Central Schemes',
      value: stats.central_schemes,
      icon: Building2,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'State Schemes',
      value: stats.state_schemes,
      icon: MapPin,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="mb-8">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stat.value?.toLocaleString() || 0}
                  </p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={stat.color} size={24} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Category Breakdown */}
      {stats.categories && stats.categories.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center">
              <Building2 className="mr-2" size={18} />
              Schemes by Category
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.categories
                .sort((a, b) => b.count - a.count)
                .slice(0, 6)
                .map((categoryItem, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">
                      {categoryItem.category_display}
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {categoryItem.count}
                    </Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default StatsOverview;
