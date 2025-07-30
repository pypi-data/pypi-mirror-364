"""
CrystaLyse.AI Agent Module

This module provides the unified materials discovery agent using OpenAI Agents SDK.
All legacy agent implementations have been consolidated into a single, efficient agent.
"""

from .crystalyse_agent import (
    CrystaLyse, 
    AgentConfig,
    analyse_materials,
    rigorous_analysis, 
    creative_analysis
)
from .session_based_agent import (
    CrystaLyseSession,
    CrystaLyseSessionManager
)

__all__ = [
    "CrystaLyse",
    "AgentConfig",
    "analyse_materials",
    "rigorous_analysis",
    "creative_analysis",
    "CrystaLyseSession",
    "CrystaLyseSessionManager"
]
