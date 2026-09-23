# Power budget report

Source: `phone/tools/power_budget.py`.

No rail carries a budget in `phone/spec/device.yaml` yet (P5); this report is informational, not a gate. Scenario module-activity levels are a modeling sketch (see `power_budget.py`'s `SCENARIOS`), and every mA figure traces back to an `[UNVERIFIED]` placeholder in `phone/spec/modules/*.yaml` (U5).

## idle

| rail | total mA | detail |
|---|---:|---|
| 1V8 | 150 | compute=typical:150mA |
| 3V3 | 195 | compute=typical:80mA, radio=typical:100mA, sensor-front=typical:15mA |
| VBAT | 700 | compute=typical:400mA, radio=typical:300mA |

## screen-on

| rail | total mA | detail |
|---|---:|---|
| 1V8 | 230 | compute=typical:150mA, display=typical:80mA |
| 3V3 | 345 | compute=typical:80mA, display=typical:150mA, radio=typical:100mA, sensor-front=typical:15mA |
| VBAT | 700 | compute=typical:400mA, radio=typical:300mA |

## video

| rail | total mA | detail |
|---|---:|---|
| 1V8 | 550 | compute=max:400mA, display=max:150mA |
| 3V3 | 715 | compute=max:200mA, display=max:400mA, radio=typical:100mA, sensor-front=typical:15mA |
| VBAT | 2300 | compute=max:2000mA, radio=typical:300mA |

## 5g-data

| rail | total mA | detail |
|---|---:|---|
| 1V8 | 230 | compute=typical:150mA, display=typical:80mA |
| 3V3 | 545 | compute=typical:80mA, display=typical:150mA, radio=max:300mA, sensor-front=typical:15mA |
| VBAT | 1900 | compute=typical:400mA, radio=max:1500mA |
