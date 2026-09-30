from typing import Any


def chunk_policy_text(policy_id: str, text: str, section: str | None = None) -> dict[str, Any]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs and text.strip():
        paragraphs = [text.strip()]
    chunks = []
    for index, paragraph in enumerate(paragraphs, start=1):
        chunks.append(
            {
                "id": f"{policy_id}-chunk-{index}",
                "policy_id": policy_id,
                "text": paragraph,
                "section": section or f"section-{index}",
                "page_reference": str(index),
                "metadata": {"policy_id": policy_id, "ordinal": index},
            }
        )
    return {"policy_id": policy_id, "chunks": chunks}
