export default function Info({ label, value }) {
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-darkGray">
        {label}
      </p>
      <div className="text-sm font-medium text-appBlack">{value}</div>
    </div>
  );
}
