from abc import ABC, abstractmethod
from typing import List
from packages.schemas import NormalizedJobPost

class BaseATSMonitor(ABC):
    """Abstract Base Class for ATS Monitors (Greenhouse, Lever, etc.)."""

    @property
    @abstractmethod
    def ats_name(self) -> str:
        """Returns name of the ATS vendor (e.g. 'greenhouse', 'lever')."""
        pass

    @abstractmethod
    async def fetch_jobs(self, company_name: str, board_token: str) -> List[NormalizedJobPost]:
        """Fetches and normalizes all job postings for a given board token."""
        pass
