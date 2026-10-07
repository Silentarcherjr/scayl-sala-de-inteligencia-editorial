# B-11 · CI

Workflow `.github/workflows/ci.yml`: Python 3.12, dependencias core fijadas de requirements.txt,
pytest completo y Ruff 0.16.10 fijado. Solo permiso contents:read, sin secretos ni descarga de
modelos. Push/PR, badge en README. Configuración de comandos basada en la
[integración oficial de Ruff](https://docs.astral.sh/ruff/integrations/).

Validación local (Python 3.14 de esta máquina): **172 pytest pasan**, `ruff check tests` verde.
Correcciones en tests: imports, nombres que ocultaban builders y literales equivalentes;
no se eliminaron aserciones ni se desactivaron casos.

**Lint global pendiente:** 36 avisos (33 scayl, 2 app, 1 deploy), detallados en
`eval/results/b11-ruff.json`. Por instrucción del Lead solo se corrigieron tests, sin tocar
sus módulos. El workflow ejecuta `ruff check .` sin exclusions/ignores/continue-on-error:
seguirá rojo hasta corregir los avisos restantes. No se afirma CI global verde ni ejecución
remota Python 3.12 medida en esta máquina.
