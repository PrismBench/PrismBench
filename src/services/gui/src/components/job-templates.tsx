"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";
import { useJobs } from "@/hooks/use-jobs";
import { JobTemplate, JobFormData } from "@/lib/types";
import { Plus, MoreHorizontal, Play, Trash2, Star } from "lucide-react";

interface JobTemplatesProps {
  onUseTemplate?: (template: JobTemplate) => void;
  showCreateDialog?: boolean;
}

export function JobTemplates({
  onUseTemplate,
  showCreateDialog = true,
}: JobTemplatesProps) {
  const { templates, createTemplate, deleteTemplate, createJob } = useJobs();
  const { toast } = useToast();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    name: "",
    description: "",
    sessionId: `session-${Date.now()}`,
    experimentConfig: "default",
    phaseSequence: "phase_1",
  });

  const handleCreateTemplate = () => {
    if (!newTemplate.name.trim()) {
      toast({
        title: "Error",
        description: "Template name is required",
        variant: "destructive",
      });
      return;
    }

    try {
      const config: JobFormData = {
        sessionId: newTemplate.sessionId,
        experimentConfig: newTemplate.experimentConfig,
        phaseSequence: newTemplate.phaseSequence
          .split(",")
          .map((p) => p.trim().replace(/^phase(\d+)$/, "phase_$1")),
      };

      createTemplate(newTemplate.name, newTemplate.description, config);

      toast({
        title: "Template Created",
        description: `Template "${newTemplate.name}" has been created successfully.`,
      });

      setCreateDialogOpen(false);
      setNewTemplate({
        name: "",
        description: "",
        sessionId: `session-${Date.now()}`,
        experimentConfig: "default",
        phaseSequence: "phase_1",
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to create template",
        variant: "destructive",
      });
    }
  };

  const handleUseTemplate = async (template: JobTemplate) => {
    if (onUseTemplate) {
      onUseTemplate(template);
      return;
    }

    // Create job directly from template
    try {
      const config = {
        ...template.config,
        sessionId: `${template.config.sessionId}-${Date.now()}`, // Make session ID unique
      };

      const job = await createJob(config);
      toast({
        title: "Job Created",
        description: `Job "${job.id}" has been created from template "${template.name}".`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to create job from template",
        variant: "destructive",
      });
    }
  };

  const handleDeleteTemplate = (template: JobTemplate) => {
    if (template.isDefault) {
      toast({
        title: "Cannot Delete",
        description: "Default templates cannot be deleted.",
        variant: "destructive",
      });
      return;
    }

    try {
      deleteTemplate(template.id);
      toast({
        title: "Template Deleted",
        description: `Template "${template.name}" has been deleted.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete template",
        variant: "destructive",
      });
    }
  };

  const formatPhases = (phases: string[] | undefined) => {
    if (!phases || phases.length === 0) return "No phases";
    return phases.join(", ");
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Job Templates</CardTitle>
          {showCreateDialog && (
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" className="h-8">
                  <Plus className="mr-2 h-4 w-4" />
                  New Template
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Job Template</DialogTitle>
                  <DialogDescription>
                    Create a reusable template for quick job creation.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="template-name">Template Name</Label>
                    <Input
                      id="template-name"
                      value={newTemplate.name}
                      onChange={(e) =>
                        setNewTemplate((prev) => ({
                          ...prev,
                          name: e.target.value,
                        }))
                      }
                      placeholder="Enter template name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="template-description">Description</Label>
                    <Textarea
                      id="template-description"
                      value={newTemplate.description}
                      onChange={(e) =>
                        setNewTemplate((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }))
                      }
                      placeholder="Describe what this template is for"
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="template-session">Session ID Pattern</Label>
                    <Input
                      id="template-session"
                      value={newTemplate.sessionId}
                      onChange={(e) =>
                        setNewTemplate((prev) => ({
                          ...prev,
                          sessionId: e.target.value,
                        }))
                      }
                      placeholder="session-template-name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="template-config">Experiment Config</Label>
                    <Input
                      id="template-config"
                      value={newTemplate.experimentConfig}
                      onChange={(e) =>
                        setNewTemplate((prev) => ({
                          ...prev,
                          experimentConfig: e.target.value,
                        }))
                      }
                      placeholder="default"
                    />
                  </div>
                  <div>
                    <Label htmlFor="template-phases">
                      Phases (comma-separated)
                    </Label>
                    <Input
                      id="template-phases"
                      value={newTemplate.phaseSequence}
                      onChange={(e) =>
                        setNewTemplate((prev) => ({
                          ...prev,
                          phaseSequence: e.target.value,
                        }))
                      }
                      placeholder="phase_1, phase_2, phase_3"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleCreateTemplate}>
                    Create Template
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {templates.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No templates available
          </div>
        ) : (
          <div className="space-y-3">
            {templates.map((template) => (
              <div
                key={template.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm">{template.name}</span>
                    {template.isDefault && (
                      <Badge variant="secondary" className="text-xs">
                        <Star className="mr-1 h-3 w-3" />
                        Default
                      </Badge>
                    )}
                  </div>
                  {template.description && (
                    <p className="text-xs text-muted-foreground mb-2">
                      {template.description}
                    </p>
                  )}
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>
                      Config: {template.config.experimentConfig || "default"}
                    </div>
                    <div>
                      Phases: {formatPhases(template.config.phaseSequence)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleUseTemplate(template)}
                    className="h-8"
                  >
                    <Play className="mr-2 h-3 w-3" />
                    Use
                  </Button>

                  {!template.isDefault && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-8 w-8 p-0"
                        >
                          <MoreHorizontal className="h-3 w-3" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => handleDeleteTemplate(template)}
                          className="text-red-600"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
