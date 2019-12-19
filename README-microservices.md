# nuclear-crack-inspection-pipeline



## Instructions for quick development setup

### Running services

Step 1. Run ElasticSearch, InfluxDB, Grafana, Kibana and Video Streamer services.

```bash
cd services
./up.sh
```

Step 2. Serve a ML model.

```bash
export SERVING_MODEL=febrero-cpu-friendly_weights
export DOCKER_SERVICE_NAME=cracks-classifier-service
```

Option 1) with CPU:

```bash
docker run -t --rm -p 8501:8501 -p 8500:8500 -v $(realpath $PWD/models):/models --name $DOCKER_SERVICE_NAME -e MODEL_NAME=$SERVING_MODEL tensorflow/serving:1.12.0
```

Option 2) with GPU:

```bash
docker run -t --rm --runtime=nvidia -p 8501:8501 -p 8500:8500 -v $(realpath $PWD/models):/models --name $DOCKER_SERVICE_NAME -e MODEL_NAME=$SERVING_MODEL tensorflow/serving:1.12.0-gpu
```

Step 3. Run development docker.

```bash
docker run -it --rm --runtime=nvidia -v $(realpath $PWD):/tf/notebooks --name tensorflowdev1 --network="host" nhorro/tensorflow1.12-py3-jupyter-opencv:latest
```

### Monitoring output

Video feed: http://localhost:5000/video_feed

Grafana: http://localhost:3000

Kibana: http://localhost:5601

### Grafana configuration

### Kibana configuration



## Project organization

```
./
|-downloads
|-media
|-services
|-misc
|-models
	|-faster_rcnn_resnet50_coco
	|-
|-src
	|-components
	|-notebooks
	|-pipelines
		|-
README.md

```

## Usage

