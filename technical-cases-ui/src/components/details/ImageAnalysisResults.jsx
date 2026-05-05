import { CheckCircle2, AlertCircle, TrendingDown } from "lucide-react";
import { getDamageTypeColor, getDamageClassLabel } from "../../utils/damageAnalysis";

export default function ImageAnalysisResults({
  analysis,
  onConfirm,
  onRetry,
  loading,
}) {
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-neutralGray/20 bg-gradient-to-r from-backgroundLight to-white p-6">
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-primaryDark border-t-transparent"></div>
            <div>
              <p className="font-semibold text-appBlack">
                Analizuję obraz...
              </p>
              <p className="text-sm text-darkGray">
                Poczekaj chwilę, przeprowadzam diagnostykę
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) return null;

  const damagePercentage = Math.round(
    analysis.damageClassConfidence * 100
  );

  return (
    <div className="space-y-4">
      {/* Główna diagnoza */}
      <div className="rounded-2xl border border-green-200 bg-green-50 p-4">
        <div className="flex gap-3">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-green-700" />
          <div>
            <p className="text-sm font-semibold text-green-900">
              Analiza ukończona z pewnością {Math.round(analysis.confidence * 100)}%
            </p>
            <p className="mt-1 text-sm text-green-800">
              {analysis.description}
            </p>
          </div>
        </div>
      </div>

      {/* Wykryte obiekty */}
      <div className="rounded-2xl border border-neutralGray/20 bg-white p-4">
        <p className="mb-3 text-xs font-bold uppercase text-darkGray">
          Wykryte obiekty
        </p>
        <div className="flex flex-wrap gap-2">
          {analysis.detectedObjects.map((obj, idx) => (
            <span
              key={idx}
              className="rounded-full bg-primaryDark/10 px-3 py-1 text-xs font-medium text-appBlack"
            >
              {obj}
            </span>
          ))}
        </div>
      </div>

      {/* Klasyfikacja uszkodzenia */}
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl border border-neutralGray/20 bg-white p-4">
            <p className="text-xs font-bold uppercase text-darkGray">
              Typ uszkodzenia
            </p>
            <p className="mt-2 text-sm font-semibold text-appBlack">
              {analysis.damageType}
            </p>
            <p className="mt-1 text-xs text-darkGray">
              Element: {analysis.damagedElement}
            </p>
          </div>

          <div className="rounded-2xl border border-neutralGray/20 bg-white p-4">
            <p className="text-xs font-bold uppercase text-darkGray">
              Powaga uszkodzenia
            </p>
            <p className="mt-2 text-sm font-semibold text-appBlack">
              {analysis.damageSeverity === "łatwe"
                ? "Lekkie"
                : analysis.damageSeverity === "średni"
                  ? "Średnie"
                  : "Poważne"}
            </p>
          </div>
        </div>
      </div>

      {/* Przyczyna */}
      <div className="rounded-2xl border border-neutralGray/20 bg-white p-4">
        <div className="flex items-start gap-3">
          <TrendingDown className="h-5 w-5 flex-shrink-0 text-darkGray" />
          <div className="flex-1">
            <p className="text-xs font-bold uppercase text-darkGray">
              Przyczyna uszkodzenia
            </p>
            <p className="mt-2 text-sm font-semibold text-appBlack">
              {getDamageClassLabel(analysis.damageClass)}
            </p>
            <p className="mt-1 text-xs text-darkGray">{analysis.scenario}</p>
            <div className="mt-3 flex items-center gap-2">
              <div className="flex-1 h-2 bg-neutralGray/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primaryDark to-primaryDark/70"
                  style={{ width: `${damagePercentage}%` }}
                ></div>
              </div>
              <span className="text-xs font-bold text-appBlack">
                {damagePercentage}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Opcje naprawy */}
      <div className="rounded-2xl border border-neutralGray/20 bg-white p-4">
        <p className="mb-3 text-xs font-bold uppercase text-darkGray">
          Opcje naprawy
        </p>
        <div className="space-y-2">
          {analysis.repairOptions.map((option, idx) => (
            <div
              key={idx}
              className={`rounded-xl border p-3 ${
                option.recommended
                  ? "border-green-300 bg-green-50"
                  : "border-neutralGray/20 bg-backgroundLight"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-bold text-appBlack">
                    {option.title}
                    {option.recommended && (
                      <span className="ml-2 inline-block rounded-full bg-green-600 px-2 py-0.5 text-xs text-white">
                        Rekomendowana
                      </span>
                    )}
                  </p>
                  <p className="mt-1 text-xs text-darkGray whitespace-pre-wrap">
                    {option.steps}
                  </p>
                  <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="font-bold text-appBlack">
                        {option.laborCost + option.materialCost} PLN
                      </span>
                      <p className="text-darkGray">Koszt całkowity</p>
                    </div>
                    <div>
                      <span className="font-bold text-appBlack">
                        {option.durability}
                      </span>
                      <p className="text-darkGray">Trwałość</p>
                    </div>
                    <div>
                      <span className="font-bold text-appBlack">
                        {option.difficulty}
                      </span>
                      <p className="text-darkGray">Trudność</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Akcje */}
      <div className="flex gap-2">
        <button
          onClick={onRetry}
          className="flex-1 rounded-full border border-neutralGray px-4 py-2.5 text-sm font-semibold text-appBlack hover:bg-backgroundLight"
        >
          Analizuj ponownie
        </button>
        <button
          onClick={onConfirm}
          className="flex-1 rounded-full bg-green-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-green-700"
        >
          Zatwierdź analizę
        </button>
      </div>
    </div>
  );
}
