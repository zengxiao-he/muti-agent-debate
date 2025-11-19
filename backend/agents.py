from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .llm import call_llm


DebateHistory = List[dict]


@dataclass
class BaseAgent:
    name: str
    role: str

    async def say(self, _topic: str, _history: DebateHistory) -> str:  # pragma: no cover
        raise NotImplementedError


@dataclass
class ProposalAgent(BaseAgent):
    proposal_id: int
    proposal_name: str
    proposal_brief: str
    evidence_pack: str

    async def opening_statement(self, topic: str) -> str:
        """Opening statement based on the proposal brief and evidence pack."""
        system_prompt = (
            "You are a debate participant representing a specific proposal.\n"
            "Your goal is to argue convincingly for the proposal's strengths "
            "and feasibility while honestly acknowledging risks and limits. "
            "Always answer in English."
        )
        user_prompt = (
            f"Topic: {topic}\n"
            f"Proposal you represent: {self.proposal_name}\n\n"
            f"Proposal brief:\n{self.proposal_brief}\n\n"
            f"Evidence pack related to this proposal:\n{self.evidence_pack}\n\n"
            "Please output a structured opening statement in English that "
            "includes:\n"
            "1. 2–3 sentences clearly restating your proposal;\n"
            "2. 3–5 key arguments supporting the proposal (refer to evidence "
            "where appropriate);\n"
            "3. The main risks and criticisms opponents might raise;\n"
            "4. A short closing remark explaining why the proposal is still "
            "worth serious consideration."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await call_llm(messages)

    async def rebuttal(self, topic: str, history: DebateHistory, max_context_turns: int = 6) -> str:
        """
        Generate a new turn by reading the most recent debate history
        and responding to it.
        """
        recent = history[-max_context_turns:]
        history_snippets = []
        for h in recent:
            history_snippets.append(
                f"[Batch {h['batch']} - Round {h['round']} - {h['agent_name']}]\n{h['content']}"
            )
        history_text = (
            "\n\n".join(history_snippets) if history_snippets else "(no prior turns)"
        )

        system_prompt = (
            "You are a participant in a multi-party debate representing one "
            "particular proposal.\n"
            "Your goal is to respond to and critique other speakers' comments "
            "while remaining rational, polite and honest. When necessary, you "
            "may soften or adjust overly extreme positions. Always respond in "
            "English."
        )
        user_prompt = (
            f"Topic: {topic}\n"
            f"Proposal you represent: {self.proposal_name}\n\n"
            f"Proposal brief (for reference):\n{self.proposal_brief}\n\n"
            f"Evidence pack (for reference):\n{self.evidence_pack}\n\n"
            "Here are the most recent debate turns; focus on statements that "
            "support or attack your proposal:\n"
            f"{history_text}\n\n"
            "Please output a new turn in English that:\n"
            "1. Starts with 1–2 sentences summarizing the main supportive and "
            "attacking points you noticed about your proposal;\n"
            "2. Responds to the most important attacks, one by one, using "
            "evidence or logical reasoning;\n"
            "3. Admits when another proposal has a clearly stronger point and "
            "suggests compromise conditions or improved variants of your "
            "proposal;\n"
            "4. Does not restate the entire history, only your own thinking "
            "and reasoning."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await call_llm(messages)


@dataclass
class ModeratorAgent(BaseAgent):
    async def summarize_batch(
        self,
        topic: str,
        batch_index: int,
        history: DebateHistory,
    ) -> str:
        """Optional batch-level summary, mainly for debugging and analysis."""
        related = [h for h in history if h["batch"] == batch_index]
        if not related:
            return ""
        text = []
        for h in related:
            text.append(
                f"[Batch {h['batch']} - Round {h['round']} - {h['agent_name']}]\n{h['content']}"
            )
        history_text = "\n\n".join(text)

        system_prompt = (
            "You are the moderator of this debate. At the end of each batch, "
            "you summarize the main conflicts and points of agreement for the "
            "audience. Answer in English."
        )
        user_prompt = (
            f"Topic: {topic}\n"
            f"Here are all turns in batch {batch_index}:\n"
            f"{history_text}\n\n"
            "Please summarize in concise bullet points (English):\n"
            "1. The core disagreements between proposals;\n"
            "2. Any emerging consensus or compromise directions;\n"
            "3. Suggested focus questions for the next batch."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await call_llm(messages)

    async def final_report(
        self,
        topic: str,
        proposals: list[dict],
        history: DebateHistory,
        language: str = "zh",
    ) -> str:
        """Generate a final report based on the full debate history."""
        history_texts = []
        for h in history:
            history_texts.append(
                f"[Batch {h['batch']} - Round {h['round']} - {h['agent_name']}]\n{h['content']}"
            )
        history_text = "\n\n".join(history_texts)

        proposals_text = []
        for p in proposals:
            proposals_text.append(
                f"- Proposal {p['id']}: {p['name']}\n  Summary: {p['summary']}\n"
            )
        proposals_block = "\n".join(proposals_text)

        system_prompt = (
            "You are a synthesis and evaluation expert. Based on a multi-agent "
            "debate, you must provide a structured, actionable recommendation."
        )
        lang_line = (
            "Please respond in Simplified Chinese."
            if language == "zh"
            else "Please answer in English."
        )
        user_prompt = (
            f"{lang_line}\n\n"
            f"Topic: {topic}\n\n"
            f"Candidate proposals in this debate:\n{proposals_block}\n\n"
            "Here is the full debate transcript:\n"
            f"{history_text}\n\n"
            "Please produce a structured final report that at minimum covers:\n"
            "1. A brief restatement of the problem and evaluation framework;\n"
            "2. Advantages, disadvantages, suitable scenarios and main risks "
            "for each proposal;\n"
            "3. A relative ranking or scoring of the proposals across "
            "dimensions such as impact, cost, risk and implementability;\n"
            "4. A clearly justified primary recommendation;\n"
            "5. Alternative recommendations under different constraints "
            "(e.g. very low budget, extreme time pressure, different risk "
            "preferences);\n"
            "6. Suggested next actions or questions that require further "
            "research."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await call_llm(messages)


