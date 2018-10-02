
.PHONY: help
help:
	@echo "\nCamera Gyroscope Make Usage"
	@echo "-----------------------------------------------------------------"
	@echo "make install --------- install required libraries for gyroscope"
	@echo "make install_demo ---- install required libraries for demo"
	@echo "make run ------------- run main test script"
	@echo "make demo ------------ run demo script"
	@echo "\n"

.PHONY: install
install:
	cat requirements.txt | xargs -n 1 pip install
	conda install -c menpo opencv


.PHONY: install_demo
install_demo:
	cat demo_requirements.txt | xargs -n 1 pip install
	conda install -c menpo opencv
	conda install pyopengl

.PHONY: run
run:
	python ./python/camera_gyro.py

.PHONY: demo
demo:
	python ./python/visualize.py
