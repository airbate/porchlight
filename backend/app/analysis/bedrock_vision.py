"""Amazon Bedrock multimodal analysis (Nova Lite via the Converse API)."""

import json
import logging
import threading

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import Settings
from ..models import AnalysisCategory, DoorstepAnalysis
from .prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_VALID = {c.value for c in AnalysisCategory if c != AnalysisCategory.UNKNOWN}

_STUB_SUMMARIES = {
    "visitor": "A visitor stopped by the front door.",
    "package_delivery": "A package was delivered to the doorstep.",
    "loitering": "Someone lingered near the front door longer than usual.",
    "fall_suspected": "Possible fall detected at the doorstep.",
    "ambient_noise": "Nothing noteworthy at the doorstep.",
    "unknown": "Doorstep activity could not be classified.",
}


class BedrockVision:
    """Classifies Ring event frames. Degrades to an offline stub so the demo
    pipeline never breaks when AWS credentials/models aren't available yet."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = None
        self._offline = False
        self._lock = threading.Lock()

    def _get_client(self):
        with self._lock:
            if self._client is None and not self._offline:
                self._client = boto3.client(
                    "bedrock-runtime", region_name=self._settings.aws_region
                )
            return self._client

    @property
    def offline(self) -> bool:
        return self._offline

    def analyze_frame(self, image: bytes | None, scenario_hint: str = "unknown") -> DoorstepAnalysis:
        if self._offline:
            return self._stub(scenario_hint)
        try:
            return self._analyze_live(image)
        except (BotoCoreError, ClientError, Exception) as exc:  # noqa: BLE001 — demo must not die
            logger.warning("Bedrock call failed, falling back to offline stub: %s", exc)
            self._offline = True
            return self._stub(scenario_hint)

    def _analyze_live(self, image: bytes | None) -> DoorstepAnalysis:
        content: list[dict] = []
        if image:
            content.append({"image": {"format": "jpeg", "source": {"bytes": image}}})
        content.append({"text": "Classify this doorstep event."})

        response = self._get_client().converse(
            modelId=self._settings.bedrock_model_id,
            messages=[{"role": "user", "content": content}],
            system=[{"text": SYSTEM_PROMPT}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 300},
        )
        raw = response["output"]["message"]["content"][0]["text"]
        parsed = self._parse_json(raw)
        category = parsed.get("category", "unknown")
        if category not in _VALID:
            category = AnalysisCategory.UNKNOWN.value
        return DoorstepAnalysis(
            category=AnalysisCategory(category),
            confidence=max(0.0, min(1.0, float(parsed.get("confidence", 0.0)))),
            summary=str(parsed.get("summary", ""))[:280] or _STUB_SUMMARIES[category],
            model=self._settings.bedrock_model_id,
            offline=False,
        )

    def summarize_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Shared Converse call for text generation (daily Care Digest)."""
        if self._offline:
            raise RuntimeError("Bedrock offline")
        response = self._get_client().converse(
            modelId=self._settings.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.4, "maxTokens": max_tokens},
        )
        return response["output"]["message"]["content"][0]["text"]

    @staticmethod
    def _parse_json(raw: str) -> dict:
        text = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _stub(scenario_hint: str) -> DoorstepAnalysis:
        category = (
            AnalysisCategory(scenario_hint) if scenario_hint in _VALID else AnalysisCategory.UNKNOWN
        )
        # Confidence 0.75 keeps the offline demo coherent: alert rules evaluate
        # the same way they will live, and the "(offline stub)" summary marks
        # the analysis as synthetic on every surface.
        return DoorstepAnalysis(
            category=category,
            confidence=0.75,
            summary=_STUB_SUMMARIES[category.value] + " (offline stub)",
            model="offline-stub",
            offline=True,
        )
