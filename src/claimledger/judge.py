"""Answer-level scoring with a local Ollama model.

This is weaker than the LongMemEval paper's GPT-4o judge: the reader and the judge
are the same small local model, and its verdicts are not comparable to published
answer-accuracy numbers. Retrieval recall is the headline for that reason.
"""
import json
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
CONTEXT_CHARS_PER_SESSION = 1500


def _generate(model: str, prompt: str, timeout: float = 600.0) -> str:
    body = json.dumps(
        {"model": model, "prompt": prompt, "stream": False,
         "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 200}}
    ).encode()
    request = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)["response"]


def parse_verdict(text: str) -> bool:
    """True only when the reply starts with yes; anything ambiguous counts as incorrect."""
    return text.strip().lower().startswith("yes")


def ollama_judge(model: str, generate=_generate):
    def judge(question: str, gold_answer: str, context_sessions: list[str]) -> bool:
        context = "\n\n".join(
            f"[session {i + 1}]\n{text[:CONTEXT_CHARS_PER_SESSION]}" for i, text in enumerate(context_sessions)
        )
        answer = generate(
            model,
            f"Use the chat history to answer the question briefly.\n\n{context}\n\nQuestion: {question}\nAnswer:",
        )
        verdict = generate(
            model,
            "Does the response contain the same answer as the reference answer? Reply yes or no.\n\n"
            f"Question: {question}\nReference answer: {gold_answer}\nResponse: {answer}\n\nReply:",
        )
        return parse_verdict(verdict)

    return judge


def judge_label(model: str) -> str:
    return f"ollama:{model} (local, reader and judge are the same model)"
