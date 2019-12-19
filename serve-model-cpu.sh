#export SERVING_MODEL=resnet
export SERVING_MODEL=faster_rcnn_resnet50_coco
docker run -t --rm -p 8501:8501 -p 8500:8500 -v $(realpath $PWD/models):/models --name object_detection_service -e MODEL_NAME=$SERVING_MODEL tensorflow/serving:1.12.0