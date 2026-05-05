import { getDamageClassLabel } from "../../utils/damageAnalysis";

export default function VerificationResultsCard({ analysis }) {
  if (!analysis) return null;

  const damagePercentage = Math.round(analysis.damageClassConfidence * 100);

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border-2 border-primaryDark/20 bg-primaryDark/5 p-4">
        <p className="text-xs font-bold uppercase text-darkGray mb-2">
          Przyczyna usterki
        </p>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-lg font-bold text-appBlack">
              {getDamageClassLabel(analysis.damageClass)}
            </p>
            <p className="mt-2 text-sm text-darkGray">
              {analysis.scenario}
            </p>
            <div className="mt-3 flex items-center gap-2">
              <div className="flex-1 h-2.5 bg-neutralGray/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primaryDark to-primaryDark/70"
                  style={{ width: `${damagePercentage}%` }}
                ></div>
              </div>
              <span className="text-sm font-bold text-appBlack min-w-fit">
                {damagePercentage}% pewności
              </span>
            </div>
          </div>
        </div>
      </div>

      {analysis.detectedObjects?.length > 0 && (
        <div className="rounded-2xl border border-neutralGray/30 bg-white p-4">
          <p className="text-xs font-bold uppercase text-darkGray mb-3">
            Wykryte obiekty
          </p>
          <p className="text-sm text-darkGray">
            {analysis.detectedObjects.join(", ")}
          </p>
        </div>
      )}
    </div>
  );
}
