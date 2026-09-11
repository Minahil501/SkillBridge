"""Free, Hugging Face-hosted LLM chat for career advice, grounded in a student's SkillBridge prediction."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# Qwen/Qwen2.5-7B-Instruct no longer routes: auto-routing maps it to a Together model
# that isn't served serverless. The ":cheapest" suffix picks the lowest-priced provider
# serving the model, which matters because a free account gets $0.10 of credit a month.
CHAT_MODEL = os.environ.get("HF_CHAT_MODEL", "meta-llama/Llama-3.1-8B-Instruct:cheapest")

_client = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        token = os.environ.get("HF_TOKEN")
        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Create a free token at "
                "https://huggingface.co/settings/tokens and set it as an environment "
                "variable before starting the server to enable the chat feature."
            )
        _client = InferenceClient(token=token)
    return _client


def _system_prompt(context: dict) -> str:
    score = context.get("employability_score")
    career = context.get("recommended_career_path")
    confidence = context.get("confidence") or 0
    probs = context.get("career_probabilities") or {}
    ranked = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    ranked_str = ", ".join(f"{name} ({p:.0%})" for name, p in ranked)

    return (
        "You are a career advisor embedded in SkillBridge, a tool that predicts student "
        "employability and recommends a career path from their academic and skills profile.\n\n"
        f"This student's prediction: employability score {score}/100, recommended career "
        f"'{career}' with {confidence:.0%} model confidence. Full ranking: {ranked_str}.\n\n"
        "Answer the student's follow-up questions about this result — what it means, how to "
        "improve their score, how to prepare for the recommended career, or why another career "
        "might also fit. Be encouraging but honest; this is a statistical estimate from a small "
        "training dataset, not a verdict, so avoid overstating its certainty. Keep replies to "
        "2-4 sentences unless the student asks for more detail."
    )


def chat(messages: list[dict], context: dict) -> str:
    """Send a conversation turn to a free Hugging Face-hosted model, grounded in the prediction."""
    client = _get_client()
    full_messages = [{"role": "system", "content": _system_prompt(context)}, *messages]
    response = client.chat_completion(
        messages=full_messages,
        model=CHAT_MODEL,
        max_tokens=512,
    )
    return response.choices[0].message.content
