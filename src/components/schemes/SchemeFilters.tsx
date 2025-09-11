import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { X, Filter } from 'lucide-react';
import type { SchemeFilters, FilterOptions } from '@/services/schemes';

interface SchemeFiltersProps {
  filterOptions: FilterOptions;
  currentFilters: SchemeFilters;
  onFilterChange: (filters: SchemeFilters) => void;
  onClearFilters: () => void;
}

const SchemeFiltersComponent: React.FC<SchemeFiltersProps> = ({
  filterOptions,
  currentFilters,
  onFilterChange,
  onClearFilters,
}) => {
  const handleFilterUpdate = (key: keyof SchemeFilters, value: any) => {
    onFilterChange({
      ...currentFilters,
      [key]: value,
    });
  };

  const hasActiveFilters = Object.values(currentFilters).some(value => 
    value !== undefined && value !== null && value !== ''
  );

  return (
    <Card className="mb-6">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center">
            <Filter size={20} className="mr-2" />
            Filter Schemes
          </CardTitle>
          {hasActiveFilters && (
            <Button onClick={onClearFilters} variant="outline" size="sm">
              <X size={16} className="mr-1" />
              Clear All
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Level Filter */}
          <div className="space-y-2">
            <Label htmlFor="level">Level</Label>
            <Select
              value={currentFilters.level || ''}
              onValueChange={(value) => handleFilterUpdate('level', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All levels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All levels</SelectItem>
                {filterOptions.levels?.map((level) => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Category Filter */}
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select
              value={currentFilters.category || ''}
              onValueChange={(value) => handleFilterUpdate('category', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All categories</SelectItem>
                {filterOptions.categories?.map((category) => (
                  <SelectItem key={category.value} value={category.value}>
                    {category.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* State Filter */}
          <div className="space-y-2">
            <Label htmlFor="state">State</Label>
            <Select
              value={currentFilters.state || ''}
              onValueChange={(value) => handleFilterUpdate('state', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All states" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All states</SelectItem>
                {filterOptions.states?.map((state) => (
                  <SelectItem key={state.value} value={state.value}>
                    {state.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Active Status Filter */}
          <div className="space-y-2">
            <Label htmlFor="is_active">Status</Label>
            <Select
              value={currentFilters.is_active?.toString() || ''}
              onValueChange={(value) => 
                handleFilterUpdate('is_active', value === '' ? undefined : value === 'true')
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="All statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All statuses</SelectItem>
                <SelectItem value="true">Active only</SelectItem>
                <SelectItem value="false">Inactive only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Additional Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {/* Has Documents Filter */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="has_documents"
              checked={currentFilters.has_documents || false}
              onCheckedChange={(checked) => 
                handleFilterUpdate('has_documents', checked || undefined)
              }
            />
            <Label 
              htmlFor="has_documents" 
              className="text-sm font-normal cursor-pointer"
            >
              Has documents
            </Label>
          </div>

          {/* Ordering */}
          <div className="space-y-2">
            <Label htmlFor="ordering">Sort by</Label>
            <Select
              value={currentFilters.ordering || ''}
              onValueChange={(value) => handleFilterUpdate('ordering', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Default order" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Default order</SelectItem>
                <SelectItem value="scheme_name">Name (A-Z)</SelectItem>
                <SelectItem value="-scheme_name">Name (Z-A)</SelectItem>
                <SelectItem value="created_at">Oldest first</SelectItem>
                <SelectItem value="-created_at">Newest first</SelectItem>
                <SelectItem value="level">Level</SelectItem>
                <SelectItem value="scheme_category">Category</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Page Size */}
          <div className="space-y-2">
            <Label htmlFor="page_size">Results per page</Label>
            <Select
              value={currentFilters.page_size?.toString() || '10'}
              onValueChange={(value) => 
                handleFilterUpdate('page_size', value ? parseInt(value) : undefined)
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="10" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5 per page</SelectItem>
                <SelectItem value="10">10 per page</SelectItem>
                <SelectItem value="25">25 per page</SelectItem>
                <SelectItem value="50">50 per page</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="text-sm font-medium text-blue-900 mb-2">Active Filters:</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(currentFilters).map(([key, value]) => {
                if (value === undefined || value === null || value === '') return null;
                
                let displayValue = value.toString();
                if (key === 'is_active') {
                  displayValue = value ? 'Active' : 'Inactive';
                }
                
                return (
                  <div
                    key={key}
                    className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    <span className="font-medium">{key.replace('_', ' ')}:</span>
                    <span className="ml-1">{displayValue}</span>
                    <button
                      onClick={() => handleFilterUpdate(key as keyof SchemeFilters, undefined)}
                      className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
                    >
                      <X size={10} />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SchemeFiltersComponent;
