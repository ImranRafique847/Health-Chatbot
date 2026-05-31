# ============================================================
# Deploy Healthcare Chatbot to AWS Lambda (Docker Container)
# ============================================================
# Prerequisites:
#   1. AWS CLI installed and configured
#   2. Docker Desktop running
#   3. Your AWS account has Bedrock access enabled
#
# Run: .\deploy.ps1
# ============================================================

$AWS_REGION = "us-east-1"
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REPO = "healthcare-chatbot"
$LAMBDA_FUNCTION = "healthcare-chatbot"
$IMAGE_TAG = "latest"

Write-Host "============================================"
Write-Host "  Deploying Healthcare Chatbot to AWS Lambda"
Write-Host "============================================"
Write-Host ""
Write-Host "  Account: $ACCOUNT_ID"
Write-Host "  Region:  $AWS_REGION"
Write-Host ""

# Step 1: Create ECR repository (if not exists)
Write-Host "Step 1: Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION 2>$null
$ECR_URI = "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"
Write-Host "  ECR: $ECR_URI"

# Step 2: Login to ECR
Write-Host ""
Write-Host "Step 2: Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Step 3: Build Docker image
Write-Host ""
Write-Host "Step 3: Building Docker image..."
docker build -t "${ECR_REPO}:${IMAGE_TAG}" .

# Step 4: Tag and push to ECR
Write-Host ""
Write-Host "Step 4: Pushing to ECR..."
docker tag "${ECR_REPO}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"
docker push "${ECR_URI}:${IMAGE_TAG}"

# Step 5: Create IAM role for Lambda (if not exists)
Write-Host ""
Write-Host "Step 5: Creating IAM role..."

$TRUST_POLICY = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

$TRUST_POLICY | Out-File -FilePath trust-policy.json -Encoding utf8
aws iam create-role --role-name lambda-healthcare-chatbot --assume-role-policy-document file://trust-policy.json 2>$null

# Attach policies
aws iam attach-role-policy --role-name lambda-healthcare-chatbot --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name lambda-healthcare-chatbot --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

Write-Host "  Waiting 10s for role propagation..."
Start-Sleep -Seconds 10

# Step 6: Create or update Lambda function
Write-Host ""
Write-Host "Step 6: Creating Lambda function..."

$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/lambda-healthcare-chatbot"

$EXISTS = aws lambda get-function --function-name $LAMBDA_FUNCTION 2>$null
if ($EXISTS) {
    Write-Host "  Updating existing function..."
    aws lambda update-function-code --function-name $LAMBDA_FUNCTION --image-uri "${ECR_URI}:${IMAGE_TAG}"
} else {
    Write-Host "  Creating new function..."
    aws lambda create-function `
        --function-name $LAMBDA_FUNCTION `
        --package-type Image `
        --code "ImageUri=${ECR_URI}:${IMAGE_TAG}" `
        --role $ROLE_ARN `
        --timeout 120 `
        --memory-size 512 `
        --environment "Variables={AWS_REGION=$AWS_REGION,MODEL_ID=amazon.nova-lite-v1:0}"
}

# Step 7: Create Function URL (public access)
Write-Host ""
Write-Host "Step 7: Creating public Function URL..."
aws lambda add-permission --function-name $LAMBDA_FUNCTION --statement-id FunctionURLAllowPublicAccess --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type NONE 2>$null

$URL_CONFIG = aws lambda create-function-url-config --function-name $LAMBDA_FUNCTION --auth-type NONE 2>$null
if (-not $URL_CONFIG) {
    $URL_CONFIG = aws lambda get-function-url-config --function-name $LAMBDA_FUNCTION
}

$FUNCTION_URL = ($URL_CONFIG | ConvertFrom-Json).FunctionUrl

# Cleanup
Remove-Item trust-policy.json -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "============================================"
Write-Host "  DEPLOYMENT COMPLETE!"
Write-Host "============================================"
Write-Host ""
Write-Host "  Your chatbot is live at:"
Write-Host "  $FUNCTION_URL"
Write-Host ""
Write-Host "  Share this URL with anyone!"
Write-Host "============================================"
