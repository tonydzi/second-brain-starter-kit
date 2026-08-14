---
name: tt-probe
description: >
  E2E probe marker for the fleet-skill-autonomy pipeline (created for a one-off verification).
  Do not invoke — it's a test marker; the writer may delete it after verification.
permissions: [filesystem]
risk_level: inert
processes_untrusted_data: false
disable-model-invocation: true
origin: MAC-1
license: MIT
---

# tt-probe — маркер end-to-end промоушена

Единственная задача файла: пройти путь local-скилл → гейт → писатель (Якорь) → общий набор → синк на все машины.
Если ты читаешь это в `skills/tt-probe/` на любой машине флота — конвейер автономии скиллов РАБОТАЕТ.
Проба: PROBE-41ac669a-20260716.
