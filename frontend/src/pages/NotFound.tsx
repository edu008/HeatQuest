import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/contexts/I18nContext";

const NotFound = () => {
  const location = useLocation();
  const { t } = useI18n();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="mb-4 text-4xl font-bold">{t("not_found_title")}</h1>
        <p className="mb-4 text-xl text-muted-foreground">{t("not_found_desc")}</p>
        <Button asChild>
          <Link to="/">{t("return_home")}</Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
