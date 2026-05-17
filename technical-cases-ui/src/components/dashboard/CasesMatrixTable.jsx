import { Eye, Mail } from "lucide-react";

import { formatDate } from "../../utils/formatters";

import ApprovalBadge from "../badges/ApprovalBadge";
import ConfidenceBadge from "../badges/ConfidenceBadge";
import ResponsibilityBadge from "../badges/ResponsibilityBadge";


export default function CasesMatrixTable({
  cases,
  selectedIds,
  setSelectedIds,
  onOpenCase,
}) {
  const allSelected = cases.length > 0 && selectedIds.length === cases.length;

  const toggleAll = () => {
    if (allSelected) setSelectedIds([]);
    else setSelectedIds(cases.map((item) => item.id));
  };

  const toggleOne = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id)
        ? prev.filter((item) => item !== id)
        : [...prev, id]
    );
  };

  return (
    <section className="overflow-hidden rounded-app bg-white shadow-card">
      {selectedIds.length > 0 && (
        <div className="flex items-center justify-between border-b border-neutralGray/40 bg-backgroundLight px-5 py-3">
          <p className="text-sm font-semibold text-appBlack">
            Zaznaczono: {selectedIds.length}
          </p>

          <div className="flex gap-2">
            <button className="rounded-full bg-primaryDark px-4 py-2 text-xs font-semibold text-white">
              Akcje masowe
            </button>

            <button
              onClick={() => setSelectedIds([])}
              className="rounded-full border border-neutralGray px-4 py-2 text-xs font-semibold text-appBlack"
            >
              Odznacz
            </button>
          </div>
        </div>
      )}

      <div className="max-h-[560px] overflow-auto">
        <table className="w-full min-w-[1250px] border-collapse text-left">
          <thead className="sticky top-0 z-10 bg-white">
            <tr className="border-b border-neutralGray/50 text-xs uppercase tracking-wide text-darkGray">
              <th className="w-12 px-5 py-4">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleAll}
                />
              </th>
              <th className="px-4 py-4">ID</th>
              <th className="px-4 py-4">Data</th>
              <th className="px-4 py-4">Temat</th>
              <th className="px-4 py-4">Kategoria AI</th>
              <th className="px-4 py-4">Typ</th>
              <th className="px-4 py-4">Zatwierdzenie</th>
              <th className="px-4 py-4">Koszt po stronie</th>
              <th className="px-4 py-4">Robocizna</th>
              <th className="px-4 py-4">Materiał</th>
              <th className="px-4 py-4">Suma</th>
              <th className="px-4 py-4">AI</th>
              <th className="px-4 py-4">Mail</th>
              <th className="px-4 py-4">Akcje</th>
            </tr>
          </thead>

          <tbody>
            {cases.map((item) => {
              const isLowAi = item.aiClassification.confidence < 0.7;

              return (
                <tr
                  key={item.id}
                  onClick={() => onOpenCase(item)}
                  className={`cursor-pointer border-b border-neutralGray/30 transition hover:bg-backgroundLight ${
                    isLowAi ? "bg-backgroundLight/60" : ""
                  }`}
                >
                  <td
                    className="px-5 py-4"
                    onClick={(event) => event.stopPropagation()}
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(item.id)}
                      onChange={() => toggleOne(item.id)}
                    />
                  </td>

                  <td className="px-4 py-4 text-sm font-bold text-appBlack">
                    {item.id}
                  </td>

                  <td className="px-4 py-4 text-sm text-darkGray">
                    {formatDate(item.createdAt)}
                  </td>

                  <td className="max-w-[260px] px-4 py-4">
                    <p className="font-semibold text-appBlack">{item.title}</p>
                    <p className="mt-1 line-clamp-1 text-xs text-darkGray">
                      {item.damageDescription}
                    </p>
                  </td>

                  <td className="px-4 py-4 text-sm text-appBlack">
                    {item.aiClassification.category}
                  </td>

                  <td className="px-4 py-4 text-sm text-darkGray">
                    {item.aiClassification.damageType}
                  </td>

                  <td className="px-4 py-4">
                    <ApprovalBadge approved={item.approved} />
                  </td>

                  <td className="px-4 py-4">
                    <ResponsibilityBadge value={item.responsibility} />
                  </td>

                  <td className="px-4 py-4 text-sm text-appBlack">
                    {item.cost.labor} {item.cost.currency}
                  </td>

                  <td className="px-4 py-4 text-sm text-appBlack">
                    {item.cost.materials} {item.cost.currency}
                  </td>

                  <td className="px-4 py-4 text-sm font-bold text-appBlack">
                    {item.cost.total} {item.cost.currency}
                  </td>

                  <td className="px-4 py-4">
                    <ConfidenceBadge value={item.aiClassification.confidence} />
                  </td>

                  <td className="px-4 py-4">
                    {item.mail.shouldGenerate ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-backgroundLight px-3 py-1 text-xs font-semibold text-appBlack">
                        <Mail size={13} />
                        Szkic
                      </span>
                    ) : (
                      <span className="text-xs text-darkGray">Nie wymagany</span>
                    )}
                  </td>

                  <td className="px-4 py-4">
                    <button className="inline-flex items-center gap-1 rounded-full border border-neutralGray px-3 py-1.5 text-xs font-semibold text-appBlack">
                      <Eye size={14} />
                      Podgląd
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
