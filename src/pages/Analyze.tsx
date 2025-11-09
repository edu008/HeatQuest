import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useGame } from "@/contexts/GameContext";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, Upload, Loader2 } from "lucide-react";

interface AnalysisResult {
  is_hotspot: boolean;
  heat_risk_score: number;
  reasons: string[];
  suggested_actions: string[];
}

const Analyze = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const { addMission } = useGame();
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const analyzeImage = async () => {
    if (!imageFile) return;

    setAnalyzing(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const mockResult: AnalysisResult = {
      is_hotspot: Math.random() > 0.3,
      heat_risk_score: Math.random() * 0.6 + 0.3,
      reasons: [
        "Große Asphaltfläche ohne Schatten",
        "Keine sichtbare Vegetation",
        "Hohe Sonneneinstrahlung zur Mittagszeit",
      ],
      suggested_actions: [
        "Bäume entlang der Straße pflanzen",
        "Reflektierende Oberflächen installieren",
        "Wasserflächen zur Kühlung hinzufügen",
        "Schattenstrukturen errichten",
      ],
    };

    setResult(mockResult);
    setAnalyzing(false);
  };

  const createMission = () => {
    if (!result) return;

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const newMission = {
          id: Date.now().toString(),
          title: `Neuer Hotspot`,
          description: "Von dir entdeckter Hotspot",
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          heatRisk: Math.round(result.heat_risk_score * 100),
          reasons: result.reasons,
          actions: result.suggested_actions,
          completed: false,
        };

        addMission(newMission);
        navigate(`/mission/${newMission.id}`);
      });
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <motion.div
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="sticky top-0 z-10 bg-card/95 backdrop-blur-sm border-b border-border p-4"
      >
        <div className="flex items-center gap-4 max-w-2xl mx-auto">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="rounded-full"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold">Hotspot Analyse</h1>
            <p className="text-sm text-muted-foreground">
              Foto analysieren und Mission erstellen
            </p>
          </div>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto p-4 space-y-6">
        <Card className="p-6 rounded-3xl">
          {!imagePreview ? (
            <label className="flex flex-col items-center justify-center min-h-[300px] cursor-pointer border-2 border-dashed border-border rounded-2xl hover:border-primary transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto bg-gradient-to-br from-heat to-primary rounded-full flex items-center justify-center">
                  <Camera className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="font-semibold">Foto aufnehmen oder hochladen</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Straße, Park, Platz oder andere urbane Fläche
                  </p>
                </div>
                <Button type="button" variant="outline" className="rounded-xl">
                  <Upload className="w-4 h-4 mr-2" />
                  Bild auswählen
                </Button>
              </div>
            </label>
          ) : (
            <div className="space-y-4">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-64 object-cover rounded-2xl"
              />
              <div className="flex gap-2">
                <Button
                  onClick={analyzeImage}
                  disabled={analyzing}
                  className="flex-1 rounded-xl bg-gradient-to-r from-heat to-primary"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analysiere...
                    </>
                  ) : (
                    "🔍 Analysieren"
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setImageFile(null);
                    setImagePreview(null);
                    setResult(null);
                  }}
                  className="rounded-xl"
                >
                  Neu
                </Button>
              </div>
            </div>
          )}
        </Card>

        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <Card className="p-6 rounded-3xl">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Heat Risk Score</h3>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-muted rounded-full h-4">
                      <div
                        className="bg-gradient-to-r from-heat to-heat-intense h-full rounded-full transition-all"
                        style={{ width: `${result.heat_risk_score * 100}%` }}
                      />
                    </div>
                    <span className="text-2xl font-bold text-heat">
                      {Math.round(result.heat_risk_score * 100)}%
                    </span>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Gründe</h3>
                  <ul className="space-y-2">
                    {result.reasons.map((reason, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-muted-foreground"
                      >
                        <span className="text-heat">🔥</span>
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Vorgeschlagene Aktionen</h3>
                  <ul className="space-y-2">
                    {result.suggested_actions.map((action, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-muted-foreground"
                      >
                        <span className="text-cool">🌳</span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>

                {result.is_hotspot && (
                  <Button
                    onClick={createMission}
                    className="w-full rounded-xl bg-gradient-to-r from-heat via-primary to-cool-intense hover:shadow-lg"
                  >
                    🚀 Mission erstellen
                  </Button>
                )}
              </div>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Analyze;
