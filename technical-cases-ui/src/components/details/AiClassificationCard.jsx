
import { CheckCircle2, Pencil } from "lucide-react";
import Card from "../shared/Card";
import Info from "../shared/Info";
import ConfidenceBadge from "../badges/ConfidenceBadge";
import ResponsibilityBadge from "../badges/ResponsibilityBadge";

export default function AiClassificationCard({ selectedCase }) {
  const ai = selectedCase.aiClassification;

  return (
    <Card title="Klasyfikacja AI">
      <div className="grid gap-3 md:grid-cols-2">
        <Info label="Kategoria" value={ai.category} />
        <Info label="Typ uszkodzenia" value={ai.damageType} />

        <Info
          label="Sugerowana odpowiedzialność"
          value={<ResponsibilityBadge value={ai.suggestedResponsibility} />}
        />

        <Info
          label="Pewność AI"
          value={<ConfidenceBadge value={ai.confidence} />}
        />
      </div>

      <div className="mt-4 rounded-2xl bg-backgroundLight p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-darkGray">
          Rekomendacja
        </p>
        <p className="mt-1 text-sm font-semibold text-appBlack">
          {ai.suggestedRepair}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button className="inline-flex items-center gap-2 rounded-full bg-primaryDark px-4 py-2.5 text-sm font-semibold text-white">
          <CheckCircle2 size={17} />
          Zaakceptuj
        </button>

        <button className="inline-flex items-center gap-2 rounded-full border border-neutralGray px-4 py-2.5 text-sm font-semibold text-appBlack">
          <Pencil size={17} />
          Popraw AI
        </button>
      </div>
    </Card>
  );
}
