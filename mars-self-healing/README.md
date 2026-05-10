<p align="center">
  <img src="docs/figures/mars-logo.png" alt="MARS Logo" width="120"/>
</p>

<h1 align="center">MARS — Multi-Agent Reasoning for Self-Healing</h1>

<p align="center">
  <em>Autonomous incident detection, diagnosis, and remediation for cloud-native microservice systems</em>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2505.XXXXX"><img src="https://img.shields.io/badge/arXiv-2505.XXXXX-b31b1b.svg" alt="arXiv"></a>
  <a href="https://ieeexplore.ieee.org/document/XXXXXXX"><img src="https://img.shields.io/badge/IEEE%20Access-Published-blue.svg" alt="IEEE Access"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/release/python-311/"><img src="https://img.shields.io/badge/Python-3.11+-yellow.svg" alt="Python"></a>
</p>

---

## Overview

MARS is a multi-agent AI framework that autonomously resolves production incidents in microservice architectures. Instead of relying on static runbooks or single-model inference, MARS splits the self-healing workflow across four specialized LLM agents—each grounded in organizational knowledge through Retrieval-Augmented Generation (RAG).

**Key Results** (from our [paper](https://arxiv.org/abs/2505.XXXXX)):
- **73.2%** autonomous resolution rate across 250 fault-injection experiments
- **5.2 min** mean time to recovery (vs. 14.7 min with rule-based automation)
- **91.4%** diagnostic accuracy with RAG-enhanced reasoning
- **2.1%** false-positive remediation rate (calibrated confidence gate)

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
                   │        RAG Knowledge Base            │
                   │  • 450 Runbooks  • 12K+ Incidents   │
                   │  • Architecture Docs  • ADRs        │
                   └─────────────────────────────────────┘
```

---

## Project Structure

```
mars-self-healing/
├── src/
│   ├── agents/                # Agent implementations
│   │   ├── __init__.py
│   │   ├── observer.py        # Anomaly detection & signal fusion
│   │   ├── diagnostician.py   # RAG-enhanced root cause analysis
│   │   ├── strategist.py      # Remediation planning & risk assessment
│   │   └── executor.py        # Safe action execution with rollback
│   ├── rag/                   # Retrieval-Augmented Generation pipeline
│   │   ├── __init__.py
│   │   ├── knowledge_base.py  # Document ingestion & indexing
│   │   ├── retriever.py       # Hybrid dense+sparse retrieval
│   │   └── embeddings.py      # Embedding model interface
│   ├── orchestrator/          # Multi-agent coordination
│   │   ├── __init__.py
│   │   ├── pipeline.py        # Agent pipeline & message passing
│   │   └── confidence_gate.py # Adaptive confidence scoring
│   ├── evaluation/            # Experiment framework
│   │   ├── __init__.py
│   │   ├── fault_injector.py  # Chaos engineering scenarios
│   │   ├── metrics.py         # ARR, MTTR, accuracy measurement
│   │   └── baselines.py       # Baseline implementations
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── logging.py         # Structured logging
│       └── telemetry.py       # Metrics/traces/logs collection
├── configs/
│   ├── agents/                # Agent prompt templates & parameters
│   │   ├── observer.yaml
│   │   ├── diagnostician.yaml
│   │   ├── strategist.yaml
│   │   └── executor.yaml
│   ├── scenarios/             # Fault injection scenarios
│   │   ├── cascading_failures.yaml
│   │   ├── resource_exhaustion.yaml
│   │   ├── network_partitions.yaml
│   │   └── dependency_degradation.yaml
│   └── retrieval/             # RAG configuration
│       └── retrieval_config.yaml
├── data/
│   ├── runbooks/              # Operational runbooks (synthetic)
│   ├── incidents/             # Historical incident reports
│   └── architecture/          # Service topology & configs
├── experiments/
│   ├── results/               # Experiment output data
│   ├── logs/                  # Execution logs
│   └── plots/                 # Generated figures
├── docs/
│   ├── architecture/          # Design documents
│   └── figures/               # Paper figures & diagrams
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── paper/                     # LaTeX source
│   └── main.tex
├── .github/
│   └── workflows/
│       └── ci.yaml            # CI pipeline
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata
├── Makefile                   # Common commands
├── Dockerfile                 # Container build
├── LICENSE                    # Apache 2.0
└── README.md                  # This file
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Kubernetes (Minikube for local development)
- OpenAI API key or compatible LLM endpoint

### Installation

```bash
git clone https://github.com/veerthubati/mars-self-healing.git
cd mars-self-healing
pip install -r requirements.txt
```

### Configuration

```bash
cp configs/retrieval/retrieval_config.yaml.example configs/retrieval/retrieval_config.yaml
# Edit with your LLM API key and embedding model settings
```

### Run MARS

```bash
# Start the agent pipeline
python -m src.orchestrator.pipeline --config configs/agents/

# Inject a test failure
python -m src.evaluation.fault_injector --scenario cascading_failures

# View results
python -m src.evaluation.metrics --output experiments/results/
```

---

## Evaluation

Reproduce the paper's experiments:

```bash
# Run all 250 fault injection scenarios
make run-experiments

# Generate comparison plots
make plots

# Run ablation study
make ablation
```

### Failure Categories Tested

| Category | Scenarios | Description |
|----------|-----------|-------------|
| Cascading Failures | 15 | Service failures propagating through dependency chains |
| Resource Exhaustion | 12 | Memory leaks, CPU saturation, disk pressure |
| Network Partitions | 10 | Connectivity issues, DNS failures, timeout storms |
| Dependency Degradation | 13 | Slow downstream services, database performance |

---

## Citation

If you use MARS in your research, please cite:

```bibtex
@article{thubati2025mars,
  title={Adaptive Multi-Agent AI Architecture for Autonomous Microservice 
         Self-Healing in Cloud-Native Systems: A Framework with 
         Retrieval-Augmented Reasoning},
  author={Thubati, Veer},
  journal={IEEE Access},
  year={2025},
  doi={10.1109/ACCESS.2025.XXXXXXX}
}
```

---

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

This work explores the intersection of large language models, multi-agent systems, and site reliability engineering. We thank the open-source communities behind LangChain, ChromaDB, and Kubernetes for enabling this research.
