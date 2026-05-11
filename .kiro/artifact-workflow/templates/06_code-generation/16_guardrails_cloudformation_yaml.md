# スケルトン: ガードレール (guardrails/guardrails_cloudformation.yaml)

## 概要

Amazon Bedrock Guardrails をデプロイするための CloudFormation テンプレート。
詳細設計書（ガードレール詳細設計.md）のガードレール定義をCFnリソースとして実装する。
設定した内容を .envに反映して利用する

## ファイル配置

`guardrails/guardrails_cloudformation.yaml`

---

## スケルトンコード

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: "エージェント用ガードレール"

Resources:
  BedrockGuardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      Name: "agent_guardrail"
      Description: "エージェント用ガードレール"

      # --- 入力ブロック時のフォールバック応答 ---
      # TODO: 詳細設計書のフォールバック応答（入力ブロック時）に置換
      BlockedInputMessaging: |
        {詳細設計書の入力ブロック時メッセージ}

      # --- 出力ブロック時のフォールバック応答 ---
      # TODO: 詳細設計書のフォールバック応答（出力ブロック時）に置換
      BlockedOutputsMessaging: |
        {詳細設計書の出力ブロック時メッセージ}

      # ============================================================
      # コンテンツポリシーフィルタ
      # ============================================================
      ContentPolicyConfig:
        ContentFiltersTierConfig:
          TierName: "STANDARD"
        FiltersConfig:
          # TODO: 詳細設計書のブロック条件に従いフィルタ種別を列挙
          #   有効な Type: VIOLENCE, HATE, SEXUAL, INSULTS, MISCONDUCT, PROMPT_ATTACK
          #   Strength: NONE, LOW, MEDIUM, HIGH
          #   Action: BLOCK, NONE
          - Type: "VIOLENCE"
            InputStrength: "HIGH"
            OutputStrength: "HIGH"
            InputAction: "BLOCK"
            OutputAction: "BLOCK"

          # 注意: PROMPT_ATTACK は入力側のみ。OutputStrength は "NONE" 固定、OutputAction は指定しない
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

      # ============================================================
      # 単語ポリシー
      # ============================================================
      WordPolicyConfig:
        ManagedWordListsConfig:
          - Type: "PROFANITY"
            InputEnabled: true
            OutputEnabled: true
            InputAction: "BLOCK"
            OutputAction: "BLOCK"
        # ※ カスタム単語がある場合のみ WordsConfig を追加する
        # WordsConfig:
        #   - Text: "禁止ワード"
        #     InputEnabled: true
        #     OutputEnabled: true
        #     InputAction: "BLOCK"
        #     OutputAction: "BLOCK"

      # ============================================================
      # センシティブ情報ポリシー
      # ============================================================
      SensitiveInformationPolicyConfig:
        PiiEntitiesConfig:
          # TODO: 詳細設計書の対象PII種別に従い列挙
          #   Action: BLOCK（検知時に応答全体を拒否）/ ANONYMIZE（プレースホルダに置換して応答を返す）/ NONE（検知のみ）
          #
          #   利用可能な Type 一覧:
          #   【個人情報 - 一般】
          #     ADDRESS              - 住所
          #     AGE                  - 年齢
          #     NAME                 - 氏名
          #     EMAIL                - メールアドレス
          #     PHONE                - 電話番号
          #     USERNAME             - ユーザー名
          #     PASSWORD             - パスワード
          #     DRIVER_ID            - 運転免許証番号
          #     LICENSE_PLATE        - ナンバープレート
          #     VEHICLE_IDENTIFICATION_NUMBER - 車両識別番号
          #   【金融情報】
          #     CREDIT_DEBIT_CARD_NUMBER  - クレジット/デビットカード番号
          #     CREDIT_DEBIT_CARD_CVV     - CVVコード
          #     CREDIT_DEBIT_CARD_EXPIRY  - カード有効期限
          #     PIN                       - PINコード
          #     BANK_ACCOUNT_NUMBER       - 銀行口座番号
          #     BANK_ROUTING              - 銀行ルーティング番号
          #     SWIFT_CODE                - SWIFTコード
          #   【医療情報】
          #     HEALTH_INSURANCE          - 健康保険情報
          #     MEDICAL_RECORD_NUMBER     - 診療記録番号
          #     MEDICATION                - 薬剤情報
          #     TREATMENT_INFORMATION     - 治療情報
          #   【米国固有】
          #     US_SOCIAL_SECURITY_NUMBER - 社会保障番号（SSN）
          #     US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER - 個人納税者番号（ITIN）
          #     US_PASSPORT_NUMBER        - パスポート番号
          #   【その他】
          #     IP_ADDRESS           - IPアドレス
          #     MAC_ADDRESS          - MACアドレス
          #     URL                  - URL
          #     AWS_ACCESS_KEY       - AWSアクセスキー
          #     AWS_SECRET_KEY       - AWSシークレットキー
          #     INTERNATIONAL_BANK_ACCOUNT_NUMBER - IBAN          
          - Type: "{PII種別}"
            Action: "BLOCK"
            InputEnabled: true
            OutputEnabled: true
            InputAction: "BLOCK"
            OutputAction: "BLOCK"
        # ※ カスタム正規表現がある場合のみ RegexesConfig を追加する
        # RegexesConfig:
        #   - Name: "{パターン名}"
        #     Description: "{パターンの説明}"        
        #     Pattern: "{正規表現}"
        #     Action: "BLOCK"
        #     InputEnabled: true
        #     OutputEnabled: true
        #     InputAction: "BLOCK"
        #     OutputAction: "BLOCK"

      # ============================================================
      # トピックポリシー（トピックポリシー定義がある場合のみ追加）
      # ============================================================
      # TopicPolicyConfig:
      #   TopicsConfig:
      #     - Name: "{トピック名}"
      #       Definition: "{トピックの定義文}"
      #       Type: "DENY"
      #       InputAction: "BLOCK"
      #       OutputAction: "BLOCK"
      #       Examples:
      #         - "{入力例1}"
      #         - "{入力例2}"

      # ============================================================
      # クロスリージョン設定
      # ============================================================
      CrossRegionConfig:
        GuardrailProfileArn: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:guardrail-profile/apac.guardrail.v1:0"

      Tags:
        - Key: "Name"
          Value: "{ガードレール名}"
        - Key: "Region"
          Value: "{リージョン}"

