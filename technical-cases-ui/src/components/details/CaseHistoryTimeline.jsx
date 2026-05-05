import Card from "../shared/Card";
import { formatDate } from "../../utils/formatters.js";

export default function CaseHistoryTimeline({ history = [] }) {
  return (
    <Card title="Historia sprawy">
      <div className="space-y-4">
        {history.map((event, index) => (
          <div key={`${event.type}-${index}`} className="flex gap-3">
            <div className="mt-1 h-3 w-3 rounded-full bg-primaryDark" />

            <div>
              <p className="text-sm font-semibold text-appBlack">
                {event.label}
              </p>

              <p className="text-xs text-darkGray">
                {formatDate(event.createdAt)} · {event.createdBy}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}