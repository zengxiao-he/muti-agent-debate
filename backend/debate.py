from __future__ import annotations

from typing import List

from .agents import ModeratorAgent, ProposalAgent
from .models import DebateConfig, DebateResult, DebateTurn, AgentInfo, ProposalInfo
from .research import (
    build_proposal_brief,
    collect_evidence,
    generate_candidate_solutions,
)


async def prepare_agents(topic: str, config: DebateConfig) -> tuple[list[ProposalAgent], list[dict]]:
    """Build ProposalAgent instances and proposal metadata from research results."""
    solutions = await generate_candidate_solutions(
        topic,
        num_solutions=config.num_solutions,
    )

    agents: List[ProposalAgent] = []
    proposals_meta: list[dict] = []

    # Sequential generation for simplicity; can be parallelized later.
    proposal_id = 1
    for name, summary in solutions:
        brief = await build_proposal_brief(topic, name, summary)
        evidence = await collect_evidence(topic, name, summary)

        agent = ProposalAgent(
            name=f"Agent-{proposal_id}",
            role="proposal",
            proposal_id=proposal_id,
            proposal_name=name,
            proposal_brief=brief,
            evidence_pack=evidence,
        )
        agents.append(agent)
        proposals_meta.append(
            {
                "id": proposal_id,
                "name": name,
                "summary": summary or brief[:120],
            }
        )
        proposal_id += 1

    return agents, proposals_meta


async def run_debate(
    topic: str,
    config: DebateConfig,
    language: str = "zh",
) -> DebateResult:
    """
    Main multi-agent debate pipeline:
    - Use research to construct agents;
    - Opening statements;
    - Multi-batch, multi-round debate;
    - Moderator generates a final report.
    """
    proposal_agents, proposals_meta = await prepare_agents(topic, config)
    moderator = ModeratorAgent(name="Moderator", role="moderator")

    history: list[dict] = []

    # 1. Opening statements
    for agent in proposal_agents:
        content = await agent.opening_statement(topic)
        history.append(
            {
                "batch": 0,
                "round": 0,
                "agent_name": agent.name,
                "role": "proposal",
                "content": content,
            }
        )

    # 2. Multi-batch, multi-round debate
    for b in range(1, config.num_batches + 1):
        for r in range(1, config.rounds_per_batch + 1):
            for agent in proposal_agents:
                content = await agent.rebuttal(topic, history)
                history.append(
                    {
                        "batch": b,
                        "round": r,
                        "agent_name": agent.name,
                        "role": "proposal",
                        "content": content,
                    }
                )
        # Optional: batch-level summary (returned as part of history)
        summary = await moderator.summarize_batch(topic, b, history)
        if summary:
            history.append(
                {
                    "batch": b,
                    "round": 0,
                    "agent_name": moderator.name,
                    "role": "moderator",
                    "content": summary,
                }
            )

    # 3. Final report
    final_report = await moderator.final_report(
        topic=topic,
        proposals=proposals_meta,
        history=history,
        language=language,
    )

    proposal_infos = [
        ProposalInfo(id=p["id"], name=p["name"], summary=p["summary"])
        for p in proposals_meta
    ]
    agent_infos = [
        AgentInfo(
            name=a.name,
            proposal_id=a.proposal_id,
            role=a.role,
        )
        for a in proposal_agents
    ]
    turns = [
        DebateTurn(
            batch=h["batch"],
            round=h["round"],
            agent_name=h["agent_name"],
            role=h["role"],
            content=h["content"],
        )
        for h in history
    ]

    return DebateResult(
        topic=topic,
        proposals=proposal_infos,
        agents=agent_infos,
        history=turns,
        final_report=final_report,
    )


