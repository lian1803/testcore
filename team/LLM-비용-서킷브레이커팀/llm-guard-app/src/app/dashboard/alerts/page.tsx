'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

// Alert thresholds configuration
const thresholds = [
  {
    level: '50%',
    color: '#58a6ff',
    colorClass: 'text-[#58a6ff]',
    channels: ['Email'],
  },
  {
    level: '80%',
    color: '#f0c040',
    colorClass: 'text-[#f0c040]',
    channels: ['Slack', 'Email'],
  },
  {
    level: '100%',
    color: '#ff4444',
    colorClass: 'text-[#ff4444]',
    channels: ['Slack', 'Email'],
  },
];

// Mock alert history (will be replaced by API data in future)
const mockAlertHistory = [
  {
    time: '2:15 PM',
    level: '80%',
    message: 'Budget threshold reached for Production API',
  },
  {
    time: '12:30 PM',
    level: '50%',
    message: 'Budget alert for Development project',
  },
  {
    time: '10:15 AM',
    level: '100%',
    message: 'Budget limit exceeded - requests blocked',
  },
];

export default function AlertsPage() {
  const [slackConnected, setSlackConnected] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [loopDetectionEnabled, setLoopDetectionEnabled] = useState(false);
  const [retryThreshold, setRetryThreshold] = useState(5);

  const handleSaveAlerts = async () => {
    try {
      // TODO: Implement API call to save alerts
      // const response = await fetch('/api/dashboard/alerts', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     emailNotifications,
      //     loopDetectionEnabled,
      //     retryThreshold,
      //   }),
      // });

      toast.success('Alert settings saved');
    } catch (error) {
      console.error('[Save Alerts Error]', error);
      toast.error('Failed to save alert settings');
    }
  };

  const handleConnectSlack = async () => {
    try {
      // TODO: Implement Slack OAuth flow
      // Redirect to Slack OAuth endpoint
      toast.success('Slack connected successfully');
      setSlackConnected(true);
    } catch (error) {
      console.error('[Slack Connect Error]', error);
      toast.error('Failed to connect Slack');
    }
  };

  const handleTestAlerts = async () => {
    try {
      // TODO: Implement test alert API call
      toast.success('Test alert sent to your channels');
    } catch (error) {
      console.error('[Test Alert Error]', error);
      toast.error('Failed to send test alert');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Alert Settings</h1>
          <p className="text-[#8b949e]">Configure when and where to get alerts</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleTestAlerts}
            className="text-xs"
          >
            Test Alerts
          </Button>
          <Button
            onClick={handleSaveAlerts}
            className="bg-[#00ff88] text-[#0d1117] font-bold text-xs"
          >
            Save Changes
          </Button>
        </div>
      </div>

      {/* Notification Channels */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Notification Channels</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Email */}
            <div className="flex items-center justify-between p-4 bg-[#0d1117] rounded-lg">
              <div>
                <p className="font-medium">Email</p>
                <p className="text-sm text-[#8b949e]">your@email.com</p>
              </div>
              <Switch
                checked={emailNotifications}
                onCheckedChange={setEmailNotifications}
              />
            </div>

            {/* Slack */}
            <div className="flex items-center justify-between p-4 bg-[#0d1117] rounded-lg">
              <div>
                <p className="font-medium">Slack</p>
                <p className="text-sm text-[#8b949e]">
                  {slackConnected ? 'Connected to #alerts' : 'Not connected'}
                </p>
              </div>
              {!slackConnected ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleConnectSlack}
                  className="text-xs"
                >
                  Connect
                </Button>
              ) : (
                <Badge className="bg-[#00ff88]/20 text-[#00ff88]">
                  Connected
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Budget Thresholds */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Budget Thresholds</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {thresholds.map((threshold, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-[#0d1117] rounded-lg border border-[#30363d]"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="font-medium">
                        <span className={`${threshold.colorClass} font-bold`}>
                          {threshold.level}
                        </span>{' '}
                        Budget Used
                      </p>
                      <p className="text-sm text-[#8b949e]">
                        {threshold.channels.join(' + ')}
                      </p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Agent Loop Detection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="bg-[#161b22] border-[#30363d] relative">
          {!loopDetectionEnabled && (
            <div className="absolute inset-0 bg-[#0d1117]/30 backdrop-blur-sm rounded-lg flex items-center justify-center z-10">
              <div className="text-center">
                <Badge className="bg-[#f0c040]/20 text-[#f0c040] mb-3">
                  PRO FEATURE
                </Badge>
                <p className="text-sm text-[#8b949e] mb-4">
                  Upgrade to unlock agent loop detection
                </p>
                <Button
                  size="sm"
                  className="bg-[#00ff88] text-[#0d1117] font-bold"
                >
                  Upgrade to Pro
                </Button>
              </div>
            </div>
          )}

          <CardHeader>
            <CardTitle>Agent Loop Detection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 opacity-60">
            <div className="flex items-center justify-between p-4 bg-[#0d1117] rounded-lg">
              <div>
                <p className="font-medium">Enable Detection</p>
                <p className="text-sm text-[#8b949e]">
                  Automatically detect repetitive API calls
                </p>
              </div>
              <Switch
                checked={loopDetectionEnabled}
                onCheckedChange={setLoopDetectionEnabled}
              />
            </div>

            <div>
              <label className="text-sm font-medium text-[#8b949e] mb-3 block">
                Retry Threshold: {retryThreshold} calls
              </label>
              <Slider
                value={[retryThreshold]}
                onValueChange={(val) => setRetryThreshold(Array.isArray(val) ? val[0] : val)}
                min={1}
                max={20}
                step={1}
                className="w-full"
              />
              <p className="text-xs text-[#6e7681] mt-2">
                Block if same request is retried more than {retryThreshold}{' '}
                times
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Alert History */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockAlertHistory.map((alert, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-4 p-3 bg-[#0d1117] rounded"
                >
                  <div className="text-xs text-[#6e7681] flex-shrink-0 w-12">
                    {alert.time}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">{alert.message}</p>
                  </div>
                  <Badge
                    className={`flex-shrink-0 ${
                      alert.level === '50%'
                        ? 'bg-[#58a6ff]/20 text-[#58a6ff]'
                        : alert.level === '80%'
                        ? 'bg-[#f0c040]/20 text-[#f0c040]'
                        : 'bg-[#ff4444]/20 text-[#ff4444]'
                    }`}
                  >
                    {alert.level}
                  </Badge>
                </div>
              ))}
            </div>
            <p className="text-xs text-[#6e7681] mt-4">
              Alert history will be loaded from API in future updates
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
