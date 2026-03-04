# ULTRA TECHNICAL HANDOFF – LOTOFACIL INTELLIGENT PLATFORM

## 1. STRATEGIC OBJECTIVE

Transform the current desktop statistical system into a modular, scalable, SaaS-ready architecture including:

- Clean Domain Layer
- Centralized Statistical Engine
- FastAPI-ready API layer
- Web layer with Google AdSense monetization
- Future AI integration capability
- Strict mathematical and legal compliance

The system must operate strictly as statistical analysis software.

---

## 2. MATHEMATICAL FOUNDATION

Lottery Model:

- Universe: 25 numbers
- Selection: 15 unique numbers
- Total combinations: 3,268,760
- Probability of 15 hits: 1 / 3,268,760

All draws are equiprobable.

The system:
- MUST NOT claim predictive capability
- MUST NOT suggest probability improvement
- MUST operate under statistical transparency

---

## 3. ARCHITECTURE (MANDATORY LAYER SEPARATION)

### 1. Domain Layer
Pure business logic.
No external dependencies.

### 2. Application Layer
Engine orchestration.
Strategy execution.
Backtest simulation.

### 3. Infrastructure Layer
Database.
Downloader.
External services.

### 4. Interface Layer
Desktop.
API (FastAPI).
Web frontend.

No layer leakage allowed.

---

## 4. FINAL DIRECTORY STRUCTURE


core/
domain/
models.py
value_objects.py
rules.py
statistics/
frequency.py
delay.py
distribution.py
aggregations.py
strategies/
base.py
frequency_strategy.py
balanced_strategy.py
hybrid_strategy.py
engine/
generator.py
scorer.py
validator.py
filters.py
backtest/
simulator.py
metrics.py
ai/
report_generator.py
adaptive_ranker.py

infrastructure/
database/
connection.py
repository.py
downloader/
caixa_client.py
parser.py

api/
main.py
routes/
schemas/

web/
templates/
static/
ads/

tests/
database/


---

## 5. DOMAIN MODELING

### Entity: Concurso

- numero: int
- data: date
- dezenas: Tuple[int, 15]

### Value Object: Jogo

- 15 sorted integers
- soma
- pares
- impares

Validation Rules:

- Exactly 15 numbers
- Unique
- Range 1–25
- Immutable value object

---

## 6. STRATEGY CONTRACT

```python
class BaseStrategy:
    def generate(self, statistics_data) -> list[Jogo]:
        ...

Strategies must be:

Pluggable

Independent

Testable

Deterministic

7. ENGINE RESPONSIBILITIES

Execute strategies

Apply statistical filters

Validate rule compliance

Score games

Rank outputs

Export structured results

Engine must not access UI directly.

8. BACKTEST SYSTEM

Simulate strategies over historical ranges.

Required Metrics:

Average hits

Standard deviation

Maximum hits

Hit distribution

Stability index

Backtest must be deterministic and reproducible.

9. DATABASE SCHEMA

Table: concursos

numero (PRIMARY KEY)

data (TEXT)

d1 ... d15 (INTEGER)

Repository pattern mandatory.

No SQL inside domain layer.

10. API PREPARATION (FASTAPI)

Endpoints:

GET /estatisticas

POST /gerar

POST /backtest

GET /historico/{numero}

Domain objects must not leak to DTO layer.

Strict schema validation required.

11. WEB + GOOGLE ADSENSE MONETIZATION

Objective:

Enable automatic personalized advertising via Google AdSense.

Each visitor sees different ads based on:

Cookies

Browsing behavior

Google interest profiling

Real-time auction system

Implementation Requirements:

Global AdSense script in <head>

Responsive ad blocks

Privacy Policy page

Cookie consent (LGPD/GDPR compliant)

No artificial click encouragement

No misleading UI

Revenue scales with traffic and engagement.

12. AI PREPARATION

Future AI capabilities:

Statistical insight generation

Adaptive ranking optimization

Automated textual reports

Pattern explanation

AI must:

Never predict future numbers

Never imply probability improvement

Operate as analysis assistant only

13. TESTING REQUIREMENTS

Unit tests (statistics)

Strategy validation tests

Backtest reliability tests

Engine orchestration tests

Minimum coverage: 70%

CI-ready test structure recommended.

14. EXECUTION PLAN

Audit existing repository

Refactor to layered architecture

Remove redundancy

Centralize statistical engine

Integrate desktop to new core

Implement automated test suite

Only after stabilization → start API/Web rollout

END OF DOCUMENT