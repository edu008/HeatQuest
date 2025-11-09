import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

type Lang = "en";

type Vars = Record<string, string | number>;

interface I18nContextType {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: string, vars?: Vars) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

const dictionaries: Record<Lang, Record<string, string>> = {
  en: {
    loading: "Loading...",
    analyze: "Analyze",
    hello_user: "Hello, {name}! 👋",
    analyzing_area: "Analyzing Area...",
    checking_area_cached: "Checking if this area was already scanned",
    area_analysis: "Area Analysis 🔥",
    total_cells: "Total Cells",
    hotspots: "Hotspots",
    avg_temp: "Avg Temp",
    avg_ndvi: "Avg NDVI",
    previously_scanned: "Previously scanned area",
    newly_scanned: "Newly scanned area",
    scanned_times: "Scanned {count} time(s) by community",
    map: "Map",
    leaderboard: "Leaderboard",
    profile: "Profile",
    not_found_title: "404",
    not_found_desc: "Oops! Page not found",
    return_home: "Return to Home",
    mapbox_token_title: "Mapbox Token",
    mapbox_token_desc: "Add your Mapbox public token to load the map.",
    token_placeholder: "pk.eyJ1Ijo...",
    show_map: "Show map",
    token_help: "You can find the token at mapbox.com → Tokens.",
    switch_to_german: "Switch to German",
    switch_to_english: "Switch to English",
    leaderboard_title: "Leaderboard",
    leaderboard_subtitle: "Top Climate Warriors",
    you: "You",
    level_label: "Level",
    missions_label: "Missions",
    xp_label: "XP",
    experience_points: "Experience Points",
    until_level: "Until level {next}",
    completed_label: "Completed",
    active_missions_label: "Active Missions",
    completed_missions_label: "Completed Missions",
    heat_risk: "Heat Risk",
    mission_back: "Back",
    mission_fallback_location: "Mission",
    mission_xp_bonus: "+100 XP",
    mission_steps: "{count} steps",
    mission_minutes: "{minutes} min",
    mission_context_title: "Context",
    mission_actions_title: "Actions",
    mission_action_done: "Done",
    mission_action_todo: "Todo",
    mission_complete_cta: "Complete Mission",
    mission_photo_required_title: "Photo Required",
    mission_photo_required_desc: "Upload a quick photo to confirm this action.",
    mission_photo_added: "Photo added ✅",
    cancel: "Cancel",
    openCamera: "Open Camera",
    mission_complete_toast_select_action: "Select at least one action",
    mission_complete_toast_add_photo: "Please add photos for checked actions",
    mission_complete_success: "Mission completed!",
    mission_complete_success_xp: "You earned XP and progressed your level.",
  },
};

function interpolate(str: string, vars?: Vars) {
  if (!vars) return str;
  return Object.keys(vars).reduce((s, k) => s.replace(new RegExp(`\\{${k}\\}`, "g"), String(vars[k])), str);
}

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Force English across the app
  const [lang, setLang] = useState<Lang>("en");

  const t = useMemo(() => {
    return (key: string, vars?: Vars) => {
      const dict = dictionaries[lang] || dictionaries.en;
      const raw = dict[key] ?? dictionaries.en[key] ?? key;
      return interpolate(raw, vars);
    };
  }, [lang]);

  return <I18nContext.Provider value={{ lang, setLang, t }}>{children}</I18nContext.Provider>;
};

export const useI18n = () => {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
};

export default I18nContext;