` 
# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.
``

Project: Enterprise Compliance Filter (Python, Flask)

Commands (run from repo root)

- Setup
  - python -m pip install -r src/requirements.txt
  - Optional (spaCy model for enhanced privacy NLP): python -m spacy download en_core_web_sm

- Run (local dev)
  - python src/run_secure_demo.py
  - or: python src/wsgi.py  (exercise the WSGI entrypoint without Gunicorn)
  - or (Windows production-style from src): waitress-serve --listen=127.0.0.1:5000 wsgi:application

- Tests (these are standalone scripts; no pytest suite in this repo)
  - Full accuracy suite: python src/test_accuracy.py
  - Detector harness:    python src/test_detector.py
  - Targeted fixes:      python src/test_fixes.py

- Lint/format/type-check (optional if installed locally or via dev Docker stage)
  - black .
  - flake8 .
  - mypy src

- Docker
  - Build: docker build -t compliance-filter ./src
  - Run:   docker run -p 5000:5000 compliance-filter
  - Compose stack: docker-compose -f src/docker-compose.yml up -d

Notes on optional detectors

- hate_speech_detector.py requires transformers and a model; if missing, it is disabled and the system relies on other signals.
- privacy_detector.py runs via regex by default; installing spaCy en_core_web_sm enables additional NER-based checks.

High-level architecture (big picture)

- Web and auth layer
  - authenticated_demo_ui.py defines the Flask app and secure demo UI (JWT, RBAC, MFA, OAuth hooks) and wires in the v2 compliance pipeline.
  - wsgi.py is the production entrypoint: loads ProductionConfig, enforces security headers/HTTPS (configurable), and exposes /health, /ready, /metrics.
  - gunicorn_config.py configures gevent workers, timeouts, logging, and optional TLS for container deploys.

- Compliance engines
  - v2 primary (enhanced_compliance_filter_v2.py): orchestrates AdvancedDetector and SemanticAnalyzer with intelligent caching (intelligent_cache.py), context-aware thresholds, and false-positive overrides; returns EnhancedComplianceResult with action (ALLOW/WARN/BLOCK), threat level, reasoning, context, and FP analysis.
  - v1 foundational (compliance_filter.py): combines privacy_detector and hate_speech_detector, offers IntelligentCache (L1 memory + optional Redis L2) and PerformanceMonitor, and computes composite risk scores/thresholds.

- Detectors and ML integrations
  - advanced_detector.py: pattern-augmented classifier; can call external LLMs (Vertex AI, OpenAI, Anthropic) if creds exist; otherwise uses rules/patterns.
  - privacy_detector.py: PII and sensitive-content detection via regex + optional spaCy.
  - hate_speech_detector.py: Hugging Face classifiers (e.g., unitary/toxic-bert) with configurable thresholds.
  - ensemble_detector.py (optional): wraps multiple HF models to ensemble category scores.

- LLM middleware
  - llm_integration.py: pre/post compliance hooks around provider calls (OpenAI, Anthropic, Azure OpenAI, Hugging Face) with async flow and basic rate limiting.

- Production and ops
  - production_config.py: env-driven settings (DB/Redis/JWT/CORS/logging/rate limits) with validators and helpers.
  - Dockerfile (in src): multi‑stage; default CMD runs Gunicorn serving wsgi:application; development stage includes pytest/black/flake8/mypy.
  - docker-compose.yml (in src): app, Postgres, Redis, Nginx, optional Prometheus/Grafana/Fluentd; healthchecks and labels included.

Cross-references

- See src/README.md for Quick Start, API examples, and production guidance.
- See src/PRODUCTION_DEPLOYMENT.md and src/PRODUCTION_SUMMARY.md for deployment options and checklists.
