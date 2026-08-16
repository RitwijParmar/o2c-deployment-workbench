.PHONY: run dashboard test mcp

run:
	PYTHONPATH=src python -m o2c_workbench.cli --project-root .

dashboard:
	PYTHONPATH=src streamlit run app.py

test:
	PYTHONPATH=src pytest -q

mcp:
	PYTHONPATH=src python -m o2c_workbench.mcp_server --transport stdio

