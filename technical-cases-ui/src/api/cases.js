// Klient API dla operacji na case'ach. Endpointy Django:
//   GET  /api/cases/         → lista wszystkich case'ów
//   POST /api/cases/create/  → uruchom pipeline AI i zapisz nowy case

const API_BASE =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `API ${options.method || "GET"} ${path} → ${response.status}: ${body.slice(0, 200)}`
    );
  }
  return response.json();
}

export async function fetchCases() {
  return request("/cases/");
}

export async function createCase({ title, photos = [], damageDescription = "" }) {
  // Backend oczekuje `photos` jako listy URL-i. Upload plików dodamy gdy
  // pojawi się endpoint /api/upload-photo/ — na razie wysyłamy URL-e jeśli są
  // (zewnętrzne linki), albo pustą listę.
  const photoUrls = photos.filter((p) => typeof p === "string");

  const data = await request("/cases/create/", {
    method: "POST",
    body: JSON.stringify({
      title,
      photos: photoUrls,
      damage_description: damageDescription,
    }),
  });
  return data.case;
}

export async function approveCase(caseId, comment = "") {
  return request(`/cases/${caseId}/approve/`, {
    method: "POST",
    body: JSON.stringify({ comment }),
  });
}

export async function correctCase(caseId, corrections) {
  // corrections: { category?, damage_type?, responsibility?, labor_cost?,
  //                material_cost?, comment? } — wszystkie opcjonalne
  return request(`/cases/${caseId}/correct/`, {
    method: "POST",
    body: JSON.stringify(corrections),
  });
}

export async function reverifyCase(caseId, additionalInfo) {
  return request(`/cases/${caseId}/reverify/`, {
    method: "POST",
    body: JSON.stringify({ additional_info: additionalInfo }),
  });
}

export async function uploadPhoto(file) {
  const formData = new FormData();
  formData.append("file", file);

  // ⚠️ NIE ustawiamy Content-Type — przeglądarka sama doda multipart boundary.
  const response = await fetch(`${API_BASE}/upload-photo/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Upload failed: ${response.status} — ${body.slice(0, 200)}`);
  }

  return response.json(); // { photo_id, url }
}