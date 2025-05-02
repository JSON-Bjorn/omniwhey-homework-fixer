import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
    FileSpreadsheet,
    Plus,
    Search,
    Copy,
    Trash2
} from 'lucide-react';
import { templatesAPI } from '@/lib/api';
import { Template } from '@/lib/types';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/hooks/useAuth';

const Templates: React.FC = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        structure: '', // JSON structure
        is_public: false
    });

    const { toast } = useToast();
    const { user } = useAuth();

    // Fetch templates
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ['templates'],
        queryFn: () => templatesAPI.getTemplates(),
        select: (response) => response.data as Template[],
    });

    // Handle form changes
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    // Handle switch change
    const handleSwitchChange = (checked: boolean) => {
        setFormData(prev => ({ ...prev, is_public: checked }));
    };

    // Create template
    const handleCreateTemplate = async () => {
        try {
            // Parse structure to ensure it's valid JSON
            JSON.parse(formData.structure);

            await templatesAPI.createTemplate(formData);
            toast({
                title: 'Template created',
                description: 'The template has been created successfully',
            });
            setIsCreateDialogOpen(false);
            setFormData({
                title: '',
                description: '',
                structure: '',
                is_public: false
            });
            refetch();
        } catch (error: any) {
            if (error instanceof SyntaxError) {
                toast({
                    title: 'Invalid JSON structure',
                    description: 'Please provide a valid JSON structure',
                    variant: 'destructive',
                });
            } else {
                toast({
                    title: 'Error',
                    description: error.response?.data?.detail || 'Failed to create template',
                    variant: 'destructive',
                });
            }
        }
    };

    // Handle template deletion
    const handleDeleteTemplate = async (id: number) => {
        if (window.confirm('Are you sure you want to delete this template?')) {
            try {
                await templatesAPI.deleteTemplate(id);
                toast({
                    title: 'Template deleted',
                    description: 'The template has been deleted successfully',
                });
                refetch();
            } catch (error: any) {
                toast({
                    title: 'Error',
                    description: error.response?.data?.detail || 'Failed to delete template',
                    variant: 'destructive',
                });
            }
        }
    };

    // Filter templates based on search query
    const filteredTemplates = data?.filter(template =>
        template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-3xl font-bold mb-6">PRD Templates</h1>

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <div className="flex-1 w-full md:w-auto relative">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                    <Input
                        placeholder="Search templates..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-9"
                    />
                </div>

                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="h-4 w-4 mr-2" />
                            Create Template
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[550px]">
                        <DialogHeader>
                            <DialogTitle>Create New Template</DialogTitle>
                            <DialogDescription>
                                Create a reusable template for PRD documents. Template structure should be in JSON format.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="py-4 space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="title">Title</Label>
                                <Input
                                    id="title"
                                    name="title"
                                    value={formData.title}
                                    onChange={handleInputChange}
                                    placeholder="Enter template title"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="description">Description</Label>
                                <Textarea
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                    placeholder="Describe the purpose of this template"
                                    className="h-20"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="structure">Template Structure (JSON)</Label>
                                <Textarea
                                    id="structure"
                                    name="structure"
                                    value={formData.structure}
                                    onChange={handleInputChange}
                                    placeholder='{"sections": [{"title": "Introduction", "fields": [{"name": "problem_statement", "type": "text", "label": "Problem Statement"}]}]}'
                                    className="h-32 font-mono text-sm"
                                />
                            </div>
                            <div className="flex items-center space-x-2">
                                <Switch
                                    id="is_public"
                                    checked={formData.is_public}
                                    onCheckedChange={handleSwitchChange}
                                />
                                <Label htmlFor="is_public">Make template public</Label>
                            </div>
                        </div>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                                Cancel
                            </Button>
                            <Button onClick={handleCreateTemplate}>
                                Create Template
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {isLoading && <p className="text-center py-8">Loading templates...</p>}

            {isError && (
                <div className="bg-red-100 dark:bg-red-900/20 border-l-4 border-red-500 text-red-700 dark:text-red-300 p-4 rounded mb-6">
                    <p>Failed to load templates. Please try again later.</p>
                </div>
            )}

            {!isLoading && filteredTemplates?.length === 0 && (
                <div className="text-center py-12">
                    <FileSpreadsheet className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-xl font-medium mb-2">No templates found</h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-6">
                        {searchQuery
                            ? "No templates match your search criteria."
                            : "You don't have access to any templates yet."}
                    </p>
                    <Dialog>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="h-4 w-4 mr-2" />
                                Create Your First Template
                            </Button>
                        </DialogTrigger>
                        {/* Dialog content would be duplicated here, so just closing the container */}
                    </Dialog>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredTemplates?.map((template) => (
                    <Card key={template.id} className="flex flex-col">
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                                <div>
                                    <CardTitle className="truncate">{template.title}</CardTitle>
                                    <CardDescription>
                                        {template.is_public
                                            ? "Public template"
                                            : template.owner_id === user?.id
                                                ? "Your private template"
                                                : "Shared with you"}
                                    </CardDescription>
                                </div>
                            </div>
                        </CardHeader>

                        <CardContent className="flex-grow">
                            <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-3">
                                {template.description || 'No description provided.'}
                            </p>
                            <div className="mt-4 text-xs text-gray-500">
                                <p className="flex items-center">
                                    <span className="font-semibold">Sections:</span>
                                    <span className="ml-1">
                                        {(() => {
                                            try {
                                                const structure = JSON.parse(template.structure);
                                                return structure.sections?.length || 0;
                                            } catch {
                                                return 0;
                                            }
                                        })()}
                                    </span>
                                </p>
                            </div>
                        </CardContent>

                        <CardFooter className="border-t pt-4">
                            <div className="flex justify-between w-full">
                                <Button variant="outline" size="sm">
                                    <Copy className="h-4 w-4 mr-2" />
                                    Use Template
                                </Button>

                                {template.owner_id === user?.id && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/20"
                                        onClick={() => handleDeleteTemplate(template.id)}
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                )}
                            </div>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default Templates; 