"""
Panel-related models and enums for the Expert Panel system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class DiscussionPattern(Enum):
    """Available discussion patterns for agent interaction."""

    ROUND_ROBIN = "round_robin"
    OPEN_FLOOR = "open_floor"
    STRUCTURED_DEBATE = "structured_debate"


@dataclass
class PanelResult:
    """Results from a panel discussion."""

    topic: str
    discussion_pattern: DiscussionPattern
    agents_participated: List[str]
    discussion_history: List[Dict[str, Any]]
    consensus_reached: bool
    final_recommendation: str
    total_rounds: int
