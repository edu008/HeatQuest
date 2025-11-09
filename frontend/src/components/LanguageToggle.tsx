import { Button } from "@/components/ui/button";
import { useI18n } from "@/contexts/I18nContext";

const LanguageToggle = () => {
  const { lang, setLang, t } = useI18n();

  const toggle = () => setLang(lang === "en" ? "de" : "en");

  return (
    <div className="fixed top-2 right-2 z-[1001] pb-[env(safe-area-inset-top)]">
      <Button
        variant="outline"
        size="sm"
        onClick={toggle}
        className="rounded-full px-3 h-8 text-xs bg-card/80 backdrop-blur-sm"
        aria-label={lang === "en" ? t("switch_to_german") : t("switch_to_english")}
      >
        {lang === "en" ? "DE" : "EN"}
      </Button>
    </div>
  );
};

export default LanguageToggle;