# Food Bank LLM Chatbot - Automated Deployment

This project provides a Flask backend API and a Streamlit frontend UI to help users find nearby food banks. This README details the automated deployment process using AWS CloudFormation and AWS CodeCatalyst.

## Architecture Overview

*   **Frontend:** Streamlit application running in a Docker container on ECS Fargate. Accessed via an Application Load Balancer (ALB).
*   **Backend:** Flask API running in a Docker container on ECS Fargate. Accessed via a separate Application Load Balancer. Handles requests from the frontend, interacts with OpenAI, and processes data.
*   **Container Registry:** AWS ECR stores the Docker images for frontend and backend.
*   **Compute:** AWS ECS Fargate manages the container orchestration (serverless).
*   **Networking:** AWS VPC provides network isolation. Public subnets host ALBs and Fargate tasks.
*   **Security:** Security Groups control traffic flow. IAM Roles grant necessary permissions. Secrets Manager or SSM Parameter Store securely stores the OpenAI API Key.
*   **Logging:** CloudWatch Logs capture container logs.
*   **CI/CD:** AWS CodeCatalyst automates building images, pushing to ECR, and deploying updates to ECS upon commits to the main branch.

## Repository Structure

```
├── .codecatalyst/
│   └── workflows/
│       └── codecatalyst-workflow.yaml  <-- CI/CD Pipeline
├── cloudformation/                 <-- NEW: CloudFormation Templates
│   ├── cfn-network-security.yaml
│   ├── cfn-infra.yaml
│   ├── cfn-backend.yaml
│   └── cfn-frontend.yaml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ... (other backend files)
├── frontend/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   ├── Dockerfile
├── data/
│   └── ... (data files like data.csv)
└── README.md                       <-- This file
```

## Prerequisites

1.  **AWS Account:** An active AWS account.
2.  **AWS CLI:** Installed and configured with credentials having permissions to create the resources defined in the CloudFormation templates (VPC, EC2, ECS, ECR, ELB, IAM, CloudWatch Logs, SSM).
3.  **OpenAI API Key:** Obtain an API key from OpenAI.
4.  **Store OpenAI API Key:** Securely store your OpenAI API Key in **AWS Systems Manager Parameter Store** as a `SecureString` type parameter in your target AWS region.
    *   Example using AWS CLI (replace `your-key-here` and parameter name if needed):
        ```bash
        aws ssm put-parameter \
            --name "/foodbank/openai-api-key" \
            --value "your-key-here" \
            --type SecureString \
            --description "OpenAI API Key for Food Bank LLM" \
            --region us-east-1 # Replace with your region
        ```
    *   **Note down the exact parameter name** (e.g., `/foodbank/openai-api-key`). You'll need it for the backend stack deployment.
5.  **Docker:** (Optional for local testing) Install Docker if you want to build/run images locally.
6.  **CodeCatalyst Setup:** (If using CI/CD)
    *   A CodeCatalyst Space and Project.
    *   An AWS Account Connection configured in your CodeCatalyst Space settings.
    *   An Environment configured in your CodeCatalyst project, linked to the AWS Account Connection.

## Deployment using CloudFormation

Deploy the stacks sequentially as they have dependencies.

**Stack Deployment Order:**

1.  `cfn-network-security.yaml`
2.  `cfn-infra.yaml`
3.  `cfn-backend.yaml`
4.  `cfn-frontend.yaml`

**Deployment Commands (using AWS CLI):**

*(Replace `YourProjectName`, `YourOpenAIParameterName`, `your-region` and stack names if you customize)*

