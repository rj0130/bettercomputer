# BetterComputer — Technical Design Document

**Overview**

This document captures the technical design, current status, and remaining work for the BetterComputer platform: an e-store and operations platform for rapid device refactoring, R&D, operations, and management.

**Vision & Goals**

- Provide a public storefront for customers to request/refactor device upgrades.
- Manage orders, inventory, staff, scheduling/operations, R&D logs, and management projects.
- Support rapid turn-around modular upgrades with a data-driven SAGA orchestration between services.
- Enable future robotic/automation integration via machine-readable recipes from R&D.

**Where we are (current scaffold)**

- Workspace folder: `bettercomputer/`
- Projects added (skeletons):
  - `src/BetterComputer.Shared/` — shared DTOs and value objects. ([src/BetterComputer.Shared](src/BetterComputer.Shared))
  - `src/BetterComputer.Platform/` — common infra (logging, DI). ([src/BetterComputer.Platform](src/BetterComputer.Platform))
  - `src/Orders.Api/` — Orders API (health + sample endpoint). ([src/Orders.Api](src/Orders.Api))
  - `src/Inventory.Api/` — Inventory API (health + sample). ([src/Inventory.Api](src/Inventory.Api))
  - `src/Staff.Api/` — Staff API (health + sample). ([src/Staff.Api](src/Staff.Api))
  - `src/Operations.Api/` — Operations & scheduling (health + sample). ([src/Operations.Api](src/Operations.Api))
  - `src/RnD.Api/` — RnD logs service (Mongo driver reference; health + sample). ([src/RnD.Api](src/RnD.Api))
  - `src/Management.Api/` — Management portal API (health + sample). ([src/Management.Api](src/Management.Api))
  - `src/Workers/` — Worker host for background tasks. ([src/Workers](src/Workers))
  - `docker-compose.yml` — initial compose created at scaffold time (root).
  - `README_ARCHITECTURE.md` — short architecture note.

Technical checks performed:

