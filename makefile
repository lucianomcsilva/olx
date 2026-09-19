all: login build push
build_push: build push
login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 132733789290.dkr.ecr.us-east-1.amazonaws.com/tricarros-olx
build:
	docker build -t tricarros-olx . --platform=linux/amd64  
#	docker build -t tricarros-olx . --platform=linux/arm64  
build_arm:
	docker build -t tricarros-olx-arm64 . --platform=linux/arm64  
push:	
	docker tag tricarros-olx 132733789290.dkr.ecr.us-east-1.amazonaws.com/tricarros-olx:latest
	docker push 132733789290.dkr.ecr.us-east-1.amazonaws.com/tricarros-olx:latest     
run_aws:
	aws ecs run-task --cluster TricarrosCluster-olx --task-definition TriCarrosScrapOlx  --launch-type="FARGATE"  --network-configuration '{ "awsvpcConfiguration": { "assignPublicIp":"ENABLED", "securityGroups": ["sg-05c9b3a0217ee5857"], "subnets": ["subnet-05b3091efed4c75b3"]}}' --overrides '{ "containerOverrides": [{"name": "tricarros-olx", "command": ["usr/local/bin/scrapy","crawl","olx_spider"], "environment": [{"name": "AWS_DEFAULT_REGION", "value": "us-east-1"}, {"name": "SESSION", "value": "52e7bee7-6673-4f63-9045-7de2e0e9d5ab"}, {"name": "TASKNO", "value": "go"}]}]}'
run:
	scrapy crawl olx_spider