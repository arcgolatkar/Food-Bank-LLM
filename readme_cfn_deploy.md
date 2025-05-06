aws ecr create-repository --repository-name foodbank-frontend-v2
aws ecr create-repository --repository-name foodbank-backend-v2

account_id = 727646504965


# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 727646504965.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t foodbank-backend-v2 .
docker tag foodbank-backend-v2:latest 727646504965.dkr.ecr.us-east-1.amazonaws.com/foodbank-backend-v2:latest
docker push 727646504965.dkr.ecr.us-east-1.amazonaws.com/foodbank-backend-v2:latest

# Build and push frontend
cd frontend
docker build -t foodbank-frontend-v2 .
docker tag foodbank-frontend-v2:latest 727646504965.dkr.ecr.us-east-1.amazonaws.com/foodbank-frontend-v2:latest
docker push 727646504965.dkr.ecr.us-east-1.amazonaws.com/foodbank-frontend-v2:latest

# List VPCs
aws ec2 describe-vpcs

vpcID = vpc-0e9988863d4f4c11b

# List subnets for your VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-0e9988863d4f4c11b"

"SubnetId": "subnet-00bb127e51d76631c",
"SubnetId": "subnet-03d6727c113ea0c80",
"SubnetId": "subnet-02ae40e988bb1c79c",
"SubnetId": "subnet-0e7baca72e0702301",
"SubnetId": "subnet-0c5b75b0f2732759c",
"SubnetId": "subnet-0448fc9b9083d3a42",

cd backend

aws cloudformation create-stack \
  --stack-name foodbank-backend-v3 \
  --template-body file://backend-template.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-0e9988863d4f4c11b \
    ParameterKey=PublicSubnet1,ParameterValue=subnet-02ae40e988bb1c79c \
    ParameterKey=PublicSubnet2,ParameterValue=subnet-0e7baca72e0702301 \
    ParameterKey=PrivateSubnet1,ParameterValue=subnet-02ae40e988bb1c79c \
    ParameterKey=PrivateSubnet2,ParameterValue=subnet-0e7baca72e0702301 \
    ParameterKey=OpenAIApiKey,ParameterValue=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 \
    ParameterKey=ECRRepositoryURI,ParameterValue=727646504965.dkr.ecr.us-east-1.amazonaws.com/foodbank-backend-v2 \
    ParameterKey=ContainerImage,ParameterValue=latest \
  --capabilities CAPABILITY_IAM


# Wait for backend stack to complete
aws cloudformation wait stack-create-complete --stack-name foodbank-backend-v3

# Get the backend URL output
aws cloudformation describe-stacks --stack-name foodbank-backend-v3 --query "Stacks[0].Outputs[?OutputKey=='BackendURL'].OutputValue" --output text

backendURL = http://backend-alb-2037475976.us-east-1.elb.amazonaws.com

cd ..
cd frontend

aws cloudformation create-stack \
  --stack-name foodbank-frontend-v9 \
  --template-body file://frontend-template.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-0e9988863d4f4c11b \
    ParameterKey=PublicSubnet1,ParameterValue=subnet-02ae40e988bb1c79c \
    ParameterKey=PublicSubnet2,ParameterValue=subnet-0e7baca72e0702301 \
    ParameterKey=ECRRepositoryURI,ParameterValue=727646504965.dkr.ecr.us-east-1.amazonaws.com/foodbank-frontend-v2 \
    ParameterKey=ContainerImage,ParameterValue=latest \
    ParameterKey=BackendURL,ParameterValue=http://backend-alb-2037475976.us-east-1.elb.amazonaws.com \
  --capabilities CAPABILITY_IAM