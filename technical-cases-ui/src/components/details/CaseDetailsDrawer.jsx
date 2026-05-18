import { useState } from "react";
import { X, Check, RefreshCw, Sparkles } from "lucide-react";
import { formatDate } from "../../utils/formatters.js";
import { approveCase, reverifyCase } from "../../api/cases";

import Card from "../shared/Card";
import Info from "../shared/Info";
import ApprovalBadge from "../badges/ApprovalBadge";
import ResponsibilityBadge from "../badges/ResponsibilityBadge";

import CasePhotoPreview from "./CasePhotoPreview";
import CostBreakdownCard from "./CostBreakdownCard";
import AiClassificationCard from "./AiClassificationCard";
import AiCorrectionForm from "./AiCorrectionForm";
import MailPanel from "./MailPanel";
import CaseHistoryTimeline from "./CaseHistoryTimeline";

export default function CaseDetailsDrawer({
  selectedCase,
  onClose,
  onOpenMail,
  onCaseUpdated,
}) {
  const [busy, setBusy] = useState(null); // "approve" | "reverify" | null
  const [error, setError] = useState(null);
  const [reverifyOpen, setReverifyOpen] = useState(false);
  const [reverifyText, setReverifyText] = useState("");

  if (!selectedCase) return null;

  const handleApprove = async () => {
    if (selectedCase.approved || busy) return;
    setBusy("approve");
    setError(null);
    try {
      const updated = await approveCase(selectedCase.id);
      onCaseUpdated?.(updated);
    } catch (err) {
      console.error("Błąd zatwierdzania:", err);
      setError(err.message || "Nie udało się zatwierdzić sprawy.");
    } finally {
      setBusy(null);
    }
  };

  const handleReverify = async () => {
    const info = reverifyText.trim();
    if (!info || busy) return;
    setBusy("reverify");
    setError(null);
    try {
      const updated = await reverifyCase(selectedCase.id, info);
      onCaseUpdated?.(updated);
      setReverifyText("");
      setReverifyOpen(false);
    } catch (err) {
      console.error("Błąd ponownej weryfikacji:", err);
      setError(err.message || "Nie udało się uruchomić ponownej weryfikacji.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <aside className="fixed inset-y-0 right-0 z-40 w-full max-w-5xl overflow-y-auto border-l border-neutralGray/50 bg-backgroundLight shadow-2xl">
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-neutralGray/40 bg-backgroundLight/95 px-6 py-4 backdrop-blur">
        <div>
          <p className="text-sm font-semibold text-darkGray">
            {selectedCase.id}
          </p>
          <h2 className="text-xl font-bold text-appBlack">
            {selectedCase.title}
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setReverifyOpen((v) => !v)}
            disabled={busy === "reverify"}
            className="inline-flex items-center gap-2 rounded-full border border-neutralGray bg-white px-5 py-2.5 text-sm font-semibold text-appBlack hover:border-appBlack disabled:opacity-50"
          >
            <RefreshCw size={16} />
            Ponowna weryfikacja
          </button>

          <button
            onClick={handleApprove}
            disabled={selectedCase.approved || busy === "approve"}
            className={`inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold disabled:opacity-50 ${
              selectedCase.approved
                ? "border border-neutralGray text-appBlack"
                : "bg-primaryDark text-white"
            }`}
          >
            <Check size={17} />
            {selectedCase.approved
              ? "Zatwierdzone"
              : busy === "approve"
              ? "Zatwierdzam..."
              : "Zatwierdź sprawę"}
          </button>

          <button
            onClick={onClose}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-white text-appBlack shadow-card"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {error && (
        <div className="mx-6 mt-4 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-800">
          {error}
        </div>
      )}

      {reverifyOpen && (
        <div className="mx-6 mt-4 rounded-app bg-white p-5 shadow-card">
          <div className="mb-3 flex items-center gap-2 text-appBlack">
            <Sparkles size={17} />
            <h3 className="text-sm font-bold">
              Dodatkowa informacja do ponownej weryfikacji AI
            </h3>
          </div>
          <p className="mb-3 text-xs text-darkGray">
            AI uruchomi pipeline ponownie z tym kontekstem + zatwierdzonymi
            sprawami z bazy wiedzy. Wynik nadpisze klasyfikację i koszt.
          </p>
          <textarea
            value={reverifyText}
            onChange={(e) => setReverifyText(e.target.value)}
            placeholder="np. Technik na miejscu stwierdził, że uszczelka jest popękana — to nie wymiana, tylko serwis."
            className="min-h-24 w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3 py-3 text-sm outline-none focus:border-primaryDark"
          />
          <div className="mt-3 flex justify-end gap-2">
            <button
              onClick={() => {
                setReverifyOpen(false);
                setReverifyText("");
              }}
              className="rounded-full border border-neutralGray px-4 py-2 text-xs font-semibold text-appBlack"
            >
              Anuluj
            </button>
            <button
              onClick={handleReverify}
              disabled={!reverifyText.trim() || busy === "reverify"}
              className="inline-flex items-center gap-2 rounded-full bg-primaryDark px-4 py-2 text-xs font-semibold text-white disabled:opacity-50"
            >
              <RefreshCw size={14} />
              {busy === "reverify" ? "Analizuję..." : "Uruchom ponownie AI"}
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-5 p-6 lg:grid-cols-[380px_1fr]">
        <div className="space-y-5">
          <CasePhotoPreview photos={selectedCase.photos} />

          <CostBreakdownCard cost={selectedCase.cost} />

          <CaseHistoryTimeline history={selectedCase.history} />
        </div>

        <div className="space-y-5">
          <Card title="Dane sprawy">
            <div className="grid gap-3 md:grid-cols-2">
              <Info
                label="Zatwierdzenie"
                value={<ApprovalBadge approved={selectedCase.approved} />}
              />

              <Info
                label="Koszt po stronie"
                value={
                  <ResponsibilityBadge value={selectedCase.responsibility} />
                }
              />

              <Info
                label="Utworzono"
                value={formatDate(selectedCase.createdAt)}
              />
            </div>
          </Card>

          <Card title="Opis usterki">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl bg-backgroundLight p-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-darkGray">
                  Co zostało uszkodzone
                </p>
                <p className="text-sm leading-relaxed text-appBlack">
                  {selectedCase.damageDescription}
                </p>
              </div>

              <div className="rounded-2xl bg-backgroundLight p-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-darkGray">
                  Jak to naprawić
                </p>
                <p className="text-sm leading-relaxed text-appBlack">
                  {selectedCase.repairDescription}
                </p>
              </div>
            </div>
          </Card>

          <AiClassificationCard selectedCase={selectedCase} />

          <AiCorrectionForm
            selectedCase={selectedCase}
            onCaseUpdated={onCaseUpdated}
          />

          <MailPanel selectedCase={selectedCase} onOpenMail={onOpenMail} />
        </div>
      </div>
    </aside>
  );
}
