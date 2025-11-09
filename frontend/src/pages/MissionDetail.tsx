import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useGame } from "@/contexts/GameContext";
import { ArrowLeft, MapPin, CheckCircle2, Flame, Sparkles, Target, Clock, FileText, Camera, Flag } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useI18n } from "@/contexts/I18nContext";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";

const MissionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { missions, completeMission } = useGame();
  const { t } = useI18n();

  const [checkedActions, setCheckedActions] = useState<Set<number>>(new Set());
  const [actionProofs, setActionProofs] = useState<Record<number, string>>({});
  const [pendingProofIndex, setPendingProofIndex] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [uploadPromptOpen, setUploadPromptOpen] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [showEntryPop, setShowEntryPop] = useState(true);

  // Entry pop effect
  useEffect(() => {
    setShowEntryPop(true);
    const tmr = setTimeout(() => setShowEntryPop(false), 900);
    return () => clearTimeout(tmr);
  }, [id]);

  const mission = missions.find((m) => m.id === id);

  useEffect(() => {
    if (!mission) {
      navigate("/map");
      return;
    }
  }, [mission, navigate]);

  if (!mission) return null;

  const toggleAction = (index: number) => {
    setCheckedActions((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
        return next;
      }
      // Require photo proof before marking as done
      if (actionProofs[index]) {
        next.add(index);
        return next;
      }
      setPendingProofIndex(index);
      setUploadPromptOpen(true);
      return prev; // unchanged until proof added
    });
  };

  const handleActionProofSelected = (file: File, actionIndex: number) => {
    const reader = new FileReader();
    reader.onload = () => {
      const url = reader.result as string;
      setActionProofs((prev) => ({ ...prev, [actionIndex]: url }));
      toast({ title: t("mission_photo_added") });
      setCheckedActions((prev) => {
        const next = new Set(prev);
        next.add(actionIndex);
        return next;
      });
    };
    reader.readAsDataURL(file);
  };

  const handleComplete = () => {
    if (checkedActions.size === 0) {
      toast({ title: t("mission_complete_toast_select_action"), variant: "destructive" });
      return;
    }
    const missingProof = Array.from(checkedActions).some((i) => !actionProofs[i]);
    if (missingProof) {
      toast({ title: t("mission_complete_toast_add_photo"), variant: "destructive" });
      return;
    }
    completeMission(mission.id);
    toast({ title: t("mission_complete_success"), description: t("mission_complete_success_xp") });
    navigate("/profile");
  };

  const completionPercentage = (checkedActions.size / mission.actions.length) * 100;
  const timeEstimate = mission.actions.length * 5; // minutes
  const handleOpenCamera = () => fileInputRef.current?.click();

  return (
    <div className="relative h-[100dvh] w-full overflow-hidden bg-background">
      {/* Entry pop overlay */}
      <AnimatePresence>
        {showEntryPop && (
          <motion.div
            className="pointer-events-none absolute inset-0 z-40 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <motion.div
              className="relative rounded-full p-5 bg-gradient-to-br from-orange-500 via-orange-500/90 to-rose-500 shadow-lg ring-8 ring-orange-500/25"
              initial={{ scale: 0.7 }}
              animate={{ scale: 1.06 }}
              exit={{ scale: 1.15 }}
              transition={{ type: "spring", stiffness: 320, damping: 18 }}
            >
              <Flag className="h-8 w-8 text-white" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        className="mx-auto h-full max-w-2xl p-3 grid grid-rows-[auto,auto,1fr,auto] gap-3"
        initial={{ opacity: 0, scale: 0.98, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 22 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between rounded-lg border bg-muted/40 px-2 py-2">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm hover:bg-muted"
          >
            <ArrowLeft className="h-4 w-4" />
            {t("mission_back")}
          </button>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <span>{mission.locationName || t("mission_fallback_location")}</span>
          </div>
        </div>

        {/* Title, heat badge and compact progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h1 className="text-base font-semibold truncate">{mission.title}</h1>
            <div className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-2 py-1 text-xs text-orange-700">
              <Flame className="h-4 w-4" />
              <span>{mission.heatRisk}%</span>
            </div>
          </div>
          <div className="w-full h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-primary via-heat to-cool-intense"
              style={{ width: `${Math.min(100, Math.round(completionPercentage))}%` }}
            />
          </div>
          {/* Compact stats row */}
          <div className="grid grid-cols-3 gap-2">
            <div className="flex items-center gap-2 rounded-lg border bg-card px-2 py-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-xs font-medium">{t("mission_xp_bonus")}</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg border bg-card px-2 py-2">
              <Target className="h-4 w-4 text-accent" />
              <span className="text-xs font-medium">{t("mission_steps", { count: mission.actions.length })}</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg border bg-card px-2 py-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs font-medium">{t("mission_minutes", { minutes: timeEstimate })}</span>
            </div>
          </div>
        </div>

        {/* Main content compact grid */}
        <div className="grid grid-rows-2 gap-3">
          {/* Description card */}
          <div className="rounded-xl border bg-card p-3 shadow-sm">
            <div className="mb-2 text-sm font-medium">{t("mission_context_title")}</div>
            <div className="flex items-start gap-2">
              <FileText className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
              <p className="text-sm text-muted-foreground leading-snug break-words max-h-20 overflow-hidden">
                {mission.description}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="rounded-xl border bg-card p-3 shadow-sm">
            <div className="mb-2 text-sm font-medium">{t("mission_actions_title")}</div>
            <ul className="grid grid-cols-2 gap-2">
              {mission.actions.map((action, index) => {
                const isChecked = checkedActions.has(index);
                return (
                  <li key={index} className="flex items-center justify-between gap-2 rounded-lg border bg-muted/40 px-2 py-2 overflow-hidden">
                    <label className="flex items-center gap-2 min-w-0 flex-1">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border shrink-0"
                        checked={isChecked}
                        onChange={() => toggleAction(index)}
                      />
                      <span className="text-xs truncate min-w-0">{action}</span>
                    </label>
                    <span className={isChecked ? "shrink-0 text-[10px] px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200" : "shrink-0 text-[10px] px-2 py-1 rounded-full bg-muted text-muted-foreground border"}>
                      {isChecked ? t("mission_action_done") : t("mission_action_todo")}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="grid grid-cols-1 gap-2 -mt-2 py-12">
          <motion.button
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-4 text-base font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60 shadow-sm"
            disabled={checkedActions.size === 0 || !Array.from(checkedActions).every((i) => !!actionProofs[i])}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            animate={completing ? { scale: 1.03 } : { scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            onClick={() => {
              if (checkedActions.size === 0 || !Array.from(checkedActions).every((i) => !!actionProofs[i])) return;
              setCompleting(true);
              setTimeout(() => {
                handleComplete();
                setCompleting(false);
              }, 180);
            }}
          >
            <CheckCircle2 className="h-5 w-5" />
            {t("mission_complete_cta")}
          </motion.button>
          {/* Hidden file input for action proofs */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file && pendingProofIndex !== null) {
                handleActionProofSelected(file, pendingProofIndex);
                setPendingProofIndex(null);
                e.currentTarget.value = ""; // reset input
              }
            }}
          />
        </div>

        {/* Upload prompt dialog */}
        <AlertDialog open={uploadPromptOpen} onOpenChange={setUploadPromptOpen}>
          <AlertDialogContent className="max-w-sm">
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-orange-500" />
                {t("mission_photo_required_title")}
              </AlertDialogTitle>
              <AlertDialogDescription>
                {t("mission_photo_required_desc")}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={() => setUploadPromptOpen(false)} className="rounded-xl">
                {t("cancel")}
              </AlertDialogCancel>
              <AlertDialogAction onClick={handleOpenCamera} className="bg-orange-500 hover:bg-orange-600 text-white rounded-xl">
                {t("openCamera")}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </motion.div>
    </div>
  );
};

export default MissionDetail;
