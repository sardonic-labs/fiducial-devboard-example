# fiducial-devboard-example

Experiment: hand a **fresh AI agent** a blank repository with [fiducial](fiducial/) mounted as a submodule, and see how well it designs a devboard when steering + verification tooling are present from the first turn.

## Layout

```
fiducial/   verification skills submodule (MIT) — instruction library +
            zero-dependency checkers: lint → erc → check-intent → drc → render
```

## How to work here

1. Read `fiducial/AGENTS.md` and `fiducial/README.md` before anything else.
2. Write design intent as `intent.csv` (`ref,pin,expected_net`) from the datasheet **before** wiring the schematic.
3. Author the schematic under fiducial's rules; gate every step: `lint → erc → check-intent`; exit codes are gates, not suggestions.
4. Only after all checks pass: layout, `drc` until clean, `render`, inspect.

## Brief

*TBD — Oliver drops the design brief here.*
