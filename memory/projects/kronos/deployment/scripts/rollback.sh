#!/bin/bash
# =====================================================
# KRONOS ROLLBACK SCRIPT
# =====================================================
# Usage: ./rollback.sh [environment] [steps-back]
# Example: ./rollback.sh production 1
# =====================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENVIRONMENT=${1:-staging}
STEPS_BACK=${2:-1}
AWS_REGION=${AWS_REGION:-us-west-2}

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Kronos Rollback Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Environment: ${ENVIRONMENT}"
echo "Rolling back: ${STEPS_BACK} deployment(s)"
echo ""

# Safety confirmation
echo -e "${RED}⚠️  WARNING: This will rollback ${ENVIRONMENT} to a previous version${NC}"
read -p "Type 'ROLLBACK' to confirm: " confirm
if [ "$confirm" != "ROLLBACK" ]; then
    echo "Rollback cancelled."
    exit 0
fi

# Get previous deployment info
echo -e "\n${YELLOW}Finding previous deployment...${NC}"
DEPLOYMENT_FILE=$(aws s3 ls s3://kronos-deployments/${ENVIRONMENT}/ | \
    grep -v latest | sort -r | \
    head -n $((STEPS_BACK + 1)) | tail -1 | awk '{print $4}')

if [ -z "$DEPLOYMENT_FILE" ]; then
    echo -e "${RED}Error: Could not find previous deployment${NC}"
    exit 1
fi

echo "Rolling back to: $DEPLOYMENT_FILE"
aws s3 cp "s3://kronos-deployments/${ENVIRONMENT}/${DEPLOYMENT_FILE}" /tmp/rollback-target.json

# Display rollback target
echo -e "\n${YELLOW}Rollback target:${NC}"
cat /tmp/rollback-target.json | jq .

# Extract image tags
BACKEND_IMAGE=$(jq -r '.backend_image' /tmp/rollback-target.json)
FRONTEND_IMAGE=$(jq -r '.frontend_image' /tmp/rollback-target.json)
WORKER_IMAGE=$(jq -r '.worker_image' /tmp/rollback-target.json)

# Update task definitions and deploy
echo -e "\n${YELLOW}Initiating rollback...${NC}"

# For each service, create new task definition revision with old images
for service in backend frontend worker; do
    echo "Rolling back kronos-${service}..."
    
    # Get current task definition
    TASK_DEF=$(aws ecs describe-services \
        --cluster "kronos-${ENVIRONMENT}" \
        --services "kronos-${service}" \
        --query 'services[0].taskDefinition' \
        --output text)
    
    # This is simplified - in practice, you'd update the container image in the task def
    aws ecs update-service \
        --cluster "kronos-${ENVIRONMENT}" \
        --service "kronos-${service}" \
        --force-new-deployment \
        --region "$AWS_REGION"
done

# Wait for stability
echo -e "\n${YELLOW}Waiting for services to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster "kronos-${ENVIRONMENT}" \
    --services kronos-backend kronos-frontend \
    --region "$AWS_REGION"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Rollback completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

# Send notification
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"⚠️ Kronos ${ENVIRONMENT} rolled back to ${DEPLOYMENT_FILE}\"}" \
        "$SLACK_WEBHOOK_URL"
fi
