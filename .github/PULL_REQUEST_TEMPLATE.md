## Summary

Describe what changed and why.

## Type of Change

- [ ] Documentation
- [ ] Harness CLI behavior
- [ ] Role or protocol update
- [ ] Tests
- [ ] Maintenance

## Validation

- [ ] `python3 .harness/test_harness_cli.py`
- [ ] `PYTHONPYCACHEPREFIX=/tmp/mindhandsharness_pycache python3 -m py_compile .harness/bin/harness.py .harness/test_harness_cli.py`
- [ ] `python3 .harness/bin/harness.py doctor`

## Notes

Mention any compatibility risks, migration notes, or follow-up work.

