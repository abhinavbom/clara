AMZ_LINUX_VERSION:=2
current_dir := $(shell pwd)
container_dir := /opt/app
circleci := ${CIRCLECI}

all: archive

clean:
	rm -rf compile/lambda.zip

archive: clean
ifeq ($(circleci), true)
	docker create -v $(container_dir) --name src alpine:3.4 /bin/true
	docker cp $(current_dir)/. src:$(container_dir)
	docker run --rm -ti \
		--volumes-from src \
		amazonlinux:$(AMZ_LINUX_VERSION) \
		/bin/bash -c "cd $(container_dir) && ./build_lambda.sh"
else
	docker run --rm -ti \
		-v $(current_dir):$(container_dir) \
		amazonlinux:$(AMZ_LINUX_VERSION) \
		/bin/bash -c "cd $(container_dir) && ./build_lambda.sh"
endif
