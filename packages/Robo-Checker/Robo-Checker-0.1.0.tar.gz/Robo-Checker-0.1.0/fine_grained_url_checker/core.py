from typing import Dict, Union, List
from urllib.parse import urlparse
from functools import lru_cache
from protego import Protego
import pandas as pd

_DEFAULT_REMOVE_USER_AGENTS = [
    "AI2Bot",  # AI2
    "Applebot-Extended",  # Apple
    "Bytespider",  # Bytedance
    "CCBot",  # Common Crawl
    "CCBot/2.0",  # Common Crawl
    "CCBot/1.0",  # Common Crawl
    "ClaudeBot",  # Anthropic
    "cohere-training-data-crawler",  # Cohere
    "Diffbot",  # Diffbot
    "FacebookBot",  # Meta
    "Meta-ExternalAgent",  # Meta
    "Google-Extended",  # Google
    "GPTBot",  # OpenAI
    "PanguBot",  # Huawei
    "*",
]

FINE_ROBOTS_PATH = 'fineweb_robots_compressed.parquet'

def load_robots(path: str = FINE_ROBOTS_PATH) -> Dict[str, Union[str, bytes]]:
    robots_domains = pd.read_parquet(path)
    return {row["domain"]: row["content"] for _, row in robots_domains.iterrows()}

class RobotsTxtComplianceChecker:
    def __init__(self, robots_txt_by_domain: Dict[str, Union[str, bytes]]):
        self.robots_dict = robots_txt_by_domain

    @lru_cache(maxsize=8192)
    def _get_parser(self, domain: str):
        robots_txt = self.robots_dict.get(domain)
        if not robots_txt:
            return None
        try:
            if isinstance(robots_txt, bytes):
                robots_txt = robots_txt.decode("utf-8", errors="replace")
            return Protego.parse(robots_txt)
        except Exception:
            return None

    def is_compliant(self, url: str, user_agents: List[str] = _DEFAULT_REMOVE_USER_AGENTS) -> str:
        domain = urlparse(url).netloc
        parser = self._get_parser(domain)
        if not parser:
            return "Compliant"
        for agent in user_agents:
            try:
                if not parser.can_fetch(url, agent):
                    return "NonCompliant"
            except Exception:
                continue
        return "Compliant" 