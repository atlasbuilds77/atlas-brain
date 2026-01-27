#!/bin/bash
# =====================================================
# KRONOS DEPLOYMENT SCRIPT
# =====================================================
# Usage: ./deploy.sh [environment] [version]
# Example: ./deploy.sh production v1.2.3
# =====================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
AWS_REGION=${AWS_REGION:-us-west-2}
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Kronos Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Environment: ${ENVIRONMENT}"
echo "Version: ${VERSION}"
echo "Region: ${AWS_REGION}"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    echo -e "${RED}Error: Invalid environment. Use 'staging' or 'production'${NC}"
    exit 1
fi

# Production safety check
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${YELLOW}⚠️  WARNING: You are about to deploy to PRODUCTION${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# Function to check service health
check_health() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    echo "Checking health at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Service is healthy${NC}"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - waiting..."
        sleep 10
        ((attempt++))
    done
    
    echo -e "${RED}✗ Service failed health check${NC}"
    return 1
}

# Function to deploy a service
deploy_service() {
    local service=$1
    local cluster="kronos-${ENVIRONMENT}"
    
    echo -e "\n${YELLOW}Deploying $service...${NC}"
    
    aws ecs update-service \
        --cluster "$cluster" \
        --service "kronos-$service" \
        --force-new-deployment \
        --region "$AWS_REGION" \
        --output text
    
    echo "Waiting for $service to stabilize..."
    aws ecs wait services-stable \
        --cluster "$cluster" \
        --services "kronos-$service" \
        --region "$AWS_REGION"
    
    echo -e "${GREEN}✓ $service deployed successfully${NC}"
}

# Main deployment flow
main() {
    echo -e "\n${YELLOW}Step 1: Authenticate with ECR${NC}"
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ECR_REGISTRY"
    
    echo -e "\n${YELLOW}Step 2: Run database migrations${NC}"
    # Run migrations as a one-off ECS task
    aws ecs run-task \
        --cluster "kronos-${ENVIRONMENT}" \
        --task-definition "kronos-migrations-${ENVIRONMENT}" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
        --region "$AWS_REGION" \
        --output text
    
    echo "Waiting for migrations to complete..."
    sleep 30
    
    echo -e "\n${YELLOW}Step 3: Deploy services${NC}"
    deploy_service "backend"
    deploy_service "frontend"
    deploy_service "worker"
    
    echo -e "\n${YELLOW}Step 4: Verify deployment${NC}"
    if [ "$ENVIRONMENT" == "production" ]; then
        check_health "https://app.kronos.app"
    else
        check_health "https://staging.kronos.app"
    fi
    
    echo -e "\n${YELLOW}Step 5: Clear CDN cache${NC}"
    if [ "$ENVIRONMENT" == "production" ]; then
        # Invalidate CloudFront cache
        aws cloudfront create-invalidation \
            --distribution-id "${CLOUDFRONT_DISTRIBUTION_ID}" \
            --paths "/*" \
            --region "$AWS_REGION"
    fi
    
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Record deployment
    echo "{\"version\": \"$VERSION\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"environment\": \"$ENVIRONMENT\"}" | \
        aws s3 cp - "s3://kronos-deployments/${ENVIRONMENT}/deployment-$(date +%Y%m%d-%H%M%S).json"
}

main
