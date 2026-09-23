# Fit report

Source: `phone/tools/fit_check.py` against `phone/spec/device.yaml`.

| bay | class | declared mm3 | computed mm3 | +clearance mm3 |
|---|---|---:|---:|---:|
| display | display | 27122.5 | 27122.5 | 33802.8 |
| battery | battery | 27744.0 | 27744.0 | 31059.3 |
| compute | compute | 4284.0 | 4284.0 | 5214.2 |
| camera-rear | camera-rear | 3146.0 | 3146.0 | 3626.4 |
| sensor-front | sensor-front | 400.0 | 400.0 | 516.9 |
| port | port | 1200.0 | 1200.0 | 1441.2 |
| radio | radio | 3037.5 | 3037.5 | 3627.9 |

- bays reported: 7
- bay volume: 66934.0 mm3
- structure volume: 15796.4 mm3
- used volume: 82730.4 mm3
- envelope volume: 131637.0 mm3
- margin: 48906.6 mm3
- P2 gate (used <= envelope): PASS
