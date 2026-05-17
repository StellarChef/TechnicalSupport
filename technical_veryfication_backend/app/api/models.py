from django.db import models


class Case(models.Model):
    """Pojedyncze zgłoszenie usterki — odpowiada obiektowi `case` z frontendu."""

    class Responsibility(models.TextChoices):
        OWNER = "owner", "Właściciel"
        TENANT = "tenant", "Najemca"
        UNRESOLVED = "unresolved", "Nierozstrzygnięte"

    class MailTemplate(models.TextChoices):
        OWNER_REPAIR_NOTICE = (
            "owner_repair_notice",
            "Powiadomienie o naprawie (właściciel)",
        )
        ISSUE_VERIFICATION_REQUEST = (
            "issue_verification_request",
            "Prośba o weryfikację usterki",
        )

    # Identyfikator biznesowy, np. "CASE-2026-0001"
    case_id = models.CharField(max_length=32, unique=True, db_index=True)

    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Pipeline od razu zwraca zweryfikowany case; koordynator tylko zatwierdza,
    # że sprawa jest zakończona (i ew. wprowadza korekty klasyfikacji AI).
    approved = models.BooleanField(default=False)

    damage_description = models.TextField(blank=True)
    repair_description = models.TextField(blank=True)

    # Klasyfikacja AI (aiClassification)
    ai_category = models.CharField(max_length=120, blank=True)
    ai_damage_type = models.CharField(max_length=120, blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)  # 0.0 - 1.0
    ai_suggested_responsibility = models.CharField(
        max_length=16, choices=Responsibility.choices, blank=True
    )
    ai_suggested_repair = models.TextField(blank=True)
    ai_suggested_labor_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    ai_suggested_material_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Decyzja koordynatora (responsibility)
    responsibility = models.CharField(
        max_length=16, choices=Responsibility.choices, default=Responsibility.UNRESOLVED
    )

    # Koszty (cost)
    cost_labor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_materials = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_currency = models.CharField(max_length=8, default="PLN")

    # Mail (mail) — generujemy tylko draft, wysyłka jest poza tym systemem
    mail_should_generate = models.BooleanField(default=False)
    mail_template = models.CharField(
        max_length=40, choices=MailTemplate.choices, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.case_id} — {self.title}"

    @property
    def cost_total(self):
        return (self.cost_labor or 0) + (self.cost_materials or 0)


class CasePhoto(models.Model):
    """Zdjęcie powiązane ze zgłoszeniem (photos[])."""

    case = models.ForeignKey(Case, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="cases/%Y/%m/", null=True, blank=True)
    url = models.URLField(blank=True)  # alternatywnie zewnętrzny URL
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main", "uploaded_at"]

    def __str__(self):
        return f"Photo #{self.pk} ({self.case.case_id})"


class CaseHistoryEvent(models.Model):
    """Wpis na osi czasu zgłoszenia (history[])."""

    case = models.ForeignKey(Case, related_name="history", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=40)  # created, ai_classified, closed, ...
    label = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=120)  # "Maciej", "AI", "System"

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.event_type} @ {self.case.case_id}"
