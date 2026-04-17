'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

interface Project {
  id: string | number;
  name: string;
  status: string;
  budget: number;
  used: number;
  requests: number;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectBudget, setNewProjectBudget] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 초기 로드: 프로젝트 조회
  useEffect(() => {
    const loadProjects = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await fetch('/api/dashboard/projects');

        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }

        const data = await response.json();
        setProjects(data.data || []);
      } catch (err) {
        console.error('[Load Projects Error]', err);
        setError(err instanceof Error ? err.message : 'Failed to load projects');
        toast.error('Failed to load projects');
      } finally {
        setIsLoading(false);
      }
    };

    loadProjects();
  }, []);

  const handleCreateProject = async () => {
    if (!newProjectName || !newProjectBudget) {
      toast.error('Please enter project name and budget');
      return;
    }

    setIsCreating(true);
    try {
      const response = await fetch('/api/dashboard/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newProjectName,
          budget: parseFloat(newProjectBudget),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.error?.message || 'Failed to create project');
        return;
      }

      const newProject: Project = {
        id: data.data.id,
        name: newProjectName,
        status: 'GUARDED',
        budget: parseFloat(newProjectBudget),
        used: 0,
        requests: 0,
      };

      setProjects([...projects, newProject]);
      setNewProjectName('');
      setNewProjectBudget('');
      setIsDialogOpen(false);
      toast.success('Project created successfully');
    } catch (err) {
      console.error('[Create Project Error]', err);
      toast.error('Failed to create project');
    } finally {
      setIsCreating(false);
    }
  };

  const handleUpdateProjectBudget = async (id: string | number, newBudget: number) => {
    if (newBudget <= 0) {
      toast.error('Budget must be greater than 0');
      return;
    }

    try {
      const response = await fetch(`/api/dashboard/projects/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ budget: newBudget }),
      });

      if (!response.ok) {
        toast.error('Failed to update budget');
        return;
      }

      setProjects(
        projects.map((p) => (p.id === id ? { ...p, budget: newBudget } : p))
      );
      toast.success('Budget updated');
    } catch (err) {
      console.error('[Update Budget Error]', err);
      toast.error('Failed to update budget');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'GUARDED':
        return 'bg-[#00ff88]/20 text-[#00ff88]';
      case 'WARNING':
        return 'bg-[#f0c040]/20 text-[#f0c040]';
      case 'AT_LIMIT':
        return 'bg-[#ff4444]/20 text-[#ff4444]';
      default:
        return 'bg-[#6e7681]/20 text-[#6e7681]';
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-10 bg-[#30363d] rounded w-1/3" />
          <div className="h-10 bg-[#30363d] rounded w-1/6" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="bg-[#161b22] border-[#30363d]">
              <CardContent className="pt-6">
                <div className="h-8 bg-[#30363d] rounded mb-3" />
                <div className="h-4 bg-[#30363d] rounded w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="bg-[#161b22] border-[#ff4444]">
          <CardContent className="pt-6">
            <p className="text-[#ff4444] mb-4">{error}</p>
            <Button
              onClick={() => window.location.reload()}
              className="bg-[#00ff88] text-[#0d1117] font-bold"
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Projects</h1>
          <p className="text-[#8b949e]">Manage budgets and monitor costs per project</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger>
            <Button className="bg-[#00ff88] text-[#0d1117] font-bold">
              + New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#161b22] border-[#30363d]">
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-[#8b949e]">
                  Project Name
                </Label>
                <Input
                  id="name"
                  placeholder="e.g., My API"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  disabled={isCreating}
                  className="mt-2 bg-[#0d1117] border-[#30363d]"
                />
              </div>
              <div>
                <Label htmlFor="budget" className="text-[#8b949e]">
                  Monthly Budget ($)
                </Label>
                <Input
                  id="budget"
                  type="number"
                  placeholder="e.g., 500"
                  value={newProjectBudget}
                  onChange={(e) => setNewProjectBudget(e.target.value)}
                  disabled={isCreating}
                  className="mt-2 bg-[#0d1117] border-[#30363d]"
                />
              </div>
              <Button
                onClick={handleCreateProject}
                disabled={isCreating}
                className="w-full bg-[#00ff88] text-[#0d1117] font-bold"
              >
                {isCreating ? 'Creating...' : 'Create Project'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold font-mono">
              {projects.length}
            </div>
            <p className="text-sm text-[#8b949e] mt-1">Active Projects</p>
          </CardContent>
        </Card>
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold font-mono text-[#00ff88]">
              ${projects.reduce((sum, p) => sum + p.budget, 0)}
            </div>
            <p className="text-sm text-[#8b949e] mt-1">Total Budget</p>
          </CardContent>
        </Card>
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold font-mono">
              {projects.reduce((sum, p) => sum + p.requests, 0).toLocaleString()}
            </div>
            <p className="text-sm text-[#8b949e] mt-1">Total Requests</p>
          </CardContent>
        </Card>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {projects.map((project, idx) => {
          const percentage = Math.round((project.used / project.budget) * 100);
          return (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.1 }}
            >
              <Card
                className={`bg-[#161b22] border-[#30363d] ${
                  project.status === 'AT_LIMIT'
                    ? 'border-[#ff4444] bg-[#1a1217]'
                    : ''
                }`}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                    <Badge className={getStatusColor(project.status)}>
                      {project.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Warning Banner */}
                  {project.status === 'WARNING' && (
                    <div className="bg-[#ff4444]/10 border-l-2 border-[#ff4444] px-4 py-2 rounded text-sm text-[#ff4444]">
                      Nearing budget limit. Requests will be blocked if exceeded.
                    </div>
                  )}

                  {/* Budget Bar */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-[#8b949e]">Budget Used</span>
                      <div className="flex items-end gap-2">
                        <span
                          className="font-mono text-lg font-bold cursor-pointer hover:text-[#00ff88] transition-colors"
                          contentEditable
                          onBlur={(e) => {
                            const newBudget = parseFloat(
                              e.currentTarget.textContent || '0'
                            );
                            if (newBudget > 0 && newBudget !== project.budget) {
                              handleUpdateProjectBudget(project.id, newBudget);
                            } else {
                              // 변경 없으면 원래 값으로 복원
                              e.currentTarget.textContent = String(project.budget);
                            }
                          }}
                          suppressContentEditableWarning
                        >
                          {project.budget}
                        </span>
                        <span className="text-xs text-[#6e7681]">edit</span>
                      </div>
                    </div>

                    <div className="w-full bg-[#21262d] rounded-full h-2">
                      <div
                        className={`h-full rounded-full transition-all ${
                          percentage > 80
                            ? 'bg-[#ff4444]'
                            : percentage > 50
                            ? 'bg-[#f0c040]'
                            : 'bg-[#00ff88]'
                        }`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between mt-2 text-xs text-[#6e7681]">
                      <span>${project.used} of ${project.budget}</span>
                      <span>{percentage}%</span>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-[#6e7681] mb-1">Requests</p>
                      <p className="font-mono font-bold">
                        {project.requests.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6e7681] mb-1">Avg Cost</p>
                      <p className="font-mono font-bold">
                        $
                        {(
                          project.used / Math.max(project.requests, 1)
                        ).toFixed(4)}
                      </p>
                    </div>
                  </div>

                  <Button variant="outline" size="sm" className="w-full text-xs">
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
