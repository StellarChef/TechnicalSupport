export default function ApprovalBadge({ approved }) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
        approved
          ? "bg-primaryDark text-white"
          : "bg-white text-appBlack border border-dashed border-neutralGray"
      }`}
    >
      {approved ? "Zatwierdzone" : "Do zatwierdzenia"}
    </span>
  );
}
