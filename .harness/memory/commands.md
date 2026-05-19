# Commands

## Test CLI
```bash
python3 .harness/test_harness_cli.py
```

## Compile Python
```bash
PYTHONPYCACHEPREFIX=/tmp/mindhandsharness_pycache python3 -m py_compile .harness/bin/harness.py .harness/test_harness_cli.py
```

## Check Harness Health
```bash
python3 .harness/bin/harness.py doctor
```

## Render Boot Context
```bash
python3 .harness/bin/harness.py context boot
```

## Update Project Map
```bash
python3 .harness/bin/harness.py map update
```
