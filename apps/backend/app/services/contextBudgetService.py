"""One configurable budget for every Ollama structured generation (embeddings excluded)."""
import json
import logging
import math
import os
import re
from dataclasses import dataclass
from app.domain.common.domainError import DomainError

logger = logging.getLogger(__name__)

def positive(name, default):
    try: value = int(os.getenv(name, str(default)))
    except ValueError: value = default
    return value if value > 0 else default

@dataclass(frozen=True)
class ContextPlan:
    contextTokens: int
    outputTokens: int
    inputTokens: int
    safetyTokens: int

class ContextBudgetService:
    def __init__(self):
        self.context = positive('LIA2_OLLAMA_CONTEXT_TOKENS', 24576)
        self.output = positive('LIA2_OLLAMA_OUTPUT_RESERVE_TOKENS', 6144)
        # Total generation reserve with thinking enabled, not an additional reserve.
        self.thinkingOutput = positive('LIA2_OLLAMA_THINKING_OUTPUT_TOKENS', 8192)
        self.safety = positive('LIA2_OLLAMA_CONTEXT_SAFETY_TOKENS', 1536)
        self.vision = positive('LIA2_OLLAMA_VISION_RESERVE_TOKENS', 4096)

    @staticmethod
    def estimate(text):
        text = str(text)
        # Calibrated conservatively against the Portuguese material canary. This is
        # an estimate, not a tokenizer: byte-heavy/OCR/code fragments use a stricter bound.
        noisy = sum(len(m.group().encode('utf-8')) for m in re.finditer(r'\S{32,}', text))
        size = len(text.encode('utf-8'))
        return math.ceil((size - noisy) / 2) + noisy

    def plan(self, prompt, schema, *, thinking=False, image=False):
        output = self.thinkingOutput if thinking not in (None, False, 'off') else self.output
        overhead = self.estimate(json.dumps(schema, ensure_ascii=False)) + 256
        return ContextPlan(self.context, output, self.estimate(prompt) + overhead + (self.vision if image else 0), self.safety)

    def fits(self, prompt, schema, *, thinking=False, image=False):
        plan = self.plan(prompt, schema, thinking=thinking, image=image)
        return plan.inputTokens + plan.outputTokens + plan.safetyTokens <= plan.contextTokens

    def evidenceBudget(self, promptWithoutEvidence='', schema=None, *, thinking=False):
        plan = self.plan(promptWithoutEvidence, schema or {}, thinking=thinking)
        return max(0, plan.contextTokens - plan.outputTokens - plan.inputTokens - plan.safetyTokens)

    def generationTimeout(self, *, thinking=False):
        # Measured 7.45 output tokens/s on this server. Keep a conservative,
        # externalized floor plus prefill time for long asynchronous tasks only.
        output = self.thinkingOutput if thinking not in (None, False, 'off') else self.output
        rate = positive('LIA2_OLLAMA_LONG_TASK_MIN_TOKENS_PER_SECOND', 6)
        maximum = positive('LIA2_OLLAMA_LONG_TASK_TIMEOUT_SECONDS', 1800)
        return min(maximum, max(360, math.ceil(output / rate) + 180))

    def require(self, prompt, schema, *, thinking=False, image=False, modelId=''):
        plan = self.plan(prompt, schema, thinking=thinking, image=image)
        if plan.inputTokens + plan.outputTokens + plan.safetyTokens > plan.contextTokens:
            logger.warning('context_budget_rejected model=%s context=%s estimated_input=%s output=%s thinking=%s', modelId, plan.contextTokens, plan.inputTokens, plan.outputTokens, thinking)
            raise DomainError(code='OLLAMA_CONTEXT_EXCEEDED', message='Este conteúdo precisa ser organizado em partes antes de continuar. Tente uma seção ou uma pergunta mais específica.', httpStatus=422)
        return plan
