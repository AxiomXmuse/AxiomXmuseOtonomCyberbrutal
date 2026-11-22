---
name: hykingcr-llm-redteam
description: "LLM red-team framework — 40 vulnerability classes (PIILeakage, ShellInjection, SSRF, PromptLeakage, BOLA, RBAC, ToolMetadataPoisoning, RecursiveHijacking, etc.), 22 single-turn + 5 multi-turn attacks (CrescendoJailbreaking, TreeJailbreaking), MITRE/OWASP/NIST framework mapping, Guardrails for production."
---

# HYKINGCR — LLM Red Team (deepteam)

Source: `repos/deepteam/` (MIT license) | PyPI: `pip install deepteam`

## Install

```bash
pip install deepteam
```

## Quick Start

```python
from deepteam import red_team
from deepteam.vulnerabilities import ShellInjection, SSRF, PIILeakage, PromptLeakage
from deepteam.attacks.single_turn import PromptInjection, Base64, Roleplay
from deepteam.attacks.multi_turn import CrescendoJailbreaking

def model_callback(prompt: str) -> str:
    # Wrap your LLM here — return the model's response string
    import requests
    resp = requests.post("https://your-llm-endpoint/v1/chat", json={"prompt": prompt})
    return resp.json()["response"]

risk = red_team(
    model_callback=model_callback,
    vulnerabilities=[ShellInjection(), SSRF(), PIILeakage(), PromptLeakage()],
    attacks=[PromptInjection(), Base64(), CrescendoJailbreaking()],
)
print(risk)
```

## 40 Vulnerability Classes

| Class | Category | Description |
|---|---|---|
| `Bias` | Safety | Discriminatory or biased outputs |
| `Toxicity` | Safety | Harmful, hateful, or offensive content |
| `Misinformation` | Safety | Factually incorrect or misleading outputs |
| `IllegalActivity` | Safety | Instructions for illegal activities |
| `ChildProtection` | Safety | CSAM or child exploitation content |
| `Ethics` | Safety | Ethical violations or harmful advice |
| `Fairness` | Safety | Unfair treatment across demographic groups |
| `GraphicContent` | Safety | Violent or graphic content generation |
| `PersonalSafety` | Safety | Content endangering personal safety |
| `PromptLeakage` | Security | System prompt or instruction leakage |
| `PIILeakage` | Security | Personally identifiable information disclosure |
| `ShellInjection` | Security | OS command injection via prompt |
| `SQLInjection` | Security | SQL injection via LLM-generated queries |
| `SSRF` | Security | Server-side request forgery via LLM |
| `DebugAccess` | Security | Access to debug mode or dev endpoints |
| `IntellectualProperty` | Legal | Copyright or IP violations |
| `Competition` | Business | Disparagement of competitors |
| `Robustness` | Reliability | Inconsistent or hallucinated outputs under adversarial input |
| `Hallucination` | Reliability | Confident fabrication of false facts |
| `BFLA` | Authorization | Broken function-level authorization (agentic) |
| `BOLA` | Authorization | Broken object-level authorization |
| `RBAC` | Authorization | Broken role-based access control |
| `IndirectInstruction` | Agentic | Indirect prompt injection via retrieved content |
| `ToolOrchestrationAbuse` | Agentic | Abuse of tool calling / function calling interface |
| `AgentIdentityAbuse` | Agentic | Impersonation or identity spoofing in multi-agent |
| `ToolMetadataPoisoning` | Agentic | Poisoned tool descriptions alter agent behavior |
| `UnexpectedCodeExecution` | Agentic | LLM executes code it should not |
| `InsecureInterAgentCommunication` | Agentic | Unsafe data flow between agents |
| `AutonomousAgentDrift` | Agentic | Agent deviates from authorized objective |
| `CrossContextRetrieval` | Agentic | RAG/memory retrieval crosses user context boundaries |
| `SystemReconnaissance` | Agentic | Agent probes its own environment/infrastructure |
| `ExploitToolAgent` | Agentic | Agent weaponized via tool calls |
| `ExternalSystemAbuse` | Agentic | Unauthorized calls to external APIs/services |
| `GoalTheft` | Agentic | Extraction of agent's hidden goal/objective |
| `RecursiveHijacking` | Agentic | Recursive self-modification or infinite loop induction |
| `ExcessiveAgency` | Agentic | Agent takes actions beyond authorized scope |
| `CustomVulnerability` | Custom | User-defined vulnerability class |