```bash
# 1. Deploy Network and Security
aws cloudformation deploy \
    --template-file cloudformation/cfn-network-security.yaml \
    --stack-name FoodBankLLM-NetworkSecurity \
    --parameter-overrides ProjectName=FoodBankLLM \
    --capabilities CAPABILITY_IAM \
    --region your-region

# 2. Deploy Infrastructure (ECR, Logs, Cluster)
aws cloudformation deploy \
    --template-file cloudformation/cfn-infra.yaml \
    --stack-name FoodBankLLM-Infra \
    --parameter-overrides ProjectName=FoodBankLLM \
    --region your-region

# 3. Deploy Backend Service
# NOTE: Wait for Infra stack to complete. Provide the SSM parameter name.
aws cloudformation deploy \
    --template-file cloudformation/cfn-backend.yaml \
    --stack-name FoodBankLLM-Backend \
    --parameter-overrides \
        ProjectName=FoodBankLLM \
        OpenAiApiKeyParameterName=/foodbank/openai-api-key \
        # Optional: Adjust DesiredCount, ContainerCpu, ContainerMemory if needed
    --capabilities CAPABILITY_IAM \
    --region your-region

# 4. Deploy Frontend Service
# NOTE: Wait for Backend stack to complete.
aws cloudformation deploy \
    --template-file cloudformation/cfn-frontend.yaml \
    --stack-name FoodBankLLM-Frontend \
    --parameter-overrides ProjectName=FoodBankLLM \
    --capabilities CAPABILITY_IAM \
    --region your-region

```

**Accessing the Application:**

*   After the `FoodBankLLM-Frontend` stack completes, find the `FrontendALBEndpoint` output. This is the URL to access the Streamlit application in your browser.
*   You can get outputs via the AWS Console or CLI:
    ```bash
    aws cloudformation describe-stacks --stack-name FoodBankLLM-Frontend --query "Stacks[0].Outputs[?OutputKey=='FrontendALBEndpoint'].OutputValue" --output text --region your-region
    ```

## CI/CD with CodeCatalyst

1.  **Push Code:** Ensure the `.codecatalyst/workflows/codecatalyst-workflow.yaml` file and the `cloudformation/` directory are committed and pushed to your CodeCatalyst source repository (`main` branch by default).
2.  **Configure Workflow Variables:**
    *   Go to your CodeCatalyst Project -> Environments. Select your target environment.
    *   Under "Environment variables" or "Environment secrets", add the required variables defined in the workflow YAML (`AWS_REGION`, `ECR_REPOSITORY_BACKEND_URI`, `ECR_REPOSITORY_FRONTEND_URI`, `ECS_CLUSTER_NAME`, `ECS_SERVICE_BACKEND_NAME`, `ECS_SERVICE_FRONTEND_NAME`). Get the ECR URIs, Cluster Name, and Service Names from the CloudFormation stack outputs.
3.  **Run Workflow:** The workflow should trigger automatically on pushes to `main`. It will:
    *   Log in to ECR.
    *   Build the backend and frontend Docker images.
    *   Tag the images.
    *   Push images to their respective ECR repositories.
    *   Update the backend ECS service, forcing a new deployment.
    *   Update the frontend ECS service, forcing a new deployment.

## Local Development

(Refer to the original backend/README.md and general Docker practices)

1.  Build images: `docker build -t foodbank-backend backend/`, `docker build -t foodbank-frontend frontend/`
2.  Run containers (requires setting environment variables, potentially network config): `docker run -p 5000:5000 -e OPENAI_API_KEY=your_key foodbank-backend`, `docker run -p 8501:8501 -e BACKEND_URL=http://host.docker.internal:5000/api/process foodbank-frontend` (adjust `BACKEND_URL` based on your Docker networking).

## Cleanup

To remove the deployed resources and stop incurring charges, delete the CloudFormation stacks **in reverse order** of creation:

```bash
aws cloudformation delete-stack --stack-name FoodBankLLM-Frontend --region your-region
aws cloudformation delete-stack --stack-name FoodBankLLM-Backend --region your-region
aws cloudformation delete-stack --stack-name FoodBankLLM-Infra --region your-region
aws cloudformation delete-stack --stack-name FoodBankLLM-NetworkSecurity --region your-region

# Also delete the SSM Parameter if no longer needed
aws ssm delete-parameter --name "/foodbank/openai-api-key" --region your-region
```

**Note:** Deleting ECR repositories might require manually deleting images first if they are present. CloudFormation might fail to delete non-empty repositories depending on the deletion policy (default is Retain).