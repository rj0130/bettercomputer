# BetterComputer — Product Vision

## Executive Summary

BetterComputer is a circular-tech e-commerce and operations platform that offers rapid, modular device refactoring and upgrade services. We collect, test, and reconfigure device components to provide customers with high-quality, upgradable devices at lower cost and reduced waste.

## Target Users

- Eco-conscious consumers and hobbyists wanting modular, repairable devices.
- Educational institutions and community organizations seeking affordable computing resources.
- Internal operations, technicians, and R&D staff who manage teardown recipes, assembly, and quality control.

## Core Value Proposition

- Sustainable, repairable hardware delivered faster than OEM refresh cycles.
- A tightly integrated software platform connecting storefront orders → inventory → R&D recipes → operations scheduling → management oversight.

## Key Features (MVP → Future)

- Public storefront with product pages, cart, and checkout (MVP).
- Orders and Inventory services with SKU- and component-level tracking (MVP).
- Staff and scheduling app to assign technicians and work orders (MVP+).
- R&D logging and recipe management in a document store for structured process definitions (Alpha).
- SAGA-driven orchestration for multi-step fulfillment and inventory reconciliation (Beta).
- Integration hooks for robotic assembly and automated test stations (Future).

## Differentiators

- Emphasis on part-level modular upgrades and rapid turnaround.
- R&D-to-operations workflow that converts experiments into machine-readable assembly recipes.
- Local-first tooling for technicians with tight feedback loops between operations and R&D.

## Success Metrics

- Throughput: number of devices refactored per week.
- Cycle time: intake → assembly → dispatch lead time.
- Yield: percent of devices passing QA after refactor.
- Customer satisfaction and repeat purchase rate.

## GTM & Business Notes

- Target local markets and partner repair cafes/education centers for initial deployment.
- Consider grants or non-profit partnerships for community programs.

## Next steps (technical)

1. Finalize data model for order → BOM → recipe mapping.
2. Implement EF Core models for Orders & Inventory and initial Postgres infra.
3. Implement event bus for OrderCreated → ReserveParts → CreateWorkOrder flows.
4. Build minimal storefront and admin dashboard for operations.

File location: this document is in the repository root for visibility.
