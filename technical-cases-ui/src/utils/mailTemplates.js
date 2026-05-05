export function buildMailPreview(caseItem) {
  const isOwner = caseItem.responsibility === "owner";

  const subject = isOwner
    ? `Zgłoszenie usterki wymagającej naprawy — ${caseItem.title}`
    : `Weryfikacja usterki i odpowiedzialności za naprawę — ${caseItem.title}`;

  const body = isOwner
    ? `Dzień dobry,

zgłoszono usterkę dotyczącą lokalu.

Temat sprawy:
${caseItem.title}

Opis uszkodzenia:
${caseItem.damageDescription}

Rekomendowany sposób naprawy:
${caseItem.repairDescription}

Szacowany koszt:
- Robocizna: ${caseItem.cost.labor} ${caseItem.cost.currency}
- Materiały: ${caseItem.cost.materials} ${caseItem.cost.currency}
- Suma: ${caseItem.cost.total} ${caseItem.cost.currency}

Na podstawie klasyfikacji zgłoszenia koszt naprawy został przypisany po stronie właściciela.

Prosimy o akceptację dalszych działań lub informację zwrotną.

Pozdrawiam,
Maciej`
    : `Dzień dobry,

zgłoszenie wymaga dodatkowej weryfikacji przed przypisaniem odpowiedzialności kosztowej.

Temat sprawy:
${caseItem.title}

Opis uszkodzenia:
${caseItem.damageDescription}

Proponowany sposób naprawy:
${caseItem.repairDescription}

Wstępny koszt:
- Robocizna: ${caseItem.cost.labor} ${caseItem.cost.currency}
- Materiały: ${caseItem.cost.materials} ${caseItem.cost.currency}
- Suma: ${caseItem.cost.total} ${caseItem.cost.currency}

Prosimy o weryfikację:
1. Czy usterka powstała w wyniku normalnego zużycia?
2. Czy naprawa powinna być po stronie właściciela czy najemcy?
3. Czy wskazany sposób naprawy jest właściwy?

Pozdrawiam,
Maciej`;

  return { subject, body };
}