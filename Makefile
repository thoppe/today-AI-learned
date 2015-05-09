download_wikipedia:
	python src/wikipedia_dl.py

all:
	python attribute_TIL.py 
	python build_decoy_db.py
	python train.py
	python score.py

full_clean:
	rm -rvf db
