import { useEffect, useMemo, useState } from "react";

import { fetchCases } from "./api/cases";
import TopNavigation from "./components/layout/TopNavigation";
import KpiCards from "./components/dashboard/KpiCards";
import CasesFilters from "./components/dashboard/CasesFilters";
import CasesMatrixTable from "./components/dashboard/CasesMatrixTable";
import CaseDetailsDrawer from "./components/details/CaseDetailsDrawer";
import NewCaseDrawer from "./components/forms/NewCaseDrawer";
import MailPreviewModal from "./components/mail/MailPreviewModal";

const EMPTY_FILTERS = {
  query: "",
  approval: "all",
  responsibility: "all",
  category: "all",
  aiConfidence: "all",
};

export default function App() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const [newCaseOpen, setNewCaseOpen] = useState(false);
  const [mailCase, setMailCase] = useState(null);

  const [filters, setFilters] = useState(EMPTY_FILTERS);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchCases()
      .then((data) => {
        if (!cancelled) setCases(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Nie udało się pobrać spraw.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleCaseCreated = (newCase) => {
    setCases((prev) => [newCase, ...prev]);
    setNewCaseOpen(false);
    setSelectedCase(newCase);
  };

  const handleCaseUpdated = (updatedCase) => {
    setCases((prev) =>
      prev.map((c) => (c.id === updatedCase.id ? updatedCase : c))
    );
    // Jeśli akurat ten case jest otwarty w drawerze — odśwież widok.
    setSelectedCase((current) =>
      current && current.id === updatedCase.id ? updatedCase : current
    );
  };

  const filteredCases = useMemo(() => {
    return cases.filter((item) => {
      const query = filters.query.toLowerCase();

      const matchesQuery =
        !query ||
        item.id.toLowerCase().includes(query) ||
        item.title.toLowerCase().includes(query) ||
        (item.damageDescription || "").toLowerCase().includes(query);

      const matchesApproval =
        filters.approval === "all" ||
        (filters.approval === "approved" && item.approved) ||
        (filters.approval === "pending" && !item.approved);

      const matchesResponsibility =
        filters.responsibility === "all" ||
        item.responsibility === filters.responsibility;

      const matchesCategory =
        filters.category === "all" ||
        item.aiClassification?.category === filters.category;

      const confidence = item.aiClassification?.confidence ?? 0;
      const matchesAi =
        filters.aiConfidence === "all" ||
        (filters.aiConfidence === "low" && confidence < 0.7) ||
        (filters.aiConfidence === "high" && confidence >= 0.7);

      return (
        matchesQuery &&
        matchesApproval &&
        matchesResponsibility &&
        matchesCategory &&
        matchesAi
      );
    });
  }, [cases, filters]);

  const openCount = cases.filter((item) => !item.approved).length;

  const lowAiCount = cases.filter(
    (item) => (item.aiClassification?.confidence ?? 0) < 0.7
  ).length;

  const resetFilters = () => setFilters(EMPTY_FILTERS);

  const handleShortcut = (shortcut) => {
    if (shortcut === "all") resetFilters();
    if (shortcut === "pending")
      setFilters((prev) => ({ ...prev, approval: "pending" }));
    if (shortcut === "approved")
      setFilters((prev) => ({ ...prev, approval: "approved" }));
    if (["owner", "tenant", "unresolved"].includes(shortcut))
      setFilters((prev) => ({ ...prev, responsibility: shortcut }));
    if (shortcut === "low_ai")
      setFilters((prev) => ({ ...prev, aiConfidence: "low" }));
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
        {error && (
          <div className="rounded-app bg-white p-4 text-sm font-semibold text-red-700 shadow-card">
            Nie udało się pobrać spraw z backendu: {error}
          </div>
        )}

        <KpiCards cases={cases} onShortcut={handleShortcut} />

        <CasesFilters
          filters={filters}
          setFilters={setFilters}
          onClear={resetFilters}
        />

        {loading ? (
          <div className="rounded-app bg-white p-6 text-center text-sm text-darkGray shadow-card">
            Ładowanie spraw z bazy...
          </div>
        ) : (
          <CasesMatrixTable
            cases={filteredCases}
            selectedIds={selectedIds}
            setSelectedIds={setSelectedIds}
            onOpenCase={setSelectedCase}
          />
        )}
      </main>

      <CaseDetailsDrawer
        selectedCase={selectedCase}
        onClose={() => setSelectedCase(null)}
        onOpenMail={setMailCase}
        onCaseUpdated={handleCaseUpdated}
      />

      <NewCaseDrawer
        open={newCaseOpen}
        onClose={() => setNewCaseOpen(false)}
        onCaseCreated={handleCaseCreated}
      />

      <MailPreviewModal caseItem={mailCase} onClose={() => setMailCase(null)} />
    </div>
  );
}
