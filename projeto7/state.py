from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    target_ip: str
    target_port: int
    scan_results: List[str]
    potential_vul: List[dict]
    verified_vul: List[dict]
    remediation_steps: str
    final_report: str
    messages: Annotated[List[str], operator.add]
