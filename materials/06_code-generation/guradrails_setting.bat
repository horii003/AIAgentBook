@echo off
chcp 65001 >nul
setlocal

REM ===== 設定（読者が編集する箇所） =====
set ACCOUNT_ID=111111111111
set PROFILE=aiagent-tutorial
set REGION=ap-northeast-1
set LOG_GROUP_NAME=bedrock-log-aiagent-tutorial
set ROLE_NAME=irl-bedrock-log-aiagent-tutorial
set POLICY_NAME=ipl-bedrock-log-aiagent-tutorial
set STACK_NAME=bedrock-guardrail-stack
set GUARDRAIL_NAME=expense-reimbursement-guardrail
REM ========================================

echo [Step 1] ロググループ作成...
aws logs create-log-group --log-group-name %LOG_GROUP_NAME% --region %REGION% --profile %PROFILE%
if %errorlevel% equ 0 (echo   → 完了) else (echo   → 既に存在するためスキップ)

echo [Step 2] IAMロール作成...
aws iam create-role --role-name %ROLE_NAME% --assume-role-policy-document {\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"bedrock.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]} --profile %PROFILE%
if %errorlevel% equ 0 (echo   → 完了) else (echo   → 既に存在するためスキップ)

echo [Step 3] IAMポリシーアタッチ...
aws iam put-role-policy --role-name %ROLE_NAME% --policy-name %POLICY_NAME% --policy-document {\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Resource\":\"arn:aws:logs:%REGION%:%ACCOUNT_ID%:log-group:%LOG_GROUP_NAME%:log-stream:aws/bedrock/modelinvocations\"}]} --profile %PROFILE%
if %errorlevel% equ 0 (echo   → 完了) else (echo   → 失敗)

echo IAMロールの反映を待機中（8秒）...
timeout /t 8 /nobreak >nul

echo [Step 4] Bedrockログ設定...
aws bedrock put-model-invocation-logging-configuration --region %REGION% --profile %PROFILE% --logging-config {\"cloudWatchConfig\":{\"logGroupName\":\"%LOG_GROUP_NAME%\",\"roleArn\":\"arn:aws:iam::%ACCOUNT_ID%:role/%ROLE_NAME%\"},\"textDataDeliveryEnabled\":true,\"imageDataDeliveryEnabled\":true,\"embeddingDataDeliveryEnabled\":true}
if %errorlevel% equ 0 (echo   → 完了) else (echo   → 失敗)

echo [Step 5] ガードレール作成（CloudFormation）...
python -c "import sys,boto3;s=boto3.Session(profile_name='%PROFILE%');c=s.client('cloudformation',region_name='%REGION%');stacks=[x['StackName'] for x in c.list_stacks(StackStatusFilter=['CREATE_COMPLETE','UPDATE_COMPLETE','ROLLBACK_COMPLETE'])['StackSummaries']];exists='%STACK_NAME%' in stacks;t=open(r'%~dp0..\..\artifacts\06_code-generation\src\guardrails\guardrails_cloudformation.yaml',encoding='utf-8').read() if not exists else '';c.create_stack(StackName='%STACK_NAME%',TemplateBody=t,Capabilities=['CAPABILITY_NAMED_IAM']) if not exists else None;sys.exit(1 if exists else 0)"
if %errorlevel% equ 0 (echo   → スタック作成開始) else (echo   → 既に存在するためスキップ)

echo スタック作成完了を待機中...
aws cloudformation wait stack-create-complete --stack-name %STACK_NAME% --region %REGION% --profile %PROFILE% 2>nul
if %errorlevel% equ 0 (echo   → スタック作成完了) else (echo   → スタック作成に失敗しました)

echo [Step 6] ガードレールID取得...
for /f "tokens=*" %%a in ('aws bedrock list-guardrails --region %REGION% --profile %PROFILE% --query "guardrails[?name=='%GUARDRAIL_NAME%'].id" --output text') do set GUARDRAIL_ID=%%a

echo ===============================
echo ガードレールID: %GUARDRAIL_ID%
echo ===============================
echo.
echo .env に以下を設定してください:
echo GUARDRAIL_ID=%GUARDRAIL_ID%

endlocal