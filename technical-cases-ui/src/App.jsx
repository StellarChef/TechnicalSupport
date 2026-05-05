import { useMemo, useState } from "react";
import { initialCases } from "./data/cases";

import TopNavigation from "./components/layout/TopNavigation";
import KpiCards from "./components/dashboard/KpiCards";
import CasesFilters from "./components/dashboard/CasesFilters";
import CasesMatrixTable from "./components/dashboard/CasesMatrixTable";
import CaseDetailsDrawer from "./components/details/CaseDetailsDrawer";
import NewCaseDrawer from "./components/forms/NewCaseDrawer";
import MailPreviewModal from "./components/mail/MailPreviewModal";

export default function App() {
  const [cases] = useState(initialCases);
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const [newCaseOpen, setNewCaseOpen] = useState(false);
  const [mailCase, setMailCase] = useState(null);

  const [filters, setFilters] = useState({
    query: "",
    status: "all",
    responsibility: "all",
    category: "all",
    aiConfidence: "all",
  });

  const filteredCases = useMemo(() => {
    return cases.filter((item) => {
      const query = filters.query.toLowerCase();

      const matchesQuery =
        !query ||
        item.id.toLowerCase().includes(query) ||
        item.title.toLowerCase().includes(query) ||
        item.damageDescription.toLowerCase().includes(query);

      const matchesStatus =
        filters.status === "all" || item.status === filters.status;

      const matchesResponsibility =
        filters.responsibility === "all" ||
        item.responsibility === filters.responsibility;

      const matchesCategory =
        filters.category === "all" ||
        item.aiClassification.category === filters.category;

      const matchesAi =
        filters.aiConfidence === "all" ||
        (filters.aiConfidence === "low" &&
          item.aiClassification.confidence < 0.7) ||
        (filters.aiConfidence === "high" &&
          item.aiClassification.confidence >= 0.7);

      return (
        matchesQuery &&
        matchesStatus &&
        matchesResponsibility &&
        matchesCategory &&
        matchesAi
      );
    });
  }, [cases, filters]);

  const openCount = cases.filter((item) => item.status !== "closed").length;

  const lowAiCount = cases.filter(
    (item) => item.aiClassification.confidence < 0.7
  ).length;

  const resetFilters = () => {
    setFilters({
      query: "",
      status: "all",
      responsibility: "all",
      category: "all",
      aiConfidence: "all",
    });
  };

  const handleShortcut = (shortcut) => {
    if (shortcut === "all") resetFilters();

    if (shortcut === "ai_review") {
      setFilters((prev) => ({ ...prev, status: "ai_review" }));
    }

    if (["owner", "tenant", "unresolved"].includes(shortcut)) {
      setFilters((prev) => ({ ...prev, responsibility: shortcut }));
    }

    if (shortcut === "low_ai") {
      setFilters((prev) => ({ ...prev, aiConfidence: "low" }));
    }

    if (shortcut === "closed") {
      setFilters((prev) => ({ ...prev, status: "closed" }));
    }
  };

  return (
    <div className="min-h-screen bg-backgroundLight text-appBlack">
      <TopNavigation
        onNewCase={() => setNewCaseOpen(true)}
        lowAiCount={lowAiCount}
        openCount={openCount}
        onFilterLowAi={() =>
          setFilters((prev) => ({ ...prev, aiConfidence: "low" }))
        }
      />

      <main className="mx-auto max-w-[1600px] space-y-5 px-6 py-6">
        <KpiCards cases={cases} onShortcut={handleShortcut} />

        <CasesFilters
          filters={filters}
          setFilters={setFilters}
          onClear={resetFilters}
        />

        <CasesMatrixTable
          cases={filteredCases}
          selectedIds={selectedIds}
          setSelectedIds={setSelectedIds}
          onOpenCase={setSelectedCase}
        />
      </main>

      <CaseDetailsDrawer
        selectedCase={selectedCase}
        onClose={() => setSelectedCase(null)}
        onOpenMail={setMailCase}
      />

      <NewCaseDrawer open={newCaseOpen} onClose={() => setNewCaseOpen(false)} />

      <MailPreviewModal caseItem={mailCase} onClose={() => setMailCase(null)} />
    </div>
  );
}
