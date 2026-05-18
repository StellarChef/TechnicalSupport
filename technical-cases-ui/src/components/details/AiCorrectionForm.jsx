import { useEffect, useState } from "react";
import Card from "../shared/Card";
import SelectFilter from "../dashboard/SelectFilter";
import { responsibilityLabels } from "../../data/cases";
import { correctCase } from "../../api/cases";

export default function AiCorrectionForm({ selectedCase, onCaseUpdated }) {
  const ai = selectedCase.aiClassification || {};

  // Lokalne wartości pól. Sync z `selectedCase` przy zmianie sprawy.
  const [category, setCategory] = useState(ai.category || "");
  const [damageType, setDamageType] = useState(ai.damageType || "");
  const [responsibility, setResponsibility] = useState(
    selectedCase.responsibility || "unresolved"
  );
  const [laborCost, setLaborCost] = useState(selectedCase.cost?.labor ?? 0);
  const [materialCost, setMaterialCost] = useState(
    selectedCase.cost?.materials ?? 0
  );
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setCategory(ai.category || "");
    setDamageType(ai.damageType || "");
    setResponsibility(selectedCase.responsibility || "unresolved");
    setLaborCost(selectedCase.cost?.labor ?? 0);
    setMaterialCost(selectedCase.cost?.materials ?? 0);
    setComment("");
    setError(null);
  }, [
    selectedCase.id,
    ai.category,
    ai.damageType,
    selectedCase.responsibility,
    selectedCase.cost?.labor,
    selectedCase.cost?.materials,
  ]);

  const submit = async (overrides = {}) => {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      // Wysyłamy tylko zmienione pola — backend ma update_fields.
      const payload = {
        category,
        damage_type: damageType,
        responsibility,
        labor_cost: Number(laborCost) || 0,
        material_cost: Number(materialCost) || 0,
        comment,
        ...overrides,
      };
      const updated = await correctCase(selectedCase.id, payload);
      onCaseUpdated?.(updated);
    } catch (err) {
      console.error("Błąd zapisu korekty:", err);
      setError(err.message || "Nie udało się zapisać korekty.");
    } finally {
      setBusy(false);
    }
  };

  const handleReject = () => {
    // "Odrzuć klasyfikację AI" = ustaw responsibility na unresolved + nota.
    submit({
      responsibility: "unresolved",
      comment:
        comment.trim() ||
        "Klasyfikacja AI odrzucona — sprawa wraca do weryfikacji.",
    });
  };

  return (
    <Card title="Korekta wyniku AI">
      <div className="mb-4 rounded-2xl border border-neutralGray/50 bg-backgroundLight p-4">
        <p className="text-sm font-semibold text-appBlack">
          Oryginalny wynik AI: {ai.category || "—"},{" "}
          {responsibilityLabels[ai.suggestedResponsibility] || "—"}
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <Input label="Kategoria" value={category} onChange={setCategory} />
        <Input
          label="Typ uszkodzenia"
          value={damageType}
          onChange={setDamageType}
        />

        <SelectFilter
          label="Odpowiedzialność kosztowa"
          value={responsibility}
          onChange={setResponsibility}
          options={[
            ["owner", "Właściciel"],
            ["tenant", "Najemca"],
            ["unresolved", "Nierozstrzygnięte"],
          ]}
        />

        <Input
          label="Koszt robocizny"
          value={laborCost}
          onChange={setLaborCost}
          type="number"
        />
        <Input
          label="Koszt materiałów"
          value={materialCost}
          onChange={setMaterialCost}
          type="number"
        />

        <label className="md:col-span-2">
          <span className="mb-1 block text-xs font-semibold text-appBlack">
            Komentarz do korekty
          </span>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Wymagany przy zmianie odpowiedzialności kosztowej..."
            className="min-h-24 w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3 py-3 text-sm outline-none"
          />
        </label>
      </div>

      {error && (
        <div className="mt-3 rounded-2xl bg-red-50 p-3 text-sm font-semibold text-red-800">
          {error}
        </div>
      )}

      <div className="mt-4 flex gap-3">
        <button
          onClick={() => submit()}
          disabled={busy}
          className="rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
        >
          {busy ? "Zapisuję..." : "Zapisz korektę"}
        </button>

        <button
          onClick={handleReject}
          disabled={busy}
          className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack disabled:opacity-50"
        >
          Odrzuć klasyfikację AI
        </button>
      </div>
    </Card>
  );
}

function Input({ label, value, onChange, type = "text" }) {
  return (
    <label>
      <span className="mb-1 block text-xs font-semibold text-appBlack">
        {label}
      </span>

      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3 py-3 text-sm outline-none"
      />
    </label>
  );
}
