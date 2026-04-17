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
import { Copy, Eye, EyeOff, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at?: string;
  is_active: boolean;
}

interface ApiKeyResponse extends ApiKey {
  key?: string; // 1회만 노출
}

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  // 프로젝트 선택 (임시: 첫 번째 프로젝트 사용)
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');

  // 초기 로드: 프로젝트 및 API 키 조회
  useEffect(() => {
    const loadData = async () => {
      try {
        // 프로젝트 조회
        const projectRes = await fetch('/api/dashboard/projects');
        if (!projectRes.ok) throw new Error('Failed to fetch projects');
        const projectData = await projectRes.json();

        if (projectData.data && projectData.data.length > 0) {
          setSelectedProjectId(projectData.data[0].id);
        }

        // API 키 조회
        const keysRes = await fetch('/api/dashboard/api-keys');
        if (!keysRes.ok) throw new Error('Failed to fetch API keys');
        const keysData = await keysRes.json();
        setKeys(keysData.data || []);
      } catch (error) {
        console.error('[Load Keys Error]', error);
        toast.error('Failed to load API keys');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const toggleKeyVisibility = (id: string) => {
    const newVisible = new Set(visibleKeys);
    if (newVisible.has(id)) {
      newVisible.delete(id);
    } else {
      newVisible.add(id);
    }
    setVisibleKeys(newVisible);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const handleCreateKey = async () => {
    if (!newKeyName || !selectedProjectId) {
      toast.error('Please enter a key name and select a project');
      return;
    }

    setIsCreating(true);
    try {
      const response = await fetch('/api/dashboard/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: selectedProjectId,
          name: newKeyName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.error?.message || 'Failed to create API key');
        return;
      }

      // 새 키를 표시 목록에 추가
      const newKey: ApiKey = {
        id: data.data.prefix,
        name: newKeyName,
        key_prefix: data.data.prefix,
        created_at: new Date().toISOString(),
        is_active: true,
      };
      setKeys([...keys, newKey]);

      // 1회용 키 표시 (복사 유도)
      const temp = new Set(visibleKeys);
      temp.add(data.data.prefix);
      setVisibleKeys(temp);

      toast.success('API key created. Save it securely!');
      toast.message(`Key: ${data.data.key}`);

      setNewKeyName('');
      setIsDialogOpen(false);
    } catch (error) {
      console.error('[Create Key Error]', error);
      toast.error('Failed to create API key');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteKey = async (id: string) => {
    try {
      const response = await fetch(`/api/dashboard/api-keys/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        toast.error('Failed to delete API key');
        return;
      }

      setKeys(keys.filter((k) => k.id !== id));
      toast.success('API key deleted');
    } catch (error) {
      console.error('[Delete Key Error]', error);
      toast.error('Failed to delete API key');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">API Keys</h1>
          <p className="text-[#8b949e]">
            Create and manage API keys for the LLM Guard SDK
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger className="bg-[#00ff88] text-[#0d1117] font-bold font-semibold px-4 py-2 rounded-md text-sm hover:opacity-90">
            + Create Key
          </DialogTrigger>
          <DialogContent className="bg-[#161b22] border-[#30363d]">
            <DialogHeader>
              <DialogTitle>Create New API Key</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="keyname" className="text-[#8b949e]">
                  Key Name
                </Label>
                <Input
                  id="keyname"
                  placeholder="e.g., Production API"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  disabled={isCreating}
                  className="mt-2 bg-[#0d1117] border-[#30363d]"
                />
              </div>
              <Button
                onClick={handleCreateKey}
                disabled={isCreating}
                className="w-full bg-[#00ff88] text-[#0d1117] font-bold"
              >
                {isCreating ? 'Creating...' : 'Create Key'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Keys List */}
      <div className="space-y-4">
        {keys.map((key, idx) => (
          <motion.div
            key={key.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: idx * 0.1 }}
          >
            <Card className="bg-[#161b22] border-[#30363d]">
              <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Left */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <p className="font-bold">{key.name}</p>
                      <Badge className="bg-[#00ff88]/20 text-[#00ff88] text-xs">
                        {key.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>

                    {/* Key Display */}
                    <div className="bg-[#0d1117] rounded px-3 py-2 font-mono text-sm flex items-center justify-between mb-3">
                      <span className="text-[#6e7681]">
                        {visibleKeys.has(key.id)
                          ? key.key_prefix
                          : key.key_prefix.substring(0, 8) + '•'.repeat(24)}
                      </span>
                      <button
                        onClick={() => toggleKeyVisibility(key.id)}
                        className="text-[#6e7681] hover:text-[#e6edf3] transition-colors"
                      >
                        {visibleKeys.has(key.id) ? (
                          <EyeOff size={16} />
                        ) : (
                          <Eye size={16} />
                        )}
                      </button>
                    </div>

                    {/* Meta Info */}
                    <div className="grid grid-cols-2 gap-4 text-xs text-[#6e7681]">
                      <div>
                        <p className="text-[#8b949e] font-medium">Created</p>
                        <p>{new Date(key.created_at).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <p className="text-[#8b949e] font-medium">Last Used</p>
                        <p>{key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => copyToClipboard(key.key_prefix)}
                      className="text-xs"
                    >
                      <Copy size={14} className="mr-1" />
                      Copy
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDeleteKey(key.id)}
                      className="text-xs"
                    >
                      <Trash2 size={14} className="mr-1" />
                      Delete
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Usage Example */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: keys.length * 0.1 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Usage Example</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-[#0d1117] rounded p-4 overflow-x-auto">
              <pre className="text-sm font-mono text-[#e6edf3]">
{`from llm_guard.openai import OpenAI

# Automatically guarded
client = OpenAI(api_key="your-openai-key")

# Set a budget cap (optional)
client.set_budget_limit(50.0)  # $50/month

# Use as normal
response = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role": "user", "content": "..."}]
)`}
              </pre>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Documentation Link */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: (keys.length + 1) * 0.1 }}
        className="text-center p-6 bg-[#161b22] border border-[#30363d] rounded-lg"
      >
        <p className="text-[#8b949e] mb-3">
          Need help? Check out our documentation
        </p>
        <Button
          variant="outline"
          className="text-[#00ff88] border-[#00ff88]"
        >
          View Docs →
        </Button>
      </motion.div>
    </div>
  );
}
