#!/bin/bash
set -e

# AWS Deployment Script for Enterprise Compliance Filter
# Supports ECS, Elastic Beanstalk, and EKS deployments

echo "🚀 Deploying Enterprise Compliance Filter to AWS..."

# Configuration
APP_NAME="enterprise-compliance-filter"
REGION=${AWS_REGION:-us-east-1}
ENVIRONMENT=${ENVIRONMENT:-production}
DEPLOYMENT_TYPE=${DEPLOYMENT_TYPE:-ecs}  # ecs, eb, eks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Build and push Docker image to ECR
build_and_push_image() {
    print_status "Building and pushing Docker image to ECR..."
    
    # Get AWS account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
    IMAGE_URI="${ECR_URI}/${APP_NAME}:${VERSION:-latest}"
    
    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names $APP_NAME --region $REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $APP_NAME --region $REGION
    
    # Get login token for ECR
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI
    
    # Build Docker image
    print_status "Building Docker image..."
    docker build -t $APP_NAME:${VERSION:-latest} .
    docker tag $APP_NAME:${VERSION:-latest} $IMAGE_URI
    
    # Push to ECR
    print_status "Pushing to ECR..."
    docker push $IMAGE_URI
    
    print_success "Image pushed to $IMAGE_URI"
    echo "IMAGE_URI=$IMAGE_URI" > .env.deploy
}

# Deploy to ECS
deploy_ecs() {
    print_status "Deploying to Amazon ECS..."
    
    # Load image URI
    source .env.deploy
    
    # Create ECS cluster if it doesn't exist
    aws ecs describe-clusters --clusters $APP_NAME-cluster --region $REGION 2>/dev/null || \
    aws ecs create-cluster --cluster-name $APP_NAME-cluster --region $REGION
    
    # Create task definition
    cat > task-definition.json << EOF
{
    "family": "$APP_NAME",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048",
    "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "$APP_NAME",
            "image": "$IMAGE_URI",
            "portMappings": [
                {
                    "containerPort": 5000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "FLASK_ENV", "value": "production"},
                {"name": "DATABASE_URL", "value": "\${DATABASE_URL}"},
                {"name": "REDIS_URL", "value": "\${REDIS_URL}"},
                {"name": "SECRET_KEY", "value": "\${SECRET_KEY}"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$APP_NAME",
                    "awslogs-region": "$REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "python healthcheck.py"],
                "interval": 30,
                "timeout": 10,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOF
    
    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json --region $REGION
    
    # Create or update service
    SERVICE_EXISTS=$(aws ecs describe-services --cluster $APP_NAME-cluster --services $APP_NAME --region $REGION --query 'services[0].status' --output text 2>/dev/null)
    
    if [ "$SERVICE_EXISTS" = "ACTIVE" ]; then
        print_status "Updating existing ECS service..."
        aws ecs update-service --cluster $APP_NAME-cluster --service $APP_NAME --task-definition $APP_NAME --region $REGION
    else
        print_status "Creating new ECS service..."
        aws ecs create-service \
            --cluster $APP_NAME-cluster \
            --service-name $APP_NAME \
            --task-definition $APP_NAME \
            --desired-count 2 \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
            --region $REGION
    fi
    
    print_success "ECS deployment completed"
}

# Deploy to Elastic Beanstalk
deploy_eb() {
    print_status "Deploying to AWS Elastic Beanstalk..."
    
    # Check if EB CLI is installed
    if ! command -v eb &> /dev/null; then
        print_error "Elastic Beanstalk CLI not found. Install it with: pip install awsebcli"
        exit 1
    fi
    
    # Create Dockerrun.aws.json for EB
    cat > Dockerrun.aws.json << EOF
{
    "AWSEBDockerrunVersion": "1",
    "Image": {
        "Name": "$IMAGE_URI",
        "Update": "true"
    },
    "Ports": [
        {
            "ContainerPort": "5000"
        }
    ],
    "Environment": [
        {"Name": "FLASK_ENV", "Value": "production"},
        {"Name": "PORT", "Value": "5000"}
    ]
}
EOF
    
    # Initialize EB application if not exists
    if [ ! -f .elasticbeanstalk/config.yml ]; then
        eb init $APP_NAME --platform docker --region $REGION
    fi
    
    # Deploy
    eb deploy $ENVIRONMENT --staged
    
    print_success "Elastic Beanstalk deployment completed"
}

# Deploy to EKS
deploy_eks() {
    print_status "Deploying to Amazon EKS..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl first."
        exit 1
    fi
    
    # Load image URI
    source .env.deploy
    
    # Create Kubernetes manifests
    mkdir -p k8s
    
    # Deployment manifest
    cat > k8s/deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $APP_NAME
  labels:
    app: $APP_NAME
spec:
  replicas: 3
  selector:
    matchLabels:
      app: $APP_NAME
  template:
    metadata:
      labels:
        app: $APP_NAME
    spec:
      containers:
      - name: $APP_NAME
        image: $IMAGE_URI
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: $APP_NAME-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: $APP_NAME-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
EOF
    
    # Service manifest
    cat > k8s/service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: $APP_NAME-service
spec:
  selector:
    app: $APP_NAME
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
EOF
    
    # Apply manifests
    kubectl apply -f k8s/
    
    print_success "EKS deployment completed"
}

# Setup AWS resources
setup_resources() {
    print_status "Setting up AWS resources..."
    
    # Create RDS instance for PostgreSQL
    print_status "Creating RDS PostgreSQL instance..."
    aws rds create-db-instance \
        --db-instance-identifier $APP_NAME-db \
        --db-instance-class db.t3.micro \
        --engine postgres \
        --master-username postgres \
        --master-user-password ${DB_PASSWORD:-CompliantDB2025!} \
        --allocated-storage 20 \
        --vpc-security-group-ids sg-12345 \
        --region $REGION \
        2>/dev/null || print_warning "RDS instance might already exist"
    
    # Create ElastiCache Redis cluster
    print_status "Creating ElastiCache Redis cluster..."
    aws elasticache create-cache-cluster \
        --cache-cluster-id $APP_NAME-redis \
        --cache-node-type cache.t3.micro \
        --engine redis \
        --num-cache-nodes 1 \
        --region $REGION \
        2>/dev/null || print_warning "Redis cluster might already exist"
    
    print_success "AWS resources setup completed"
}

# Main deployment function
main() {
    print_status "Starting AWS deployment for $APP_NAME"
    print_status "Environment: $ENVIRONMENT"
    print_status "Deployment Type: $DEPLOYMENT_TYPE"
    print_status "Region: $REGION"
    
    check_prerequisites
    
    # Setup resources if requested
    if [ "$SETUP_RESOURCES" = "true" ]; then
        setup_resources
    fi
    
    build_and_push_image
    
    case $DEPLOYMENT_TYPE in
        "ecs")
            deploy_ecs
            ;;
        "eb")
            deploy_eb
            ;;
        "eks")
            deploy_eks
            ;;
        *)
            print_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    print_success "🎉 AWS deployment completed successfully!"
    print_status "Check AWS console for deployment status"
}

# Run main function
main "$@"