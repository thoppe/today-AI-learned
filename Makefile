features:
	python src/build_features.py

download_wikipedia:
	python src/wikipedia_dl.py

learn:
	python src/attribute_TIL.py 
	python src/build_decoy_db.py
	python src/train.py
	python src/score.py

report:
	python src/report.py

cross_ref:
	python src/cross_reference.py

best_time:
	python src/plot_times.py

full_clean:
	rm -rvf db
