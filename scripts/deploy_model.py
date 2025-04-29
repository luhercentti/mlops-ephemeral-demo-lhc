#!/usr/bin/env python3
import argparse
import boto3
import sagemaker
from sagemaker import get_execution_role, ModelPackage

def main():
    parser = argparse.ArgumentParser(description='Deploy a model from SageMaker Model Registry')
    parser.add_argument('--model-package-arn', type=str, required=True, help='Model package ARN')
    parser.add_argument('--endpoint-name', type=str, required=True, help='Endpoint name')
    parser.add_argument('--instance-type', type=str, default='ml.t2.medium', help='Instance type')
    parser.add_argument('--instance-count', type=int, default=1, help='Instance count')
    
    args = parser.parse_args()
    
    # Setup SageMaker session
    sm_session = sagemaker.Session()
    role = get_execution_role()
    
    print(f"Deploying model package: {args.model_package_arn}")
    print(f"To endpoint: {args.endpoint_name}")
    
    # Create a deployable model from the model package
    model = ModelPackage(
        role=role,
        model_package_arn=args.model_package_arn,
        sagemaker_session=sm_session
    )
    
    # Check if endpoint already exists
    sm_client = boto3.client('sagemaker')
    try:
        sm_client.describe_endpoint(EndpointName=args.endpoint_name)
        endpoint_exists = True
    except sm_client.exceptions.ClientError:
        endpoint_exists = False
    
    # Deploy the model
    if endpoint_exists:
        print(f"Endpoint {args.endpoint_name} already exists, updating...")
        model.deploy(
            initial_instance_count=args.instance_count,
            instance_type=args.instance_type,
            endpoint_name=args.endpoint_name,
            update_endpoint=True
        )
    else:
        print(f"Creating new endpoint {args.endpoint_name}...")
        model.deploy(
            initial_instance_count=args.instance_count,
            instance_type=args.instance_type,
            endpoint_name=args.endpoint_name
        )
    
    print(f"Model deployed successfully to endpoint: {args.endpoint_name}")
    
if __name__ == '__main__':
    main()