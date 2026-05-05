import { statusLabels } from "../../data/cases";

export default function StatusBadge({ status }) {
  const base =
    "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold whitespace-nowrap";

  const variants = {
    ai_review: "bg-primaryDark text-white",
    correction_needed: "bg-white text-appBlack border border-appBlack",
    verification: "bg-white text-appBlack border border-neutralGray",
    closed: "bg-neutralGray/20 text-darkGray",
    approved: "bg-primaryDark text-white",
    ai_processing: "bg-white text-appBlack border border-neutralGray",
    draft: "bg-white text-darkGray border border-neutralGray",
  };

  return (
    <span
      className={`${base} ${
        variants[status] || "bg-white text-appBlack border border-neutralGray"
      }`}
    >
      {statusLabels[status] || status}
    </span>
  );
}
