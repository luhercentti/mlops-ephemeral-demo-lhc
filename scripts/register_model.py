#!/usr/bin/env python3
import argparse
import boto3
import json
import sagemaker
from sagemaker import get_execution_role
from sagemaker.model_metrics import MetricsSource, ModelMetrics

def main():
    parser = argparse.ArgumentParser(description='Register a model in the SageMaker Model Registry')
    parser.add_argument('--training-job-name', type=str, required=True, help='Training job name')
    parser.add_argument('--model-package-group-name', type=str, required=True, help='Model package group name')
    parser.add_argument('--evaluation-file', type=str, required=True, help='Path to evaluation metrics file')
    
    args = parser.parse_args()
    
    # Setup clients
    sm_client = boto3.client('sagemaker')
    s3_client = boto3.client('s3')
    sm_session = sagemaker.Session()
    role = get_execution_role()
    
    # Get training job info
    training_job = sm_client.describe_training_job(TrainingJobName=args.training_job_name)
    model_data_url = training_job['ModelArtifacts']['S3ModelArtifacts']
    image_uri = training_job['AlgorithmSpecification']['TrainingImage']
    
    # Create model package group if it doesn't exist
    try:
        sm_client.create_model_package_group(
            ModelPackageGroupName=args.model_package_group_name,
            ModelPackageGroupDescription='Sentiment Analysis Models'
        )
        print(f"Created model package group: {args.model_package_group_name}")
    except sm_client.exceptions.ResourceInUse:
        print(f"Model package group {args.model_package_group_name} already exists")
    
    # Upload evaluation metrics to S3
    with open(args.evaluation_file, 'r') as f:
        metrics = json.load(f)
    
    bucket = 'my-mlops-demo-bucket-lhc'
    metrics_key = f'sentiment-analysis/metrics/{args.training_job_name}/evaluation.json'
    
    s3_client.put_object(
        Body=json.dumps(metrics),
        Bucket=bucket,
        Key=metrics_key
    )
    
    metrics_s3_uri = f's3://{bucket}/{metrics_key}'
    
    # Create model metrics
    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=metrics_s3_uri,
            content_type='application/json'
        )
    )
    
    # Create model package
    model_package_response = sm_client.create_model_package(
        ModelPackageGroupName=args.model_package_group_name,
        ModelPackageDescription=f'Sentiment analysis model from job {args.training_job_name}',
        ModelApprovalStatus='Approved',
        InferenceSpecification={
            'Containers': [
                {
                    'Image': image_uri,
                    'ModelDataUrl': model_data_url
                }
            ],
            'SupportedContentTypes': ['text/csv'],
            'SupportedResponseMIMETypes': ['text/csv']
        },
        ModelMetrics=model_metrics
    )
    
    # Save model package ARN for deployment
    model_package_arn = model_package_response['ModelPackageArn']
    with open('model_package_arn.txt', 'w') as f:
        f.write(model_package_arn)
    
    print(f"Registered model package: {model_package_arn}")
    
if __name__ == '__main__':
    main()