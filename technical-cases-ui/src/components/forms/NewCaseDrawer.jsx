import { useState } from "react";
import { X, Sparkles } from "lucide-react";
import Card from "../shared/Card";
import PhotoUploader from "./PhotoUploader";
import VerificationResultsCard from "./VerificationResultsCard";
import { analyzeImageForDamage } from "../../utils/damageAnalysis";

export default function NewCaseDrawer({ open, onClose }) {
  const [photos, setPhotos] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
  });

  if (!open) return null;

  const handleSendToAi = async () => {
    if (!formData.title || photos.length === 0) return;

    setIsAnalyzing(true);
    setAnalysis(null);

    try {
      const casePayload = {
        title: formData.title,
        photos: photos.map((photo) => photo.file),
        prompt: `Przeanalizuj uszkodzenia na podstawie tematu zgłoszenia: ${formData.title}`,
      };

      // TODO: zastąp mockowe wywołanie realnym endpointem backendowym
      const result = await analyzeImageForDamage(casePayload);
      setAnalysis(result);
    } catch (error) {
      console.error("Błąd analizy AI:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-3xl overflow-y-auto border-l border-neutralGray/50 bg-backgroundLight shadow-2xl">
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-neutralGray/40 bg-backgroundLight/95 px-6 py-4 backdrop-blur">
        <div>
          <p className="text-sm font-semibold text-darkGray">Formularz</p>
          <h2 className="text-xl font-bold text-appBlack">
            Nowe zgłoszenie techniczne
          </h2>
        </div>

        <button
          onClick={onClose}
          className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-white text-appBlack shadow-card"
        >
          <X size={18} />
        </button>
      </div>

      <div className="space-y-5 p-6">
        {/* Sekcja zdjęć z AI analizą */}
        <Card title="Dodaj zdjęcia do analizy">
          <PhotoUploader photos={photos} setPhotos={setPhotos} />
        </Card>

        {/* Wyniki analizy AI */}
        {analysis && (
          <Card title="Wyniki weryfikacji AI">
            <VerificationResultsCard analysis={analysis} />
          </Card>
        )}

        <Card title="Dane zgłoszenia">
          <div className="space-y-4">
            <label>
              <span className="mb-1 block text-xs font-semibold text-appBlack">
                Temat sprawy technicznej
              </span>

              <input
                placeholder="np. Przeciek w zastawce wodnej"
                value={formData.title}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, title: e.target.value }))
                }
                maxLength={100}
                className="w-full rounded-2xl border border-neutralGray/60 bg-white px-3 py-3 text-sm outline-none focus:border-primaryDark focus:ring-1 focus:ring-primaryDark/30"
              />

              <p className="mt-1 text-xs text-darkGray">
                {formData.title.length}/100 znaków
              </p>
            </label>
          </div>
        </Card>

        <div className="flex flex-wrap justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack hover:bg-backgroundLight"
          >
            Anuluj
          </button>

          <button className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack hover:bg-backgroundLight">
            Zapisz jako szkic
          </button>

          <button
            type="button"
            onClick={handleSendToAi}
            disabled={!formData.title || photos.length === 0 || isAnalyzing}
            className="inline-flex items-center gap-2 rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50 hover:bg-primaryDark/90"
          >
            <Sparkles size={17} />
            {isAnalyzing ? "Analizuję..." : "Wyślij do analizy AI"}
          </button>
        </div>
      </div>
    </aside>
  );
}