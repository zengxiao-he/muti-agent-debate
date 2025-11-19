from typing import List, Tuple

from .llm import call_llm
from .search import web_search


async def generate_candidate_solutions(
    topic: str,
    num_solutions: int = 4,
    language: str = "zh",
) -> List[Tuple[str, str]]:
    """
    Generate several distinct candidate solutions for a given topic.

    Returns a list of (solution_name, short_description).
    """
    num_solutions = max(3, min(5, num_solutions))
    prompt = (
        "You are a strategy designer tasked with creating several clearly "
        "distinct solution paths for a topic.\n"
        f"Topic: {topic}\n\n"
        f"Please propose {num_solutions} candidate solutions. Each one should:\n"
        "1. Have a clear stance or strategic direction that is meaningfully "
        "different from the others;\n"
        "2. Be summarized in a single concise sentence;\n"
        "3. Avoid long essays or detailed implementation plans.\n\n"
        "Return a plain-text list, one per line, using the format:\n"
        "Solution name: one-sentence description\n"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert at designing diverse policy and product "
                "strategies. Always respond in English."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    raw = await call_llm(messages)

    solutions: List[Tuple[str, str]] = []
    for line in raw.splitlines():
        line = line.strip("- ").strip()
        if not line:
            continue
        if "：" in line:
            name, desc = line.split("：", 1)
        elif ":" in line:
            name, desc = line.split(":", 1)
        else:
            name, desc = line, ""
        solutions.append((name.strip(), desc.strip()))
        if len(solutions) >= num_solutions:
            break

    return solutions


async def build_proposal_brief(topic: str, proposal_name: str, proposal_summary: str) -> str:
    """Generate a more detailed position description for a single proposal."""
    user_prompt = (
        f"Topic: {topic}\n"
        f"Proposal: {proposal_name}\n"
        f"Short summary: {proposal_summary}\n\n"
        "Please expand this proposal in bullet points, covering at least:\n"
        "1. Objectives and core idea;\n"
        "2. Expected benefits (for which groups and in what ways);\n"
        "3. High-level implementation path;\n"
        "4. Key assumptions that must hold;\n"
        "5. Known risks and potential negative side effects.\n"
        "Answer in English."
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strategy consultant. Describe proposals clearly "
                "and concretely. Always respond in English."
            ),
        },
        {"role": "user", "content": user_prompt},
    ]
    return await call_llm(messages)


async def collect_evidence(topic: str, proposal_name: str, proposal_summary: str) -> str:
    """
    Build a lightweight evidence pack for a given proposal:
    - Call web_search (currently may return mock data);
    - Use the LLM to structure and critique the evidence.
    """
    base_query = f"{topic} {proposal_name} feasibility evidence data study"
    search_text = await web_search(base_query, max_results=5)

    user_prompt = (
        "You are given a topic and a proposal. Based on the search-result "
        "summary, build supportive and critical evidence for that proposal.\n\n"
        f"Topic: {topic}\n"
        f"Proposal: {proposal_name}\n"
        f"Short summary: {proposal_summary}\n\n"
        "Here is a (possibly incomplete) search-result summary. Extract "
        "useful information and explicitly call out uncertainties:\n"
        f"{search_text}\n\n"
        "Please output the following sections in English:\n"
        "1. Key arguments supporting this proposal (bullet list, with rough "
        "source descriptions);\n"
        "2. Arguments questioning or opposing this proposal;\n"
        "3. Assessment of evidence quality (source reliability, sample biases, "
        "other limitations);\n"
        "4. Follow-up questions worth deeper investigation.\n"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a highly critical research assistant. Always output "
                "structured bullet points in English."
            ),
        },
        {"role": "user", "content": user_prompt},
    ]
    return await call_llm(messages)


