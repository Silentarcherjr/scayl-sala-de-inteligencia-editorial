# Relevo · <usuario> · <AAAA-MM-DD HH:MM UTC>

> Escrito por el agente de <usuario> antes de detenerse. El siguiente agente debe leer este archivo
> **antes** que cualquier otro (después de AGENTS.md y de `docs/agents/<usuario>.md`).

- **Motivo de la parada:** límite de sesión cercano (~15%) | el usuario lo pidió | bloqueo
- **Rama:** `worker-?/...` · **Último commit:** `<sha corto>` (empujado: sí/no)
- **PR abierto:** <url o "ninguno">

## Tarea en curso
<ID de tarea (p. ej., B-03)> — qué se está haciendo exactamente y en qué paso quedó.

## Hecho en esta sesión
- ...

## Siguiente paso concreto (lo primero que debe hacer el próximo agente)
1. ...
2. ...

## Estado de las pruebas
`python -m pytest -q` → <N passed / M failed>. Si algo falla: qué prueba y por qué (si se sabe).

## Archivos tocados
- `ruta` — qué cambió

## Bloqueos, dudas y decisiones pendientes
- ... (incluye propuestas abiertas en docs/AGENT_PROPOSALS.md)

## Contexto que no está en el código
- Supuestos, comandos útiles, datos descargados fuera del repo, variables de entorno usadas (sin valores secretos).
