
import { Plus, User } from "lucide-react";

export default function TopNavigation({
  onNewCase,
  lowAiCount,
  openCount,
  onFilterLowAi,
}) {
  return (
    <header className="sticky top-0 z-30 border-b border-neutralGray/40 bg-backgroundLight/90 backdrop-blur">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-appBlack">
            Zgłoszenia techniczne
          </h1>
          <p className="mt-1 text-sm text-darkGray">
            Otwarte sprawy:{" "}
            <strong className="text-appBlack">{openCount}</strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onFilterLowAi}
            className="rounded-full border border-neutralGray bg-white px-4 py-2 text-sm font-semibold text-appBlack hover:border-appBlack"
          >
            AI do korekty: {lowAiCount}
          </button>

          <button
            onClick={onNewCase}
            className="inline-flex items-center gap-2 rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white shadow-card hover:opacity-90"
          >
            <Plus size={18} />
            Nowe zgłoszenie
          </button>

          <button className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-white text-appBlack shadow-card">
            <User size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}
