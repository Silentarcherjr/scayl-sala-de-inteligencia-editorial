.PHONY: install test fixture demo

install:
	pip install -r requirements.txt

test:
	python -m pytest -q

fixture:
	python scripts/make_ui_fixture.py

# Single reproducible run path (pipeline and app land in M1).
demo:
	python -m scayl.pipeline build --snapshot $${SCAYL_SNAPSHOT_DIR:-data/raw/v1}
	streamlit run app/Home.py
