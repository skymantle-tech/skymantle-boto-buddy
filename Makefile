lintAndAnalysis:
	hatch run _ruff
	hatch run _bandit
	hatch run _black

setup:
	pip install --upgrade pip
	pip install hatch 
	hatch env create default