- `dotnet build` was run for API projects and succeeded for the created skeletons.
- VS Code extensions and developer tool installs were performed earlier (C#, Docker, MongoDB, SQL, Prettier, ESLint, etc.).

**High-level architecture**

- Microservice-style split: each bounded-context has its own Web API and data store.
- Event-driven integration: services publish domain events (OrderCreated, PartsReserved, WorkOrderCompleted). Subscribers update local state and trigger side effects.
- Data stores:
  - PostgreSQL (primary OLTP for Orders, Inventory, Staff, Management projects)
  - MongoDB (document store for R&D logs/recipes/experiments)
  - Vector DB (for R&D search and future ConsoleGenie integrations) — placeholder for Pinecone/Weaviate or Atlas Vector.
  - Redis (cache, distributed locks)
- Messaging: RabbitMQ or Kafka for asynchronous events and SAGA orchestration.
- Background processing: Workers host processes asynchronous jobs (embeddings, long-running tasks, integration retries, robotic dispatch).

**Service responsibilities & initial API surface**

- Orders.Api
  - Responsibilities: create orders, update status, expose order lifecycle events, payment integration hook.
  - Implemented (skeleton): `/health`, `/orders/sample`
  - To implement: `/orders (POST/GET/PUT)`, order item reservation, publish `OrderCreated` events.

- Inventory.Api
  - Responsibilities: SKU/parts management, stock levels, suppliers, reservations/releases.
  - Implemented (skeleton): `/health`, `/inventory/sample`
  - To implement: `/inventory`, stock reservation endpoints, reprovisioning, supplier sync.

- Staff.Api
  - Responsibilities: staff profiles, skills, certifications, availability.
  - Implemented (skeleton): `/health`, `/staff/sample`
  - To implement: staff search by skill, availability calendar, shift assignments.

- Operations.Api
  - Responsibilities: convert orders and R&D recipes into work orders, scheduling, work order lifecycle, station routing.
  - Implemented (skeleton): `/health`, `/ops/schedule/sample`
  - To implement: work order CRUD, assignment algorithm, integration with Workers.

- RnD.Api
  - Responsibilities: store R&D logs, experiments, BOMs, process recipes, attachments.
  - Implemented (skeleton): `/health`, `/rnd/logs/sample`
  - To implement: ingest RnD documents, versioned recipes, approvals, schema validation in Mongo.

- Management.Api
  - Responsibilities: projects, milestones, approvals, recipe gating.
  - Implemented (skeleton): `/health`, `/management/projects/sample`
  - To implement: project lifecycle endpoints, document management, KPI dashboards.

- Workers
  - Responsibilities: background tasks: embedding generation, event consumers, SAGA orchestrator steps, retries, notifications.
  - Implemented (skeleton): host scaffold.
  - To implement: concrete hosted services for each background concern.

**Data model sketches (next steps: expand into EF Core & Mongo schemas)**

- Order (Postgres / EF Core)
  - `Order` { Id: Guid, CustomerId: Guid, Items: List<OrderItem>, Status: enum, CreatedAt: DateTime, FulfillmentAssignedTo }
  - `OrderItem` { ProductId, Quantity, ComponentParts[] }

- InventoryItem (Postgres)
  - `InventoryItem` { Id, SKU, PartNumber, QuantityOnHand, ReorderThreshold }

- StaffMember (Postgres)
  - `StaffMember` { Id, Name, Roles[], Skills[], Availability[] }

- RnDLog (Mongo)
  - Document with fields: `_id`, `title`, `authors`, `parts` (array), `configuration` (JSON), `results`, `attachments` (refs), `createdAt`, `version`.

Best practices:

- Use Value Objects for complex fields (address, monetary amounts, part references) in domain model.
- Maintain database migrations per service using `dotnet ef migrations` in service projects that use EF Core.

**CI/CD & Infra (recommended)**

- CI Pipeline per repo (GitHub Actions recommended): restore, build, test, image build, push to registry.
- CD: deploy to Kubernetes (Helm charts) or managed app services (ECS/Fargate, Azure App Service). Keep staging and prod clusters.
- Infra as Code: Terraform modules for VPC, managed Postgres (RDS), MongoDB Atlas (or managed instance), vector DB, Redis, and message broker.

**Security & Compliance**

- Auth: central Identity service (IdentityServer or managed Auth0/Okta) issuing JWTs. Services validate tokens and implement RBAC.
- Secrets: store in cloud secrets manager (AWS Secrets Manager / Azure Key Vault). Local dev use `.env` and dotfiles excluded from VCS.
- Data privacy: RnD attachments may contain IP-sensitive work — implement permissions and audit logs.

**Testing strategy**

- Unit tests per project (xUnit). Integration tests for cross-service flows (use testcontainers / docker-compose for local infra).
- Contract tests for APIs (Pact or OpenAPI-driven tests).

**Where we need to go (short actionable list)**

1. Wire projects into a top-level solution file (`dotnet sln add` all newly created projects).
2. Add EF Core to `Orders.Api` and `Inventory.Api` and create initial migrations + Postgres connection strings.
3. Implement domain models, DTOs, and mapping (AutoMapper or manual).
4. Implement event publishing & RabbitMQ/Kafka configuration across services.
5. Implement Workers with consumers for core events (OrderCreated → ReserveInventory → CreateWorkOrder).
6. Implement RnD ingestion endpoints and Mongo schemas; add validation and versioning.
7. Implement Management approval workflow to convert RnD recipes to production operations.
8. Add CI workflows and container image builds.
9. Add helm charts / terraform modules and provable staging infra.
10. Add tests and observability (OpenTelemetry) to each service.

**Risks & open decisions**

- Choice of message broker (RabbitMQ vs Kafka) affects delivery semantics and complexity.
- Vector DB selection for RnD search and ConsoleGenie integration (hosted vs self-hosted).
- How much to keep local-first for RnD & ConsoleGenie (privacy concerns).

**Ownership & next milestones**

- Short term (2–6 weeks): wire solutions, implement EF models for Orders & Inventory, basic event publish/consume flow to reserve inventory.
- Mid term (6–12 weeks): implement Operations work orders, basic scheduling UI, RnD ingestion and approval pipeline.
- Longer term (3–9 months): Management dashboard, robotic integration hooks, production-grade infra & monitoring.

If you approve, I will: (A) add the domain model classes and EF Core wiring for `Orders.Api` and `Inventory.Api`, (B) add `dotnet sln` wiring and initial Git commits, or (C) create GitHub Actions CI templates. Pick one and I'll implement it next.
