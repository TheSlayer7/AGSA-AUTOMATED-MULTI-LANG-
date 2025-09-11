import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Users, Calendar, MapPin, DollarSign, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { schemesService } from '@/services/schemes';
import type { Scheme, SchemeFilters, FilterOptions, SchemeStats } from '@/services/schemes';
import { SchemeCard, SchemeFilters as SchemeFiltersComponent, EligibilityChecker, StatsOverview } from '@/components/schemes';

const Schemes: React.FC = () => {
  const navigate = useNavigate();
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<SchemeFilters>({});
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [stats, setStats] = useState<SchemeStats | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [showEligibilityChecker, setShowEligibilityChecker] = useState(false);
  const { toast } = useToast();

  // Fetch schemes data
  const fetchSchemes = async () => {
    try {
      setLoading(true);
      const response = await schemesService.getSchemes({
        ...filters,
        search: searchTerm,
        page: currentPage,
      });
      setSchemes(response.results);
      setTotalPages(Math.ceil(response.count / 10)); // Assuming 10 per page
    } catch (error) {
      console.error('Error fetching schemes:', error);
      toast({
        title: "Error",
        description: "Failed to load schemes. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch filter options and stats
  const fetchMetadata = async () => {
    try {
      const [filterOpts, statsData] = await Promise.all([
        schemesService.getFilterOptions(),
        schemesService.getSchemeStats(),
      ]);
      setFilterOptions(filterOpts);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching metadata:', error);
    }
  };

  useEffect(() => {
    fetchMetadata();
  }, []);

  useEffect(() => {
    fetchSchemes();
  }, [searchTerm, filters, currentPage]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchSchemes();
  };

  const handleFilterChange = (newFilters: SchemeFilters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                onClick={() => navigate('/')}
                className="flex items-center space-x-2"
              >
                <Home size={16} />
                <span>Home</span>
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Government Schemes</h1>
                <p className="mt-1 text-gray-600">
                  Discover and explore government schemes tailored for you
                </p>
              </div>
            </div>
            <div className="mt-4 lg:mt-0 flex space-x-4">
              <Button
                variant="outline"
                onClick={() => setShowEligibilityChecker(true)}
                className="flex items-center space-x-2"
              >
                <Users size={16} />
                <span>Check Eligibility</span>
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2"
              >
                <Filter size={16} />
                <span>Filters</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        {stats && <StatsOverview stats={stats} />}

        {/* Search and Filters */}
        <div className="mb-8">
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <Input
                type="text"
                placeholder="Search schemes by name, description, or keywords..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-24 py-3 text-lg"
              />
              <Button
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2"
                size="sm"
              >
                Search
              </Button>
            </div>
          </form>

          {/* Filters Panel */}
          {showFilters && filterOptions && (
            <SchemeFiltersComponent
              filterOptions={filterOptions}
              currentFilters={filters}
              onFilterChange={handleFilterChange}
              onClearFilters={clearFilters}
            />
          )}
        </div>

        {/* Results Summary */}
        <div className="flex items-center justify-between mb-6">
          <div className="text-gray-600">
            {loading ? (
              "Loading schemes..."
            ) : (
              `Showing ${schemes.length} schemes`
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Sort by:</span>
            <Select
              onValueChange={(value) => 
                handleFilterChange({ ...filters, ordering: value })
              }
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Relevance" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="-created_at">Newest</SelectItem>
                <SelectItem value="created_at">Oldest</SelectItem>
                <SelectItem value="category">Category</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Schemes Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-20 bg-gray-200 rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : schemes.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {schemes.map((scheme) => (
                <SchemeCard key={scheme.scheme_id} scheme={scheme} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center mt-8">
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  <span className="text-sm text-gray-600">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">
              No schemes found matching your criteria.
            </div>
            <Button onClick={clearFilters} className="mt-4" variant="outline">
              Clear all filters
            </Button>
          </div>
        )}
      </div>

      {/* Eligibility Checker Modal */}
      {showEligibilityChecker && (
        <EligibilityChecker
          onClose={() => setShowEligibilityChecker(false)}
        />
      )}
    </div>
  );
};

export default Schemes;
