
export default function KpiCards({ cases, onShortcut }) {
  const stats = [
    {
      label: "Wszystkie zgłoszenia",
      value: cases.length,
      filter: "all",
    },
    {
      label: "Do weryfikacji AI",
      value: cases.filter((item) => item.status === "ai_review").length,
      filter: "ai_review",
    },
    {
      label: "Koszt po stronie właściciela",
      value: cases.filter((item) => item.responsibility === "owner").length,
      filter: "owner",
    },
    {
      label: "Koszt po stronie najemcy",
      value: cases.filter((item) => item.responsibility === "tenant").length,
      filter: "tenant",
    },
    {
      label: "Nierozstrzygnięte",
      value: cases.filter((item) => item.responsibility === "unresolved")
        .length,
      filter: "unresolved",
    },
    {
      label: "AI z niską pewnością",
      value: cases.filter((item) => item.aiClassification.confidence < 0.7)
        .length,
      filter: "low_ai",
    },
    {
      label: "Zamknięte",
      value: cases.filter((item) => item.status === "closed").length,
      filter: "closed",
    },
  ];

  return (
    <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-7">
      {stats.map((item) => (
        <button
          key={item.label}
          onClick={() => onShortcut(item.filter)}
          className="rounded-app bg-white p-5 text-left shadow-card transition hover:-translate-y-0.5 hover:shadow-lg"
        >
          <p className="text-sm font-medium text-darkGray">{item.label}</p>
          <p className="mt-3 text-3xl font-bold text-appBlack">{item.value}</p>
        </button>
      ))}
    </section>
  )}
