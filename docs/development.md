# Development and tests

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[agent,test]'
pytest
ruff check .
```

The unit tests cover data ingestion, version-change events and collector output. Run an integration test against a disposable NetBox 4.5.x instance before production; the test settings are not a substitute for NetBox's full Django app registry.
