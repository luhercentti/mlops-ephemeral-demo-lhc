#!/usr/bin/env python3
import argparse
import boto3
import sagemaker
from sagemaker import get_execution_role
from sagemaker.model_monitor import ModelMonitor, DataCaptureConfig

def main():
    parser = argparse.ArgumentParser(description='Setup monitoring for a SageMaker endpoint')
    parser.add_argument('--endpoint-name', type=str, required=True, help='Endpoint name')
    parser.add_argument('--monitoring-schedule-name', type=str, required=True, help='Monitoring schedule name')
    parser.add_argument('--instance-type', type=str, default='ml.m5.xlarge', help='Instance type')
    parser.add_argument('--schedule', type=str, default='0 * ? * * *', help='Schedule expression (cron format)')
    
    args = parser.parse_args()
    
    # Setup SageMaker session
    sm_session = sagemaker.Session()
    role = get_execution_role()
    
    print(f"Setting up monitoring for endpoint: {args.endpoint_name}")
    
    # Enable data capture on the endpoint
    sm_client = boto3.client('sagemaker')
    
    # Update the endpoint to enable data capture if it's not already enabled
    endpoint_config_name = sm_client.describe_endpoint(EndpointName=args.endpoint_name)['EndpointConfigName']
    endpoint_config = sm_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
    
    # If data capture is not enabled, create a new endpoint config with data capture
    try:
        # Check if data capture is enabled
        data_capture_config = endpoint_config['DataCaptureConfig']
        print("Data capture is already enabled on the endpoint")
    except KeyError:
        # Create a new endpoint config with data capture
        print("Enabling data capture on the endpoint...")
        
        # Create data capture config
        data_capture_config = DataCaptureConfig(
            enable_capture=True,
            sampling_percentage=100,
            destination_s3_uri=f's3://my-mlops-demo-bucket-lhc/sentiment-analysis/datacapture'
        )
        
        # Create model monitor
        model_monitor = ModelMonitor(
            role=role,
            instance_count=1,
            instance_type=args.instance_type,
            volume_size_in_gb=20,
            max_runtime_in_seconds=3600
        )
        
        # Create the baseline constraints and statistics
        baseline_job = model_monitor.suggest_baseline(
            baseline_dataset='s3://my-mlops-demo-bucket-lhc/sentiment-analysis/data/train.csv',
            dataset_format=sagemaker.model_monitor.DatasetFormat.csv(header=True)
        )
        baseline_job.wait()
        
        # Get the baseline statistics and constraints
        baseline_statistics = baseline_job.baseline_statistics()
        baseline_constraints = baseline_job.suggested_constraints()
        
        # Setup the monitoring schedule
        model_monitor.create_monitoring_schedule(
            monitor_schedule_name=args.monitoring_schedule_name,
            endpoint_input=args.endpoint_name,
            statistics=baseline_statistics,
            constraints=baseline_constraints,
            schedule_cron_expression=args.schedule
        )
        
        print(f"Monitoring schedule created: {args.monitoring_schedule_name}")
    
if __name__ == '__main__':
    main()