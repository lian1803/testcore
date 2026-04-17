"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { settingsData } from "@/lib/mock-data";
import { toast } from "sonner";

/* ─── Profile Section ───────────────────────────────– */
function ProfileSection() {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(settingsData.user.name);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setIsEditing(false);
    toast.success("프로필이 업데이트되었습니다.");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-white/7 p-8"
      style={{ background: "var(--bg-elevated)" }}
    >
      <div className="flex items-center gap-6 mb-8">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-2xl font-bold text-white shrink-0">
          {name.charAt(0)}
        </div>
        <div>
          <h2 className="text-lg font-bold text-white mb-1">프로필</h2>
          <p className="text-xs text-zinc-500">{settingsData.user.email}</p>
        </div>
      </div>

      {isEditing ? (
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-2">이름</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="이름을 입력하세요"
              className="bg-white/5 border-white/10 text-white"
            />
          </div>
          <div className="flex gap-3">
            <Button
              onClick={handleSave}
              disabled={isSaving}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isSaving ? (
                <>
                  <Loader className="w-3 h-3 animate-spin mr-2" />
                  저장 중...
                </>
              ) : (
                "저장"
              )}
            </Button>
            <Button
              onClick={() => setIsEditing(false)}
              variant="outline"
              disabled={isSaving}
            >
              취소
            </Button>
          </div>
        </div>
      ) : (
        <div className="mb-6">
          <p className="text-sm text-white mb-4">{name}</p>
          <Button
            onClick={() => setIsEditing(true)}
            variant="outline"
          >
            편집
          </Button>
        </div>
      )}
    </motion.div>
  );
}

/* ─── Password Section ───────────────────────────────– */
function PasswordSection() {
  const [isEditing, setIsEditing] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isChanging, setIsChanging] = useState(false);
  const [error, setError] = useState("");

  const handleChangePassword = async () => {
    setError("");

    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("모든 필드를 입력해주세요.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("새 비밀번호가 일치하지 않습니다.");
      return;
    }

    if (newPassword.length < 8) {
      setError("비밀번호는 최소 8자 이상이어야 합니다.");
      return;
    }

    setIsChanging(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsChanging(false);

    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setIsEditing(false);
    toast.success("비밀번호가 변경되었습니다.");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="rounded-xl border border-white/7 p-8"
      style={{ background: "var(--bg-elevated)" }}
    >
      <h2 className="text-lg font-bold text-white mb-2">비밀번호</h2>
      <p className="text-xs text-zinc-500 mb-6">계정 보안을 위해 정기적으로 비밀번호를 변경하세요.</p>

      {isEditing ? (
        <div className="space-y-4 mb-6">
          {error && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-xs text-red-400">
              {error}
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-2">현재 비밀번호</label>
            <Input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="현재 비밀번호"
              className="bg-white/5 border-white/10 text-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-2">새 비밀번호</label>
            <Input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="새 비밀번호"
              className="bg-white/5 border-white/10 text-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-2">비밀번호 확인</label>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="비밀번호 확인"
              className="bg-white/5 border-white/10 text-white"
            />
          </div>
          <div className="flex gap-3">
            <Button
              onClick={handleChangePassword}
              disabled={isChanging}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isChanging ? (
                <>
                  <Loader className="w-3 h-3 animate-spin mr-2" />
                  변경 중...
                </>
              ) : (
                "변경"
              )}
            </Button>
            <Button
              onClick={() => {
                setIsEditing(false);
                setError("");
              }}
              variant="outline"
              disabled={isChanging}
            >
              취소
            </Button>
          </div>
        </div>
      ) : (
        <Button
          onClick={() => setIsEditing(true)}
          variant="outline"
        >
          비밀번호 변경
        </Button>
      )}
    </motion.div>
  );
}

/* ─── Danger Zone ───────────────────────────────────– */
function DangerZone() {
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (confirmText !== "계정 탈퇴") {
      toast.error('"계정 탈퇴"를 입력해주세요.');
      return;
    }

    setIsDeleting(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsDeleting(false);

    toast.success("계정이 삭제되었습니다. 감사합니다.");
    // 실제로는 로그아웃 후 /login으로 리다이렉트
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="rounded-xl border border-red-500/30 bg-red-500/10 p-8"
    >
      <div className="flex items-start gap-4 mb-6">
        <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
        <div>
          <h2 className="text-lg font-bold text-red-200 mb-2">위험 구역</h2>
          <p className="text-xs text-red-300">
            이 섹션의 작업은 되돌릴 수 없습니다. 주의해서 진행하세요.
          </p>
        </div>
      </div>

      {!showConfirm ? (
        <Button
          onClick={() => setShowConfirm(true)}
          className="bg-red-600 hover:bg-red-700"
        >
          계정 탈퇴
        </Button>
      ) : (
        <div className="space-y-4">
          <div className="rounded-lg bg-black/40 border border-red-500/30 px-4 py-3">
            <p className="text-xs text-red-200 mb-3 font-semibold">
              계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
            </p>
            <p className="text-xs text-red-300 mb-4">
              &quot;계정 탈퇴&quot;를 입력하여 확인해주세요.
            </p>
            <Input
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder="계정 탈퇴"
              className="bg-white/5 border-red-500/30 text-white mb-4"
            />
            <div className="flex gap-3">
              <Button
                onClick={handleDelete}
                disabled={isDeleting}
                className="bg-red-600 hover:bg-red-700"
              >
                {isDeleting ? (
                  <>
                    <Loader className="w-3 h-3 animate-spin mr-2" />
                    삭제 중...
                  </>
                ) : (
                  "삭제"
                )}
              </Button>
              <Button
                onClick={() => {
                  setShowConfirm(false);
                  setConfirmText("");
                }}
                variant="outline"
                disabled={isDeleting}
              >
                취소
              </Button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}

/* ─── Page ───────────────────────────────────────────– */
export default function AccountPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">계정 설정</h1>
        <p className="text-sm text-zinc-500">프로필, 보안 및 계정 정보를 관리합니다.</p>
      </div>

      {/* Profile */}
      <ProfileSection />

      {/* Password */}
      <PasswordSection />

      {/* Danger Zone */}
      <DangerZone />
    </div>
  );
}
