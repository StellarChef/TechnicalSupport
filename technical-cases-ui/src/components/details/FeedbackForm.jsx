
import Card from "../shared/Card";
import SelectFilter from "../dashboard/SelectFilter";

export default function FeedbackForm() {
  return (
    <Card title="Feedback użytkownika">
      <div className="grid gap-3 md:grid-cols-2">
        <SelectFilter
          label="Czy wynik AI był pomocny?"
          value=""
          onChange={() => {}}
          options={[
            ["", "Wybierz"],
            ["yes", "Tak"],
            ["partially", "Częściowo"],
            ["no", "Nie"],
          ]}
        />

        <SelectFilter
          label="Ocena"
          value=""
          onChange={() => {}}
          options={[
            ["", "Wybierz"],
            ["1", "1"],
            ["2", "2"],
            ["3", "3"],
            ["4", "4"],
            ["5", "5"],
          ]}
        />

        <label className="md:col-span-2">
          <span className="mb-1 block text-xs font-semibold text-appBlack">
            Komentarz
          </span>

          <textarea
            placeholder="Dodaj komentarz..."
            className="min-h-24 w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight px-3 py-3 text-sm outline-none"
          />
        </label>
      </div>

      <button className="mt-4 rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white">
        Zapisz feedback
      </button>
    </Card>
  );
}