Outputs:
  GuardrailId:
    Description: "Bedrock Guardrail のリソース ID"
    Value: !GetAtt BedrockGuardrail.GuardrailId
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailId"

  GuardrailVersion:
    Description: "Bedrock Guardrail のバージョン"
    Value: !GetAtt BedrockGuardrail.Version
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailVersion"
```

## カスタマイズガイド

1. **プレースホルダ**: `{xxx}` は全て詳細設計書の対応する定義で置換する
2. **ContentPolicyConfig**: 詳細設計書のブロック条件に従いフィルタ種別を FiltersConfig に列挙する。`PROMPT_ATTACK` は入力側のみ（OutputStrength は `NONE` 固定、OutputAction は指定しない）
3. **SensitiveInformationPolicyConfig**: 詳細設計書の対象PII種別を PiiEntitiesConfig に列挙する。Action は設計書の要件に応じて `BLOCK`（全拒否）または `ANONYMIZE`（マスキング）を選択する
4. **オプショナルな配列プロパティ**: `WordsConfig`, `RegexesConfig`, `TopicPolicyConfig` 等は、使用する場合のみコメントを解除して記述する。
5. **TopicPolicyConfig**: 詳細設計書にトピックポリシーの定義がある場合のみコメントを解除して追加する
6. **詳細設計書に記載のないプロパティは追加しない**
