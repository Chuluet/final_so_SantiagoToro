#!/bin/bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 517178430674.dkr.ecr.us-east-1.amazonaws.com

docker build --platform linux/amd64 --provenance=false -t final_santiagotoro .

docker tag final_santiagotoro:latest 517178430674.dkr.ecr.us-east-1.amazonaws.com/final_santiagotoro:latest

docker push 517178430674.dkr.ecr.us-east-1.amazonaws.com/final_santiagotoro:latest