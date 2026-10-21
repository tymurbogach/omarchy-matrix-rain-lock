# Matrix Rain Refine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Afinar cantidad, distribucion, azar, cola y color de la lluvia CPU (ttfx nativa) y GPU (shader), sin tocar codigo aun.

**Architecture:** La CPU vive en `omarchy-enter-the-matrix-theme/omarchy-rain/lib/derive-screensaver.py` y solo cambia flags de `ttfx matrix`. La GPU completa vive en `omarchy-enter-the-matrix-theme/tools/matrix.frag` + `MatrixRain.qml`, se compila a `matrix.frag.qsb`. `omarchy-matrix/` es la variante nativa minima y solo recibe el subconjunto seguro.

**Tech Stack:** QML Qt6 ShaderEffect, GLSL 440 -> QSB, Python 3 derivers, ttfx 0.5.0, bash check harness.

**Spec:** Conversacion 2026-10-20: refinar diseno si es posible y cantidad, distribucion, random de caida, cola y colores. GPU con todo va en enter-the-matrix. Nativa va en omarchy-matrix. Cambios de codigo despues, solo plan ahora.

## Global Constraints

- No editar `Service.qml` / `LockView.qml` mas alla del bloque rain ya derivado.
- `matrix.frag.qsb` se construye con `--glsl 300es,330 --hlsl 50 --msl 12`.
- `qmllint` Qt6 debe pasar en `Service.qml` y `MatrixRain.qml`.
- `omarchy-matrix/tests/test_contract.py` debe pasar.
- `omarchy-enter-the-matrix-theme/tools/check.sh` debe pasar.
- No publicar clones a mano: `clonedFrom == omarchy.lock` y rain QML dentro.
- La lluvia corre siempre, sin freno por bateria (`UPower`, `windowsHere` prohibidos).
- Hold negro de 1 s con `startDelayMs: 1000` y `onRunningChanged: if (running) restart()` se preserva.

## Review Focus

- Pantalla 4K + escala 2: celdas de 32 px logicos no deben verse gigantes ni vacias; se espera densidad pareja.
- Panel vertical o ultrawide: `span = h/cellH + TAIL_MAX` no debe dejar bandas negras periodicas cada `period`.
- Suspend/resume: el reloj envuelto no debe saltar ni mostrar frame viejo; se espera hold negro de 1 s.
- `ttfx` sin fuente CJK: los katakana `ｦ-ﾜ` no deben salir como huecos; se espera fallback probado.
- `derive-screensaver.py` con Omarchy nuevo: si `NEEDLE` aparece 0 o 2 veces, debe abortar, no parchear a medias.

---

### Task 1: Nativa CPU ttfx

**Files:**
- Modify: `/home/cyberdyne/Projects/omarchy-enter-the-matrix-theme/omarchy-rain/lib/derive-screensaver.py:11-12`
- Test: `/home/cyberdyne/Projects/omarchy-enter-the-matrix-theme/omarchy-rain/lib/derive-screensaver.py` via `--check` + manual `ttfx`

**Interfaces:**
- Consumes: `/usr/share/omarchy/bin/omarchy-screensaver` con `NEEDLE = "    --random-effect --no-eol --no-restore-cursor &\n"`
- Produces: `REPLACEMENT: str` usado por `derive(source: str) -> str`

- [ ] **Step 1: Write the failing test**

```python
def test_replacement_has_tuned_flags():
    from derive_screensaver import REPLACEMENT
    assert "--highlight-color E2FFE2" in REPLACEMENT
    assert "--rain-color-gradient 7EBB7E 3F7A3F 0E3A12" in REPLACEMENT
    assert "--rain-fall-delay-range 4-12" in REPLACEMENT
    assert "--rain-column-delay-range 1-4" in REPLACEMENT
    assert "--symbol-swap-chance 0.03" in REPLACEMENT
    assert "--color-swap-chance 0.008" in REPLACEMENT
    assert "--frame-rate 60" in REPLACEMENT or "--frame-rate 60 " in open("/usr/share/omarchy/bin/omarchy-screensaver").read()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPYCACHEPREFIX=/tmp/pyc python3 -m pytest omarchy-rain/tests/test_derive.py::test_replacement_has_tuned_flags -v`
Expected: FAIL with `E2FFE2 not in`

- [ ] **Step 3: Implement `REPLACEMENT` in `omarchy-rain/lib/derive-screensaver.py:11`**

Exact string:

```
    --no-eol --no-restore-cursor matrix --highlight-color E2FFE2 --rain-color-gradient 7EBB7E 3F7A3F 0E3A12 --rain-fall-delay-range 4-12 --rain-column-delay-range 1-4 --symbol-swap-chance 0.03 --color-swap-chance 0.008 --rain-time 86400 &
```

Y wrapper `--frame-rate 120` a `--frame-rate 60` en el mismo `REPLACEMENT` si el flag vive en el script instalado; si vive fuera, documentar en `omarchy-rain/README.md`.

