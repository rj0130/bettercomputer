# Open questions for Rae

Async by default: each row has a default that executes past its decide-by date unless Rae says
otherwise. Class: REVERSIBLE (default executes) · NO-DEFAULT (work routes around it; money, third
parties, product promise).

| # | Question | Default | Decide-by | Class |
|---|---|---|---|---|
| Q1 | Does BC-1 stay a general-purpose smartphone, or should it converge with `../termphone` into one modular platform with a CLI-phone SKU? | Stay separate; BC-1 is the general-purpose handset. termphone could later be a display+input module SKU on the BC-Bus, tracked as an idea only | 2026-10-15 | REVERSIBLE |
| Q2 | Target price band for BC-1 (drives SoC tier, display tier). | Mid-range: BOM ceiling USD 260, retail target USD 549. Drives the BOM roll-up ceiling in `device.yaml` | 2026-10-15 | REVERSIBLE |
| Q3 | Primary OS image shipped to customers: mainline Linux or AOSP? | Both built; AOSP is the default first-boot image for a consumer, Linux is a one-command switch. Consumers need their banking apps | 2026-10-15 | REVERSIBLE |
| Q4 | Should Claude push commits to `github.com/rj0130/bettercomputer`? | No. Local commits only | — | NO-DEFAULT |
| Q5 | Install KiCad (about 1 GB) on this host for schematic capture in a later unit? | Not yet; electrical stays YAML/text until a board is laid out | 2026-10-15 | REVERSIBLE |
