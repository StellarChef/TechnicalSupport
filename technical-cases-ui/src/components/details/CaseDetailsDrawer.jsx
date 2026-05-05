
import { X } from "lucide-react";
import { formatDate } from "../../utils/formatters.js";

import Card from "../shared/Card";
import Info from "../shared/Info";
import StatusBadge from "../badges/StatusBadge";
import ResponsibilityBadge from "../badges/ResponsibilityBadge";

import CasePhotoPreview from "./CasePhotoPreview";
import CostBreakdownCard from "./CostBreakdownCard";
import AiClassificationCard from "./AiClassificationCard";
import AiCorrectionForm from "./AiCorrectionForm";
import MailPanel from "./MailPanel";
import FeedbackForm from "./FeedbackForm";
import CaseHistoryTimeline from "./CaseHistoryTimeline";

export default function CaseDetailsDrawer({
  selectedCase,
  onClose,
  onOpenMail,
}) {
  if (!selectedCase) return null;

  return (
    <aside className="fixed inset-y-0 right-0 z-40 w-full max-w-5xl overflow-y-auto border-l border-neutralGray/50 bg-backgroundLight shadow-2xl">
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-neutralGray/40 bg-backgroundLight/95 px-6 py-4 backdrop-blur">
        <div>
          <p className="text-sm font-semibold text-darkGray">
            {selectedCase.id}
          </p>
          <h2 className="text-xl font-bold text-appBlack">
            {selectedCase.title}
          </h2>
        </div>

        <button
          onClick={onClose}
          className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-white text-appBlack shadow-card"
        >
          <X size={18} />
        </button>
      </div>

      <div className="grid gap-5 p-6 lg:grid-cols-[380px_1fr]">
        <div className="space-y-5">
          <CasePhotoPreview photos={selectedCase.photos} />

          <CostBreakdownCard cost={selectedCase.cost} />

          <CaseHistoryTimeline history={selectedCase.history} />
        </div>

        <div className="space-y-5">
          <Card title="Dane sprawy">
            <div className="grid gap-3 md:grid-cols-3">
              <Info
                label="Status"
                value={<StatusBadge status={selectedCase.status} />}
              />

              <Info
                label="Koszt po stronie"
                value={
                  <ResponsibilityBadge value={selectedCase.responsibility} />
                }
              />

              <Info
                label="Utworzono"
                value={formatDate(selectedCase.createdAt)}
              />
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <Info
                label="Co jest uszkodzone"
                value={selectedCase.damageDescription}
              />

              <Info
                label="Co należy naprawić"
                value={selectedCase.repairDescription}
              />
            </div>
          </Card>

          <AiClassificationCard selectedCase={selectedCase} />

          <AiCorrectionForm selectedCase={selectedCase} />

          <MailPanel selectedCase={selectedCase} onOpenMail={onOpenMail} />

          <FeedbackForm />
        </div>
      </div>
    </aside>
  );
}