## 22 Single-Turn Attacks

| Class | Strategy |
|---|---|
| `AdversarialPoetry` | Embed malicious instruction in verse |
| `Base64` | Base64-encode the harmful payload |
| `GrayBox` | Use partial system prompt knowledge to craft bypass |
| `Leetspeak` | Obfuscate via 1337-speak substitution |
| `MathProblem` | Frame harmful request as a math word problem |
| `Multilingual` | Submit in low-resource language to bypass filters |
| `PromptInjection` | Direct injection of override instructions |
| `PromptProbing` | Iterative probing to extract system prompt |
| `Roleplay` | Wrap harmful request in fiction/roleplay frame |
| `ROT13` | ROT-13 obfuscation of payload |
| `CharacterStream` | Split payload across character-level stream |
| `ContextFlooding` | Flood context window to dilute safety instructions |
| `EmbeddedInstructionJSON` | Hide instructions inside JSON structure |
| `SyntheticContextInjection` | Inject synthetic prior context to manufacture permission |
| `AuthorityEscalation` | Impersonate authority (admin, developer, system) |
| `EmotionalManipulation` | Exploit emotional appeals to bypass refusal |
| `SystemOverride` | Claim system-level override authority |
| `PermissionEscalation` | Claim escalated permissions within the conversation |
| `GoalRedirection` | Redirect agent's goal to attacker-chosen objective |
| `LinguisticConfusion` | Exploit linguistic ambiguity to bypass semantic filters |
| `InputBypass` | Bypass input validation via encoding/format tricks |
| `ContextPoisoning` | Poison conversation context with false premises |

## 5 Multi-Turn Attacks

| Class | Strategy |
|---|---|
| `CrescendoJailbreaking` | Gradual escalation across turns; each turn individually benign |
| `LinearJailbreaking` | Sequential turn-by-turn escalation toward target |
| `TreeJailbreaking` | Branching multi-path exploration to find successful jailbreak path |
| `SequentialJailbreak` | Sequential decomposition of harmful request across turns |
| `BadLikertJudge` | Use Likert-scale framing to elicit harmful content via indirect scoring |

## Framework Mapping

| Vulnerability | OWASP LLM | MITRE ATLAS | NIST AI RMF |
|---|---|---|---|
| PromptLeakage | LLM07 | AML.T0051 | GOVERN 1.1 |
| ShellInjection | LLM02 | AML.T0049 | MANAGE 2.2 |
| SSRF | LLM02 | AML.T0049 | MANAGE 2.2 |
| PIILeakage | LLM06 | AML.T0025 | GOVERN 6.1 |
| IndirectInstruction | LLM01 | AML.T0054 | MANAGE 2.4 |
| ToolOrchestrationAbuse | LLM08 | AML.T0048 | MANAGE 3.1 |
| ExcessiveAgency | LLM08 | AML.T0048 | MANAGE 3.2 |
| BOLA/BFLA | LLM05 | AML.T0043 | GOVERN 4.1 |

## Guardrails (Production)

```python
from deepteam.guardrails import Guardrails

guards = Guardrails(
    prompt_injection=True,
    pii_detection=True,
    toxicity=True,
    hallucination=True,
)

@guards.protect
def call_llm(prompt: str) -> str:
    return your_llm(prompt)
```

## Standalone Runner

```bash
python3 '${CLAUDE_SKILL_DIR}/scripts/redteam_run.py' \
  --target-url https://your-llm-api/v1/chat \
  --vulns ShellInjection,SSRF,PIILeakage,PromptLeakage \
  --attacks PromptInjection,CrescendoJailbreaking,Base64 \
  --output report.json
```
