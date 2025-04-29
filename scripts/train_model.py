#!/usr/bin/env python3
import argparse
import boto3
import json
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker import get_execution_role

def main():
    parser = argparse.ArgumentParser(description='Train a model using SageMaker')
    parser.add_argument('--bucket', type=str, required=True, help='S3 bucket name')
    parser.add_argument('--prefix', type=str, required=True, help='S3 prefix')
    parser.add_argument('--hyperparameters', type=str, required=True, help='JSON string of hyperparameters')
    parser.add_argument('--instance-type', type=str, default='ml.m5.xlarge', help='Training instance type')
    
    args = parser.parse_args()
    
    # Parse hyperparameters
    hyperparameters = json.loads(args.hyperparameters.replace("'", '"'))
    
    # Setup SageMaker session
    session = boto3.Session(region_name='us-east-1')
    sm_session = sagemaker.Session(session)
    role = get_execution_role()
    
    # Create the estimator
    sklearn_estimator = SKLearn(
        entry_point='train.py',
        role=role,
        instance_type=args.instance_type,
        instance_count=1,
        framework_version='0.23-1',
        hyperparameters=hyperparameters,
        output_path=f's3://{args.bucket}/{args.prefix}/output'
    )
    
    # Start training
    train_data_uri = f's3://{args.bucket}/{args.prefix}/data/train.csv'
    test_data_uri = f's3://{args.bucket}/{args.prefix}/data/test.csv'
    
    sklearn_estimator.fit({
        'train': train_data_uri,
        'test': test_data_uri
    })
    
    # Save the training job name for subsequent steps
    training_job_name = sklearn_estimator.latest_training_job.name
    with open('training_job_name.txt', 'w') as f:
        f.write(training_job_name)
    
    print(f"Training job completed: {training_job_name}")
    
if __name__ == '__main__':
    main()