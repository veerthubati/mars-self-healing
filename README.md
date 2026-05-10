<h1 align="center">MARS — Multi-Agent Reasoning for Self-Healing</h1>

<p align="center">
  <em>Autonomous incident detection, diagnosis, and remediation for cloud-native microservice systems</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/release/python-311/"><img src="https://img.shields.io/badge/Python-3.11+-yellow.svg" alt="Python"></a>
  <img src="https://img.shields.io/badge/Status-Under%20Review-orange.svg" alt="Status">
</p>

---

## Overview

MARS is a multi-agent AI framework that autonomously resolves production incidents in microservice architectures. Instead of relying on static runbooks or single-model inference, MARS splits the self-healing workflow across four specialized LLM agents — each grounded in organizational knowledge through Retrieval-Augmented Generation (RAG).

**How it works:** When a service starts failing, MARS detects the problem, figures out what caused it, plans a fix, and safely executes the repair — all without waking up an engineer at 3 AM.

**Key Results** (from our evaluation with 250 controlled failure scenarios):
- **73.2%** of incidents resolved autonomously (no human needed)
- **5.2 minutes** average recovery time (down from 14.7 min with traditional automation)
- **87.3%** accuracy in identifying the correct root cause
- **4.2%** rate of unnecessary actions (the system knows when to ask for help)

---

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌────────────┐
│  Observer   │───▶│  Diagnostician   │───▶│  Strategist │───▶│  Executor  │
│   Agent     │    │     Agent        │    │    Agent    │    │   Agent    │
│             │    │                  │    │             │    │            │
│ • Metrics   │    │ • Root Cause     │    │ • Plan      │    │ • K8s API  │
│ • Logs      │    │ • RAG Retrieval  │    │ • Risk      │    │ • Rollback │
│ • Traces    │    │ • Evidence Chain │    │ • Confidence│    │ • Canary   │
└─────────────┘    └────────┬─────────┘    └──────┬──────┘    └────────────┘
                            │                      │
                            ▼                      ▼
                   ┌─────────────────────────────────────┐
                   │        RAG Knowledge Base           │
                   │  • 450 Runbooks  • 12K+ Incidents   │
                   │  • Architecture Docs  • ADRs        │
                   └─────────────────────────────────────┘
```

**What each agent does:**
- **Observer** — Watches metrics, logs, and traces. Detects real anomalies while filtering out noise.
- **Diagnostician** — Searches past incidents and runbooks to identify the root cause.
- **Strategist** — Plans a safe remediation with risk assessment and rollback options.
- **Executor** — Carries out the fix (restart, scale, rollback, reroute) with built-in safety checks.

---

## Project Structure

```
mars-self-healing/
├── src/
│   ├── agents/                # Agent implementations
│   │   ├── observer.py        # Anomaly detection and signal fusion
│   │   ├── diagnostician.py   # RAG-enhanced root cause analysis
│   │   ├── strategist.py      # Remediation planning and risk assessment
│   │   └── executor.py        # Safe action execution with rollback
│   ├── rag/                   # Retrieval-Augmented Generation pipeline
│   ├── orchestrator/          # Multi-agent coordination
│   │   ├── pipeline.py        # Agent pipeline and message passing
│   │   └── confidence_gate.py # Adaptive confidence scoring
│   ├── evaluation/            # Experiment framework
│   └── utils/                 # Shared utilities
├── configs/
│   ├── agents/                # Agent prompt templates and parameters
│   └── scenarios/             # Fault injection scenarios
├── data/
│   ├── runbooks/              # Operational runbooks (synthetic)
│   ├── incidents/             # Historical incident reports
│   └── architecture/          # Service topology and configs
├── experiments/               # Experiment outputs and plots
├── paper/                     # LaTeX source for the research paper
├── tests/                     # Unit and integration tests
├── pyproject.toml             # Project metadata and dependencies
├── Makefile                   # Common commands
├── CONTRIBUTING.md            # Contribution guidelines
├── CODE_OF_CONDUCT.md         # Community standards
└── LICENSE                    # Apache 2.0
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Kubernetes (Minikube for local development)
- OpenAI API key or compatible LLM endpoint

### Installation

```bash
git clone https://github.com/veerthubati/mars-self-healing.git
cd mars-self-healing
pip install -e ".[dev]"
```

### Run Experiments

```bash
# Run all 250 fault injection scenarios
make run-experiments

# Generate comparison plots
make plots

# Run ablation study (testing each component's contribution)
make ablation
```

---

## Evaluation

### Failure Categories Tested

| Category | Scenarios | What It Tests |
|----------|-----------|---------------|
| Cascading Failures | 15 | Service failures spreading through dependency chains |
| Resource Exhaustion | 12 | Memory leaks, CPU saturation, disk pressure |
| Network Partitions | 10 | Connectivity issues, DNS failures, timeout storms |
| Dependency Degradation | 13 | Slow downstream services, database performance |

---

## Research Paper

This repository accompanies a research paper currently under review:

> **Adaptive Multi-Agent AI Architecture for Autonomous Microservice Self-Healing in Cloud-Native Systems: A Framework with Retrieval-Augmented Reasoning**

The paper details the framework design, experimental methodology, and evaluation results.

### Citation

```bibtex
@article{thubati2025mars,
  title={Adaptive Multi-Agent AI Architecture for Autonomous Microservice 
         Self-Healing in Cloud-Native Systems: A Framework with 
         Retrieval-Augmented Reasoning},
  author={Thubati, Veeraiah Chowdary and Tubati, Durga Prasad},
  year={2025},
  note={Under review}
}
```

---

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

This work explores the intersection of large language models, multi-agent systems, and site reliability engineering. We thank the open-source communities behind LangChain, ChromaDB, and Kubernetes for enabling this research.
