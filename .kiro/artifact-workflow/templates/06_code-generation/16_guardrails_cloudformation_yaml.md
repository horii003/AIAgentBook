# スケルトン: ガードレール (guardrails/guardrails_cloudformation.yaml)


## 概要

AWS Bedrockのguardrailsにガードレールを設定するためのCloudFormationのYAMLを作成するためのテンプレート
設定した内容を .envに反映して利用する

## ファイル配置

`guardrails/guardrails_cloudformation.yaml`

---

## サンプルデータ

```yaml

AWSTemplateFormatVersion: "2010-09-09"
Description: 

Resources:
  ExpenseAgentGuardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      Name: "expense_agent"
      Description: "v1"

      BlockedInputMessaging: |
        その話題は有害または不適切である可能性があるため、情報を提供できません。
        安全にお手伝いできる別の内容についてご質問ください。

      BlockedOutputsMessaging: |
        そのような種類のコンテンツは、有害または不適切である可能性があるため生成できません。
        他にお手伝いできることがあればお知らせください。

      ContentPolicyConfig:
        ContentFiltersTierConfig:
          TierName: "STANDARD"
        FiltersConfig:
          - Type: "VIOLENCE"
            InputStrength: "HIGH"
            OutputStrength: "HIGH"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"

          - Type: "PROMPT_ATTACK"
            InputStrength: "HIGH"
            OutputStrength: "NONE"
            InputAction: "BLOCK"

          - Type: "MISCONDUCT"
            InputStrength: "HIGH"
            OutputStrength: "HIGH"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"

          - Type: "HATE"
            InputStrength: "HIGH"
            OutputStrength: "HIGH"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"

          - Type: "SEXUAL"
            InputStrength: "HIGH"
            OutputStrength: "HIGH"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"

          - Type: "INSULTS"
            InputStrength: "HIGH"
            OutputStrength: "HIGH"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"

      WordPolicyConfig:
        ManagedWordListsConfig:
          - Type: "PROFANITY"
            InputEnabled: true
            OutputEnabled: true
            InputAction: "BLOCK"
            OutputAction: "BLOCK"
        WordsConfig: []

      SensitiveInformationPolicyConfig:
        PiiEntitiesConfig:
          - Type: "CREDIT_DEBIT_CARD_CVV"
            InputEnabled: true
            OutputEnabled: true
            Action: "BLOCK"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"
        RegexesConfig: []

      CrossRegionConfig:
        GuardrailProfileArn: "arn:aws:bedrock:ap-northeast-1:869935080389:guardrail-profile/apac.guardrail.v1:0"

      Tags:
        - Key: "Name"
          Value: "expense_agent"
        - Key: "Region"
          Value: "ap-northeast-1"

Outputs:
  GuardrailId:
    Description: "Bedrock Guardrail のリソース ID"
    Value: !GetAtt ExpenseAgentGuardrail.GuardrailId
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailId"

  GuardrailArn:
    Description: "Bedrock Guardrail の ARN"
    Value: !GetAtt ExpenseAgentGuardrail.GuardrailArn
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailArn"

  GuardrailVersion:
    Description: "Bedrock Guardrail のバージョン"
    Value: !GetAtt ExpenseAgentGuardrail.Version
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailVersion"

```
