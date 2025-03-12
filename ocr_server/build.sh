#!/bin/sh
set -e
GET_BUILD_TAG(){
	local TAG_NAME=`git rev-parse --short HEAD`
	if [ -z "${TAG_NAME}" ]
	then
		echo "only build for commit after tags"
		exit 0
	fi
	echo ${TAG_NAME}
}

IMAGE_BUILD(){
	local base_url=$1
	local tag=$2
	local file=$3
	local image_url="${base_url}:${tag}"
	echo "build images:${image_url}"
	docker build --network=host -t "${image_url}" -f ${file} . || exit -1
  echo "try push ....."
  docker push ${image_url} || exit -2
}

CI_IMAGE_BASE_URL="10.12.0.78:5000/data_works/ocr"

BUILD_TAG=$(GET_BUILD_TAG)

IMAGE_BUILD "${CI_IMAGE_BASE_URL}" "${BUILD_TAG}" ./Dockerfile


