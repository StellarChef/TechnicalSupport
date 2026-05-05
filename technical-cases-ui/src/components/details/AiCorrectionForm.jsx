import Card from "../shared/Card";
import SelectFilter from "../dashboard/SelectFilter";
import { responsibilityLabels } from "../../data/cases";

export default function AiCorrectionForm({ selectedCase }) {
  const ai = selectedCase.aiClassification;

  return (
    <Card title="Korekta wyniku AI">
      <div className="mb-4 rounded-2xl border border-neutralGray/50 bg-backgroundLight p-4">
        <p className="text-sm font-semibold text-appBlack">
          Oryginalny wynik AI: {ai.category},{" "}
          {responsibilityLabels[ai.suggestedResponsibility]}
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <Input label="Kategoria" defaultValue={ai.category} />
        <Input label="Typ uszkodzenia" defaultValue={ai.damageType} />

        <SelectFilter
          label="Odpowiedzialność kosztowa"
          value={selectedCase.responsibility}
          onChange={() => {}}
          options={[
            ["owner", "Właściciel"],
            ["tenant", "Najemca"],
            ["unresolved", "Nierozstrzygnięte"],
          ]}
        />

        <Input label="Koszt robocizny" defaultValue={selectedCase.cost.labor} />
        <Input
          label="Koszt materiałów"
          defaultValue={selectedCase.cost.materials}
        />

        <label className="md:col-span-2">
          <span className="mb-1 block text-xs font-semibold text-appBlack">
            Komentarz do korekty
          </span>

          <textarea
            placeholder="Wymagany przy zmianie odpowiedzialności kosztowej..."
            className="min-h-24 w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3 py-3 text-sm outline-none"
          />
        </label>
      </div>

      <div className="mt-4 flex gap-3">
        <button className="rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white">
          Zapisz korektę
        </button>

        <button className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack">
          Odrzuć klasyfikację AI
        </button>
      </div>
    </Card>
  );
}

function Input({ label, defaultValue }) {
  return (
    <label>
      <span className="mb-1 block text-xs font-semibold text-appBlack">
        {label}
      </span>

      <input
        defaultValue={defaultValue}
        className="w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3 py-3 text-sm outline-none"
      />
    </label>
  );
}