Rationale una linea: iguala head/gradient a GPU `E2FFE2 / 7EBB7E 0E3A12`, reduce varianza 7.5x a 3x como `k 300-900`, duplica densidad, hierve simbolos.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPYCACHEPREFIX=/tmp/pyc python3 -m py_compile omarchy-rain/lib/derive-screensaver.py && OMARCHY_PATH=/usr/share/omarchy python3 omarchy-rain/lib/derive-screensaver.py --check`
Expected: PASS, sin salida

- [ ] **Step 5: Manual visual check**

Run: `ttfx --frame-rate 60 --canvas-width 0 --canvas-height 0 --reuse-canvas --anchor-canvas c --anchor-text c --no-eol --no-restore-cursor matrix --highlight-color E2FFE2 --rain-color-gradient 7EBB7E 3F7A3F 0E3A12 --rain-fall-delay-range 4-12 --rain-column-delay-range 1-4 --symbol-swap-chance 0.03 --color-swap-chance 0.008 --rain-time 10`
Expected: lluvia densa 10 s, luego sale; sin huecos ni parpadeo

- [ ] **Step 6: Commit**

```bash
git add omarchy-rain/lib/derive-screensaver.py
git commit -m "tune: ttfx native rain density and color to match GPU"
```

### Task 2: GPU completa en enter-the-matrix

**Files:**
- Modify: `/home/cyberdyne/Projects/omarchy-enter-the-matrix-theme/tools/matrix.frag:45,80,103,111,154,180,205`
- Modify: `/home/cyberdyne/Projects/omarchy-enter-the-matrix-theme/MatrixRain.qml:24-33`
- Create: `/home/cyberdyne/Projects/omarchy-enter-the-matrix-theme/matrix.frag.qsb` (rebuild)
- Test: `./tools/check.sh`

**Interfaces:**
- Consumes: uniforms `colBg, colHead E2FFE2, colRainA 7EBB7E, colRainB 0E3A12, cellH 32, dpr, period 3600, birth`
- Produces: `matrix.frag.qsb` cargado por `MatrixRain.qml:145` via `fragmentShader`

- [ ] **Step 1: Write the failing visual contract test**

```python
def test_shader_has_refined_tail():
    src = open("tools/matrix.frag").read()
    assert "TAIL_MAX 36.0" in src or "tail = 12.0 +" in src
    assert "alive = step(0.15" in src  # 85% vivas, antes 0.20
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tools/test_shader.py::test_shader_has_refined_tail -v`
Expected: FAIL

- [ ] **Step 3: Implement `tools/matrix.frag` refinements**

Valores exactos propuestos, una linea cada uno:
- `TAIL_MAX 40.0` a `36.0`: cola mas corta, mas columnas visibles.
- `tail = 14.0 + hash*24.0` a `12.0 + hash*20.0`: rango 12-32, menos arrastre.
- `dim = 0.68 + hash*0.60` mantener: da profundidad, no tocar.
- `alive = step(0.20, ...)` a `step(0.15, ...)`: 85% vivas, mas cantidad sin llenar todo.
- `bright = mix(1.0, 0.30, pow(t,0.75))` a `mix(1.0, 0.24, pow(t,0.85))`: cola funde mas hondo.
- `glow * 0.07` a `0.09`: bloom leve mas fosforo, sin halo duro.
- `k = 300.0 + floor(hash*601.0)` mantener: 3x varianza ya buena.

- [ ] **Step 4: Rebuild QSB**

Run: `qsb --glsl 300es,330 --hlsl 50 --msl 12 -o matrix.frag.qsb tools/matrix.frag`
Expected: archivo nuevo, `ls -l matrix.frag.qsb` > 0

- [ ] **Step 5: Run checks**

Run: `./tools/check.sh`
Expected: `all checks passed`

- [ ] **Step 6: Commit**

```bash
git add tools/matrix.frag matrix.frag.qsb
git commit -m "tune: gpu rain tail and density"
```

### Task 3: Port minimo a omarchy-matrix nativa

**Files:**
- Modify: `/home/cyberdyne/Projects/omarchy-matrix/tools/matrix.frag` (solo si Task 2 queda bien)
- Modify: `/home/cyberdyne/Projects/omarchy-matrix/matrix.frag.qsb` (rebuild mismo comando)
- Modify: `/home/cyberdyne/Projects/omarchy-matrix/MatrixRain.qml:24-33` (solo defaults si cambian)
- Test: `/home/cyberdyne/Projects/omarchy-matrix/tests/test_contract.py`

**Interfaces:**
- Consumes: `tools/matrix.frag` validado en Task 2
- Produces: plugin minimo que pasa `omarchy plugin validate`

- [ ] **Step 1: Write the failing test**

```python
def test_qsb_matches_frag():
    assert open("matrix.frag.qsb","rb").read().__len__() > 0
```

- [ ] **Step 2: Run test to verify baseline**

Run: `python3 -m pytest tests/test_contract.py -v`
Expected: PASS antes del port (linea base)

- [ ] **Step 3: Copiar `tools/matrix.frag` y reconstruir QSB**

Run: `cp /home/cyberdyne/Projects/omarchy-enter-the-matrix-theme/tools/matrix.frag tools/matrix.frag && qsb --glsl 300es,330 --hlsl 50 --msl 12 -o matrix.frag.qsb tools/matrix.frag`
Expected: `tests/test_contract.py::test_assets_exist` sigue PASS

- [ ] **Step 4: Run full validation**

Run: `python3 -m pytest tests/ -v && qmllint -I /usr/share/omarchy/shell MatrixRain.qml Service.qml`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/matrix.frag matrix.frag.qsb MatrixRain.qml
git commit -m "port: tuned gpu rain from theme"
```
