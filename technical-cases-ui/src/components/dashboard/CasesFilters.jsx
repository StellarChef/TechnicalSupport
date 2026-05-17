import {
  Search,
  SlidersHorizontal,
  Save,
  Download,
} from "lucide-react";
import SelectFilter from "./SelectFilter";

export default function CasesFilters({ filters, setFilters, onClear }) {
  return (
    <section className="rounded-app bg-white p-5 shadow-card">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-appBlack">Filtry</h2>
          <p className="text-sm text-darkGray">
            Szukaj po ID, temacie, opisie, kosztach i klasyfikacji AI.
          </p>
        </div>
        <SlidersHorizontal className="text-darkGray" size={20} />
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-6">
        <label className="xl:col-span-2">
          <span className="mb-1 block text-xs font-semibold text-appBlack">
            Wyszukiwarka
          </span>

          <div className="flex items-center gap-2 rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3">
            <Search size={17} className="text-darkGray" />
            <input
              value={filters.query}
              onChange={(event) =>
                setFilters((prev) => ({
                  ...prev,
                  query: event.target.value,
                }))
              }
              placeholder="ID, temat lub opis..."
              className="w-full bg-transparent py-3 text-sm outline-none placeholder:text-darkGray"
            />
          </div>
        </label>

        <SelectFilter
          label="Zatwierdzenie"
          value={filters.approval}
          onChange={(value) =>
            setFilters((prev) => ({ ...prev, approval: value }))
          }
          options={[
            ["all", "Wszystkie"],
            ["pending", "Do zatwierdzenia"],
            ["approved", "Zatwierdzone"],
          ]}
        />

        <SelectFilter
          label="Koszt po stronie"
          value={filters.responsibility}
          onChange={(value) =>
            setFilters((prev) => ({ ...prev, responsibility: value }))
          }
          options={[
            ["all", "Wszystkie"],
            ["owner", "Właściciel"],
            ["tenant", "Najemca"],
            ["unresolved", "Nierozstrzygnięte"],
          ]}
        />

        <SelectFilter
          label="Kategoria AI"
          value={filters.category}
          onChange={(value) =>
            setFilters((prev) => ({ ...prev, category: value }))
          }
          options={[
            ["all", "Wszystkie"],
            ["Hydraulika", "Hydraulika"],
            ["Stolarka", "Stolarka"],
          ]}
        />

        <SelectFilter
          label="Pewność AI"
          value={filters.aiConfidence}
          onChange={(value) =>
            setFilters((prev) => ({ ...prev, aiConfidence: value }))
          }
          options={[
            ["all", "Wszystkie"],
            ["low", "Niska < 70%"],
            ["high", "Wysoka ≥ 70%"],
          ]}
        />
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button className="rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white">
          Zastosuj filtry
        </button>

        <button
          onClick={onClear}
          className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack"
        >
          Wyczyść filtry
        </button>

        <button className="inline-flex items-center gap-2 rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack">
          <Save size={16} />
          Zapisz widok
        </button>

        <button className="inline-flex items-center gap-2 rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack">
          <Download size={16} />
          Eksportuj listę
        </button>
      </div>
    </section>
  );
}