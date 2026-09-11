"""Alert rules: who needs to be woken up, and when."""

from datetime import UTC, datetime

from .config import Settings
from .models import Alert, AnalysisCategory, DoorstepAnalysis


def evaluate_alert(
    analysis: DoorstepAnalysis, occurred_at: datetime | None = None, settings: Settings | None = None
) -> Alert:
    settings = settings or Settings()
    hour = occurred_at.hour if occurred_at else datetime.now(UTC).hour
    quiet_hours = hour >= settings.quiet_hours_start or hour < settings.quiet_hours_end

    if (
        analysis.category == AnalysisCategory.FALL_SUSPECTED
        and analysis.confidence >= settings.fall_confidence_threshold
    ):
        return Alert(
            level="critical",
            reason="Possible fall detected at the doorstep — call your loved one or a neighbour now.",
        )

    if (
        analysis.category == AnalysisCategory.LOITERING
        and analysis.confidence >= settings.loitering_confidence_threshold
    ):
        if quiet_hours:
            return Alert(
                level="high",
                reason="Someone is lingering at the door late at night.",
            )
        return Alert(level="none", reason="Daytime loitering below alert threshold.")

    return Alert(level="none", reason="Routine doorstep activity.")
