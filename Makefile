.PHONY: install test fixture demo ping precompute public-bundle

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

# --- Demo machine (frictionspp-svg: AMD RX 9060 XT 8 GB / Vulkan, Ollama running) ---
ping:            ## warm-up + latency of the local model
	python -m scayl.gen.llm ping

precompute:      ## LLM claims + Story Studio for the top events; fills data/cache/llm/
	python -m scayl.pipeline build --snapshot $${SCAYL_SNAPSHOT_DIR:-data/raw/v1} --llm live --top 15

public-bundle:   ## hosted demo: reuse cached outputs, strip RSS descriptions
	python -m scayl.pipeline build --snapshot $${SCAYL_SNAPSHOT_DIR:-data/raw/v1} --llm cache --top 15 --public

demo-offline:    ## video/rehearsal: public bundle + cached LLM outputs, no internet, no build
	python scripts/demo_offline.py
