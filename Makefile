features:
	python src/build_features.py

download_wikipedia:
	python src/wikipedia_dl.py

learn:
	python src/attribute_TIL.py 
	python src/build_decoy_db.py
	python src/train.py
	python src/score.py

full_clean:
	rm -rvf db
