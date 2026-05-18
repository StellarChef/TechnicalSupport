import { useState } from "react";
import { X, Sparkles } from "lucide-react";
import Card from "../shared/Card";
import PhotoUploader from "./PhotoUploader";
import { createCase, uploadPhoto } from "../../api/cases";

export default function NewCaseDrawer({ open, onClose, onCaseCreated }) {
  const [photos, setPhotos] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({ title: "" });

  if (!open) return null;

  const resetForm = () => {
    setPhotos([]);
    setFormData({ title: "" });
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async () => {
    if (!formData.title || isSubmitting) return;

    setIsSubmitting(true);
    setError(null);

    try {
      // 1. Najpierw wgraj wszystkie pliki do backendu, zbierz URL-e.
      //    Promise.all → uploady lecą równolegle (szybciej niż sekwencyjnie).
      const uploadedUrls = await Promise.all(
        photos.map((photo) => uploadPhoto(photo.file).then((res) => res.url))
      );

      // 2. Utwórz case z URL-ami zdjęć — pipeline AI dostanie do analizy.
      const newCase = await createCase({
        title: formData.title,
        photos: uploadedUrls,
        damageDescription: "",
      });

      onCaseCreated?.(newCase);
      resetForm();
    } catch (err) {
      console.error("Błąd tworzenia sprawy:", err);
      setError(err.message || "Nie udało się utworzyć sprawy.");
    } finally {
      setIsSubmitting(false);
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
          onClick={handleClose}
          className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-white text-appBlack shadow-card"
        >
          <X size={18} />
        </button>
      </div>

      <div className="space-y-5 p-6">
        <Card title="Dodaj zdjęcia do analizy">
          <PhotoUploader photos={photos} setPhotos={setPhotos} />
          <p className="mt-3 text-xs text-darkGray">
            Zdjęcia zostaną wgrane do backendu i przekazane do analizy AI.
          </p>
        </Card>

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

        {error && (
          <div className="rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-800">
            {error}
          </div>
        )}

        <div className="flex flex-wrap justify-end gap-3">
          <button
            onClick={handleClose}
            className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack hover:bg-backgroundLight"
          >
            Anuluj
          </button>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!formData.title || isSubmitting}
            className="inline-flex items-center gap-2 rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50 hover:bg-primaryDark/90"
          >
            <Sparkles size={17} />
            {isSubmitting ? "Tworzę sprawę..." : "Utwórz sprawę (AI)"}
          </button>
        </div>
      </div>
    </aside>
  );
}
