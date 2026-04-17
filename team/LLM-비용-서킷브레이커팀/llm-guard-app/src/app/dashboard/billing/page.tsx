'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';

export default function BillingPage() {
  const handleUpgrade = () => {
    // Stripe 연동 시 구현
  };

  return (
    <div className="p-6 space-y-6">
      {/* Coming Soon Notice */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0 }}
      >
        <Card className="bg-[#161b22] border-[#f0c040] border-2">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <AlertCircle className="text-[#f0c040] w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-lg mb-2">Billing Coming Soon</h3>
                <p className="text-[#8b949e] mb-4">
                  Payment processing and billing features are currently in development.
                  Stripe integration will be available soon.
                </p>
                <p className="text-sm text-[#6e7681]">
                  For now, you can use the free tier with unlimited API requests.
                  Paid plans will be available with the next release.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Free Plan Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-[#8b949e] text-sm mb-2">Plan</p>
                <p className="text-3xl font-bold text-[#00ff88]">Free</p>
                <p className="text-sm text-[#6e7681] mt-2">
                  $0/month • Always free
                </p>
              </div>

              <div>
                <p className="text-[#8b949e] text-sm mb-2">Features</p>
                <ul className="text-sm text-[#8b949e] space-y-1">
                  <li>✓ Unlimited API requests</li>
                  <li>✓ 1 project</li>
                  <li>✓ Basic alerts</li>
                </ul>
              </div>

              <div>
                <p className="text-[#8b949e] text-sm mb-2">Next Billing Date</p>
                <p className="text-3xl font-bold">N/A</p>
                <p className="text-sm text-[#6e7681] mt-2">Free plan always free</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Future Plans Preview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Coming Soon: Paid Plans</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 bg-[#0d1117] rounded-lg border border-[#30363d]">
                <p className="font-bold mb-3">Pro Plan</p>
                <p className="text-sm text-[#8b949e] mb-4">
                  Advanced features for production applications
                </p>
                <ul className="text-sm text-[#6e7681] space-y-2 mb-4">
                  <li>✓ Unlimited projects</li>
                  <li>✓ Agent loop detection</li>
                  <li>✓ Slack integration</li>
                  <li>✓ Priority support</li>
                </ul>
                <Badge className="bg-[#f0c040]/20 text-[#f0c040]">Coming Soon</Badge>
              </div>

              <div className="p-4 bg-[#0d1117] rounded-lg border border-[#00ff88]/30">
                <p className="font-bold mb-3 text-[#00ff88]">Enterprise</p>
                <p className="text-sm text-[#8b949e] mb-4">
                  Custom plans for large organizations
                </p>
                <ul className="text-sm text-[#6e7681] space-y-2 mb-4">
                  <li>✓ All Pro features</li>
                  <li>✓ Custom rate limits</li>
                  <li>✓ Dedicated support</li>
                  <li>✓ SLA guarantees</li>
                </ul>
                <Badge className="bg-[#00ff88]/20 text-[#00ff88]">Contact Sales</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Documentation Link */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="text-center p-6 bg-[#161b22] border border-[#30363d] rounded-lg"
      >
        <p className="text-[#8b949e] mb-3">
          Have questions about billing?
        </p>
        <Button
          variant="outline"
          className="text-[#00ff88] border-[#00ff88]"
        >
          Contact Support →
        </Button>
      </motion.div>
    </div>
  );
}
