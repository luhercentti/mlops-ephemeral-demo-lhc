# ML Deployment Diagram

flowchart TD
    %% Starting point
    start(("Trigger: Push/PR\nto Main Branch"))
    
    %% Sequential Flow with numbering
    start --> step1["1. GitHub Actions Workflow Starts"]
    
    %% Job 1: Train Model - Sequential steps
    step1 --> step2["2. Checkout Code"]
    step2 --> step3["3. Configure AWS"]
    step3 --> step4["4. Upload Data to S3"]
    step4 --> step5["5. Train Model with SageMaker"]
    step5 --> step6["6. Save Training Job Info"]
    
    %% Job 2: Evaluate Model - Sequential steps
    step6 --> step7["7. Download Training Info"]
    step7 --> step8["8. Evaluate Model Performance"]
    step8 --> decision{"9. Accuracy > 0.8?"}
    
    %% Branching based on decision
    decision -->|No| end1["Pipeline Stops"]
    decision -->|Yes| step10["10. Upload Evaluation Results"]
    
    %% Job 3: Register Model - Sequential steps
    step10 --> step11["11. Download Evaluation Results"]
    step11 --> step12["12. Register Model in SageMaker Registry"]
    step12 --> step13["13. Save Model Package ARN"]
    
    %% Job 4: Deploy Model - Sequential steps
    step13 --> step14["14. Download Model Info"]
    step14 --> step15["15. Deploy Model to Endpoint"]
    step15 --> step16["16. Setup Monitoring"]
    step16 --> step17["17. Pipeline Complete"]
    
    %% User interaction starts after deployment
    step17 --> step18["18. User Makes Prediction Requests"]
    
    %% AWS Services supporting the flow (shown on right)
    step4 -.-> s3[(S3 Bucket\nmy-mlops-demo-bucket-lhc)]
    step5 -.-> sm1[SageMaker Training\nml.m5.xlarge]
    step8 -.-> sm2[SageMaker Evaluation]
    step12 -.-> sm3[SageMaker Model Registry\nSentimentAnalysisModels]
    step15 -.-> sm4[SageMaker Endpoint\nsentiment-analysis-endpoint]
    step16 -.-> mon[CloudWatch Monitoring\nHourly Schedule]

    %% Styling
    classDef process fill:#d4f1f9,stroke:#05386b,stroke-width:1px,color:black
    classDef decision fill:#ffccbc,stroke:#ff5722,stroke-width:1px,color:black
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:1px,color:black
    classDef endpoint fill:#e8f5e9,stroke:#388e3c,stroke-width:1px,color:black
    
    class step1,step2,step3,step4,step5,step6,step7,step8,step10,step11,step12,step13,step14,step15,step16,step17,step18 process
    class decision decision
    class s3,sm1,sm2,sm3,sm4,mon aws
    class end1 endpoint
 
``` 

s3 bucket:

my-mlops-demo-bucket


Detailed Data Flow Explanation

Data Preparation & Storage

The sample data (train.csv and test.csv) is stored in your GitHub repository
When the GitHub Actions workflow runs, it uploads these files to an S3 bucket
S3 maintains versioning of these files, allowing you to track data changes


Training Pipeline

GitHub Actions triggers the training script (train_model.py)
The script creates a SageMaker training job using the scikit-learn container
Data is fetched from S3 by SageMaker for training
The model is trained according to your hyperparameters
The resulting model artifacts are stored back in S3


Evaluation Process

The evaluate_model.py script retrieves the trained model's metrics
It analyzes metrics like accuracy, precision, recall, and F1 score
Results are stored in a JSON file, which is passed to the next stage
A quality threshold is checked (e.g., accuracy > 0.8) to determine if the model should proceed


Model Registration

If the model passes quality checks, register_model.py registers it in the SageMaker Model Registry
The model is stored with its metadata, including performance metrics
The Model Registry maintains versions and approval status of different models


Deployment Phase

deploy_model.py creates or updates a SageMaker endpoint with the approved model
The endpoint provides a REST API for real-time inference
If an endpoint already exists, it's updated rather than creating a new one


Monitoring Setup

setup_monitoring.py configures CloudWatch monitoring for the endpoint
Data capture is enabled to collect inference data
Baselines are established for detecting data drift
Scheduled monitoring jobs check for model performance degradation


Inference Flow

External applications send prediction requests to the SageMaker endpoint
The endpoint processes these requests using the deployed model
Predictions are returned to the calling application
Inference data is captured for monitoring



Key Components and Their Roles

GitHub Actions: Orchestrates the entire workflow, passing artifacts between jobs
S3: Central storage for datasets, model artifacts, and evaluation results
SageMaker Training: Executes the machine learning training job in a managed environment
SageMaker Model Registry: Tracks model versions and approval status
SageMaker Endpoints: Hosts models for real-time inference
CloudWatch: Monitors model performance and detects data drift

Sample Data Explanation

train.csv: Contains 100 customer reviews with sentiment labels (1=positive, 0=negative)
test.csv: Contains 30 additional reviews for testing model performance

Both files have two columns:

review_text: The customer review text
sentiment: Binary sentiment label (1 for positive, 0 for negative)

This dataset is perfect for our sentiment analysis example because:

It's simple enough to understand quickly
It demonstrates text classification, a common ML task
The balanced classes (positive/negative) help with model evaluation
It's realistic enough to show meaningful results



Check AWS Console to see the created resources:

SageMaker training jobs
SageMaker models and endpoints
CloudWatch monitoring configurations