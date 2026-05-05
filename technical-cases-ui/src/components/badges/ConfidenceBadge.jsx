export default function ConfidenceBadge({ value }) {
  const confidence = value * 100;
  const isHigh = confidence >= 70;

  const variants = {
    high: "bg-green-100 text-green-800 border border-green-200",
    low: "bg-yellow-100 text-yellow-800 border border-yellow-200",
  };

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${variants[isHigh ? "high" : "low"]}`}
    >
      {confidence.toFixed(0)}%
    </span>
  );
}