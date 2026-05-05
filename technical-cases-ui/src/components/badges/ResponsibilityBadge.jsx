import { responsibilityLabels } from "../../data/cases";

export default function ResponsibilityBadge({ value }) {
  const variants = {
    owner: "bg-primaryDark text-white",
    tenant: "bg-neutralGray/20 text-appBlack border border-neutralGray",
    unresolved: "bg-white text-appBlack border border-dashed border-neutralGray",
  };

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${variants[value]}`}
    >
      {responsibilityLabels[value]}
    </span>
  );
}


