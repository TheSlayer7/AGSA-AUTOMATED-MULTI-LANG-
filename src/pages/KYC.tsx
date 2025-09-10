import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  ArrowRight, 
  User, 
  Phone, 
  Mail, 
  Calendar, 
  MapPin, 
  Shield, 
  FileText, 
  Upload, 
  Download, 
  CheckCircle, 
  Loader2 
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useAuth } from '../contexts/AuthContext';
import { documentService, DocumentListItem, DocumentType } from '../services/documents';
import { useToast } from '../hooks/use-toast';

const KYC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { toast } = useToast();
  
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  
  // Upload form state
  const [newDocumentType, setNewDocumentType] = useState('');
  const [newDocumentNumber, setNewDocumentNumber] = useState('');
  const [newDocumentIssueDate, setNewDocumentIssueDate] = useState('');
  const [newDocumentExpiryDate, setNewDocumentExpiryDate] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadingDocument, setUploadingDocument] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    
    loadData();
  }, [user, navigate]);

  const loadData = async () => {
    try {
      setLoadingDocuments(true);
      const [docsResponse, typesResponse] = await Promise.all([
        documentService.getUserDocuments(),
        documentService.getDocumentTypes()
      ]);
      
      setDocuments(docsResponse.data || []);
      setDocumentTypes(typesResponse.data || []);
    } catch (error) {
      console.error('Error loading data:', error);
      toast({
        title: "Error",
        description: "Failed to load documents and types",
        variant: "destructive",
      });
    } finally {
      setLoadingDocuments(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please select a file smaller than 10MB",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
  };

  const handleDocumentUpload = async () => {
    if (!selectedFile || !newDocumentType || !newDocumentNumber || !newDocumentIssueDate) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields and select a file",
        variant: "destructive",
      });
      return;
    }

    try {
      setUploadingDocument(true);
      
      const request = {
        document_type_id: parseInt(newDocumentType),
        doc_number: newDocumentNumber,
        issue_date: newDocumentIssueDate,
        expiry_date: newDocumentExpiryDate || undefined,
        file: selectedFile,
      };

      await documentService.uploadDocument(request);
      
      toast({
        title: "Success",
        description: "Document uploaded successfully",
      });

      // Reset form
      setSelectedFile(null);
      setNewDocumentType('');
      setNewDocumentNumber('');
      setNewDocumentIssueDate('');
      setNewDocumentExpiryDate('');
      
      // Reload documents
      loadData();
      
    } catch (error) {
      console.error('Error uploading document:', error);
      toast({
        title: "Upload failed",
        description: "Failed to upload document. Please try again.",
        variant: "destructive",
      });
    } finally {
      setUploadingDocument(false);
    }
  };

  const handleDocumentDownload = async (docId: string, filename: string) => {
    try {
      const documentData = await documentService.downloadDocument(docId);
      
      let blob: Blob;
      
      // Handle different content formats
      if (documentData.content) {
        try {
          // Try to decode as base64
          const byteCharacters = atob(documentData.content);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          blob = new Blob([byteArray], { type: documentData.mime_type });
        } catch (base64Error) {
          // If base64 fails, treat as text content
          blob = new Blob([documentData.content], { type: documentData.mime_type || 'text/plain' });
        }
      } else {
        // Create empty blob if no content
        blob = new Blob([''], { type: 'text/plain' });
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = documentData.filename || filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Success",
        description: "Document downloaded successfully",
      });
    } catch (error) {
      console.error('Error downloading document:', error);
      toast({
        title: "Download failed",
        description: "Failed to download document. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="w-full min-h-screen">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200/50 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between h-16 sm:h-20">
              <Button
                variant="ghost"
                onClick={() => navigate("/auth")}
                className="text-gray-600 hover:text-gray-900 flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="hidden sm:inline">Back</span>
              </Button>
              
              <div className="text-center flex-1 mx-4">
                <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">
                  Profile & Documents
                </h1>
                <p className="text-gray-600 text-xs sm:text-sm hidden sm:block">
                  Manage your information and documents
                </p>
              </div>
              
              <Button
                variant="outline"
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900 text-sm"
              >
                <span className="hidden sm:inline">Logout</span>
                <span className="sm:hidden">Exit</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 lg:gap-8">
            {/* User Profile Card - Responsive width */}
            <div className="xl:col-span-1">
              <Card className="h-fit sticky top-24 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center text-lg">
                    <User className="w-5 h-5 mr-2 text-blue-600" />
                    Your Profile
                  </CardTitle>
                  <CardDescription className="text-sm">
                    DigiLocker account information
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {user && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Name</Label>
                        <p className="font-semibold text-gray-900">{user.name}</p>
                      </div>
                      
                      <div className="space-y-2">
                        <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Phone</Label>
                        <p className="font-medium flex items-center text-gray-700">
                          <Phone className="w-4 h-4 mr-2 text-blue-500" />
                          {user.phone_number}
                        </p>
                      </div>
                      
                      {user.email && (
                        <div className="space-y-2">
                          <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Email</Label>
                          <p className="font-medium flex items-center text-gray-700 break-all">
                            <Mail className="w-4 h-4 mr-2 text-blue-500 flex-shrink-0" />
                            <span className="text-sm">{user.email}</span>
                          </p>
                        </div>
                      )}
                      
                      <div className="space-y-2">
                        <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Date of Birth</Label>
                        <p className="font-medium flex items-center text-gray-700">
                          <Calendar className="w-4 h-4 mr-2 text-blue-500" />
                          {new Date(user.dob).toLocaleDateString()}
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Gender</Label>
                        <p className="font-medium text-gray-700">
                          {user.gender === 'M' ? 'Male' : user.gender === 'F' ? 'Female' : 'Other'}
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Address</Label>
                        <p className="font-medium flex items-start text-gray-700">
                          <MapPin className="w-4 h-4 mr-2 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm leading-relaxed">{user.address}</span>
                        </p>
                      </div>
                      
                      {user.aadhaar_number && (
                        <div className="space-y-2">
                          <Label className="text-xs text-gray-500 uppercase tracking-wide font-medium">Aadhaar</Label>
                          <p className="font-medium flex items-center text-gray-700">
                            <Shield className="w-4 h-4 mr-2 text-blue-500" />
                            {user.aadhaar_number}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="pt-6 border-t border-gray-200">
                    <Button
                      onClick={() => navigate("/chat")}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
                    >
                      Continue to Chat Assistant
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Documents Section - Takes remaining space */}
            <div className="xl:col-span-3 space-y-6 lg:space-y-8">
              {/* Existing Documents */}
              <Card className="shadow-lg border-0 bg-white/70 backdrop-blur-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center justify-between text-lg">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 mr-2 text-green-600" />
                      Your Documents
                      <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                        {documents.length}
                      </span>
                    </div>
                  </CardTitle>
                  <CardDescription className="text-sm">
                    Documents from your DigiLocker account
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loadingDocuments ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="text-center">
                        <Loader2 className="w-8 h-8 text-blue-500 mx-auto mb-4 animate-spin" />
                        <p className="text-gray-500 font-medium">Loading documents...</p>
                      </div>
                    </div>
                  ) : documents.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <FileText className="w-8 h-8 text-gray-400" />
                      </div>
                      <p className="text-gray-600 font-medium mb-2">No documents found</p>
                      <p className="text-sm text-gray-400">Upload your first document below</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {documents.map((doc) => (
                        <div
                          key={doc.doc_id}
                          className="group p-4 border border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all duration-200 bg-white/50"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-start space-x-3 flex-1 min-w-0">
                              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                                <FileText className="w-5 h-5 text-white" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <h4 className="font-semibold text-gray-900 truncate">{doc.name}</h4>
                                <p className="text-sm text-gray-500 mt-1">
                                  #{doc.doc_number}
                                </p>
                                <p className="text-xs text-gray-400 mt-1">
                                  Issued: {new Date(doc.issue_date).toLocaleDateString()}
                                </p>
                                {doc.expiry_date && (
                                  <p className="text-xs text-gray-400">
                                    Expires: {new Date(doc.expiry_date).toLocaleDateString()}
                                  </p>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
                              {doc.is_verified && (
                                <CheckCircle className="w-5 h-5 text-green-500" />
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDocumentDownload(doc.doc_id, `${doc.name}.pdf`)}
                                className="opacity-0 group-hover:opacity-100 transition-opacity"
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Upload New Document - Improved scrollable form */}
              <Card className="shadow-lg border-0 bg-white/70 backdrop-blur-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center text-lg">
                    <Upload className="w-5 h-5 mr-2 text-purple-600" />
                    Upload New Document
                  </CardTitle>
                  <CardDescription className="text-sm">
                    Add a new document to your profile
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Form fields in responsive grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="documentType" className="text-sm font-medium text-gray-700">
                          Document Type *
                        </Label>
                        <Select value={newDocumentType} onValueChange={setNewDocumentType}>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select document type" />
                          </SelectTrigger>
                          <SelectContent>
                            {documentTypes.map((type) => (
                              <SelectItem key={type.id} value={type.id.toString()}>
                                {type.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="documentNumber" className="text-sm font-medium text-gray-700">
                          Document Number *
                        </Label>
                        <Input
                          id="documentNumber"
                          value={newDocumentNumber}
                          onChange={(e) => setNewDocumentNumber(e.target.value)}
                          placeholder="Enter document number"
                          className="w-full"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="issueDate" className="text-sm font-medium text-gray-700">
                          Issue Date *
                        </Label>
                        <Input
                          id="issueDate"
                          type="date"
                          value={newDocumentIssueDate}
                          onChange={(e) => setNewDocumentIssueDate(e.target.value)}
                          className="w-full"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="expiryDate" className="text-sm font-medium text-gray-700">
                          Expiry Date
                          <span className="text-gray-400 text-xs ml-1">(Optional)</span>
                        </Label>
                        <Input
                          id="expiryDate"
                          type="date"
                          value={newDocumentExpiryDate}
                          onChange={(e) => setNewDocumentExpiryDate(e.target.value)}
                          className="w-full"
                        />
                      </div>
                    </div>

                    {/* File upload section */}
                    <div className="space-y-3">
                      <Label htmlFor="documentFile" className="text-sm font-medium text-gray-700">
                        Document File *
                      </Label>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 transition-colors">
                        <Input
                          id="documentFile"
                          type="file"
                          onChange={handleFileSelect}
                          accept=".pdf,.jpg,.jpeg,.png,.gif,.txt"
                          className="w-full file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                      </div>
                      {selectedFile && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <p className="text-sm text-blue-800 font-medium">
                            📄 {selectedFile.name}
                          </p>
                          <p className="text-xs text-blue-600">
                            Size: {documentService.formatFileSize(selectedFile.size)}
                          </p>
                        </div>
                      )}
                      <p className="text-xs text-gray-500">
                        Supported formats: PDF, JPG, PNG, GIF, TXT • Maximum size: 10MB
                      </p>
                    </div>

                    {/* Upload button */}
                    <div className="pt-4 border-t border-gray-200">
                      <Button
                        onClick={handleDocumentUpload}
                        disabled={uploadingDocument || !selectedFile || !newDocumentType || !newDocumentNumber || !newDocumentIssueDate}
                        className="w-full md:w-auto bg-purple-600 hover:bg-purple-700 text-white font-medium py-2.5 px-8"
                      >
                        {uploadingDocument ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Upload className="w-4 h-4 mr-2" />
                            Upload Document
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KYC;
