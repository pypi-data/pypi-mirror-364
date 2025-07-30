import os
from dotenv import load_dotenv
from .token_utils import num_tokens_from_string
from .selector import select_chunks_within_budget

load_dotenv()

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"

_default_client = None
if os.getenv("GROQ_API_KEY"):
    from groq import Groq
    _default_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_chunk_with_groq(chunk: str, query: str, model=DEFAULT_GROQ_MODEL, client=None) -> str:
    """
    Summarizes a given document chunk using the Groq API.
    
    Args:
        chunk (str): The text chunk to summarize.
        query (str): The user query.
        model (str): The Groq model name.
        client: Optional Groq client. If not provided, uses default from environment.

    Returns:
        str: The summarized content.
    """
    if client is None:
        if _default_client is None:
            raise ValueError("Groq client must be passed explicitly if GROQ_API_KEY is not set.")
        client = _default_client

    prompt = (
        f"Summarize the following document chunk focusing on answering this query:\n"
        f"Query: {query}\n"
        f"Chunk: {chunk}\n\n"
        f"Provide a concise but informative summary:"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=256,
    )

    return response.choices[0].message.content.strip()


def compress_chunk(chunks: list[str], query: str, token_budget: int, model=DEFAULT_GROQ_MODEL, client=None) -> list[str]:
    """
    Compresses a list of document chunks by summarizing each and returning only the summaries
    that fit within the specified token budget.

    Args:
        chunks (list[str]): List of document chunks.
        query (str): The user query.
        token_budget (int): Max allowed tokens for all summaries combined.
        model (str): The Groq model to use.
        client: Optional Groq client. If not provided, uses default.

    Returns:
        list[str]: Selected summarized chunks fitting within the token budget.
    """
    summarized_chunks = []
    for chunk in chunks:
        summary = summarize_chunk_with_groq(chunk, query, model=model, client=client)
        summarized_chunks.append(summary)

    chunk_token_pairs = [(chunk, num_tokens_from_string(chunk)) for chunk in summarized_chunks]
    chunk_token_pairs.sort(key=lambda x: x[1])

    selected_summaries = []
    total_tokens = 0
    for summary, tokens in chunk_token_pairs:
        if total_tokens + tokens <= token_budget:
            selected_summaries.append(summary)
            total_tokens += tokens
        else:
            break

    return selected_summaries