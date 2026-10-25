.PHONY: generate detect test demo clean

generate:
	PYTHONPATH=src python -m cloudspend.generate

detect: generate
	PYTHONPATH=src python -m cloudspend.cli --input data/synthetic_gcp_billing.csv

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

demo: detect

clean:
	rm -f data/synthetic_gcp_billing.csv data/injected_anomalies.csv reports/anomalies.json

