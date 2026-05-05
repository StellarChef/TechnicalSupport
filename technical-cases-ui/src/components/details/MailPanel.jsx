
import { Mail } from "lucide-react";
import Card from "../shared/Card";

export default function MailPanel({ selectedCase, onOpenMail }) {
  const responsibility = selectedCase.responsibility;

  if (responsibility === "tenant") {
    return (
      <Card title="Mail">
        <div className="rounded-2xl bg-backgroundLight p-4 text-sm font-semibold text-appBlack">
          Koszt po stronie najemcy — mail nie jest wymagany.
        </div>
      </Card>
    );
  }

  const label =
    responsibility === "owner"
      ? "Wygeneruj mail do właściciela"
      : "Wygeneruj mail weryfikacyjny";

  return (
    <Card title="Mail">
      <p className="mb-4 text-sm text-darkGray">
        System wygeneruje wiadomość zgodnie z odpowiedzialnością kosztową.
      </p>

      <button
        onClick={() => onOpenMail(selectedCase)}
        className="inline-flex items-center gap-2 rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white"
      >
        <Mail size={17} />
        {label}
      </button>
    </Card>
  );
}
