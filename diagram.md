# ML Lifecycle Deployment

```mermaid
flowchart TD
    subgraph "GitHub Repository"
        A[ML Code] --> |Triggers| B[GitHub Actions Workflow]
        B --> |Script Execution| C1[train_model.py]
        B --> |Script Execution| C2[evaluate_model.py]
        B --> |Script Execution| C3[register_model.py]
        B --> |Script Execution| C4[deploy_model.py]
        B --> |Script Execution| C5[setup_monitoring.py]
    end

    subgraph "AWS Services"
        D[S3: Data Storage]
        E[SageMaker: Training Job]
        F[SageMaker: Model Evaluation]
        G[SageMaker: Model Registry]
        H[SageMaker: Endpoint]
        I[CloudWatch: Monitoring]
    end

    %% Data Flow Connections
    C1 -->|1. Upload data| D
    D -->|2. Read data| E
    C1 -->|3. Start training| E
    E -->|4. Output model| D
    C2 -->|5. Get metrics| F
    F -->|6. Evaluation results| D
    C3 -->|7. Register if quality threshold met| G
    C4 -->|8. Deploy approved model| H
    C5 -->|9. Setup monitoring| I
    I -->|10. Monitor for drift| H
    H -->|11. Capture inference data| D

    %% Inference Flow
    J[User/Application] -->|12. Request prediction| H
    H -->|13. Return prediction| J

    style D fill:#FFD2A5,stroke:#FF8000
    style E fill:#A5D4FF,stroke:#0066CC
    style F fill:#A5D4FF,stroke:#0066CC
    style G fill:#A5D4FF,stroke:#0066CC
    style H fill:#A5D4FF,stroke:#0066CC
    style I fill:#D5A5FF,stroke:#8000CC
