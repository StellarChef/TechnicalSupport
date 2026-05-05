import { X } from "lucide-react";
import { buildMailPreview } from "../../utils/mailTemplates";

export default function MailPreviewModal({ caseItem, onClose }) {
  if (!caseItem) return null;

  const { subject, body } = buildMailPreview(caseItem);

  return (
    <div className="fixed inset-0 z-60 flex items-center justify-center bg-appBlack/50 p-4">
      <div className="w-full max-w-3xl rounded-app bg-white p-6 shadow-2xl">
        <div className="mb-5 flex items-start justify-between">
          <div>
            <p className="text-sm font-semibold text-darkGray">
              Podgląd maila
            </p>

            <h2 className="text-xl font-bold text-appBlack">{subject}</h2>
          </div>

          <button onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <textarea
          defaultValue={body}
          className="min-h-[420px] w-full rounded-2xl border border-neutralGray/60 bg-backgroundLight p-4 text-sm leading-6 outline-none"
        />

        <div className="mt-5 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-full border border-neutralGray px-5 py-2.5 text-sm font-semibold text-appBlack"
          >
            Zapisz jako draft
          </button>

          <button className="rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white">
            Wyślij mail
          </button>
        </div>
      </div>
    </div>
  );
}

