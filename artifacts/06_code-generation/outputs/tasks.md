# 螳溯｣・ち繧ｹ繧ｯ險育判

## 蜈ｱ騾壼盾辣ｧ隕冗ｴ・- `.kiro/steering/00_rule_directory_structure.md`
- `.kiro/steering/00_rule_project_conventions.md`
- `.kiro/steering/00_rule_code_review_checklist.md`

---

## 繧ｿ繧ｹ繧ｯ01: 繝・・繧ｿ繝｢繝・Ν螳夂ｾｩ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝・・繧ｿ繝｢繝・Ν隧ｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/莠､騾夊ｲｻ險育ｮ励ヤ繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/逕ｳ隲区嶌逕滓・繝・・繝ｫ隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/01_skeleton_data_models.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/models/data_models.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_data_models.py`
- **螳溯｣・・螳ｹ**:
  - 蜈ｱ騾壹ヰ繝ｪ繝・・繧ｿ繝ｼ髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ: `validate_station_name`, `validate_transport_type`, `validate_expense_category`, `validate_date_format`
  - 繝槭せ繧ｿ繝・・繧ｿ繝｢繝・Ν繧貞ｮ夂ｾｩ縺吶ｋ: `TrainFareRecord`, `FixedFareRecord`
  - 繝・・繝ｫ蜈･蜉帙Δ繝・Ν繧貞ｮ夂ｾｩ縺吶ｋ: `TransportCalculatorInput`, `TransportItem`, `TransportFormInput`, `ExpenseItem`, `ExpenseFormInput`
  - 繝・・繝ｫ蜃ｺ蜉帙Δ繝・Ν繧貞ｮ夂ｾｩ縺吶ｋ: `TransportCalculatorOutput`, `TransportFormOutput`, `ExpenseFormOutput`
  - 蜷・Δ繝・Ν縺ｫ `field_validator` 繧帝←逕ｨ縺吶ｋ・医Λ繝繝繝ｩ繝・ヱ繝ｼ遖∵ｭ｢縲～classmethod(validate_xxx)` 繧堤峩謗･貂｡縺呻ｼ・  - invocation_state縺ｯ霎樊嶌繝ｪ繝・Λ繝ｫ縺ｧ貂｡縺吶◆繧√∝ｰら畑Pydantic繝｢繝・Ν・・nvocationState遲会ｼ峨・螳夂ｾｩ縺励↑縺・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-020縲・30: 蜷・Δ繝・Ν縺ｮ豁｣蟶ｸ邉ｻ繝ｻ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ逡ｰ蟶ｸ邉ｻ繝ｻ蠅・阜蛟､繝・せ繝・  - 莠､騾壽焔谿ｵ縺ｮ陦ｨ險倥ｆ繧梧ｭ｣隕丞喧・・"train"` 竊・`"髮ｻ霆・`・・  - 鬧・錐謗･蟆ｾ隱樣勁蜴ｻ・・"譚ｱ莠ｬ鬧・` 竊・`"譚ｱ莠ｬ"`・・  - 邨瑚ｲｻ蛹ｺ蛻・・陦ｨ險倥ｆ繧梧ｭ｣隕丞喧・・"莠句漁逕ｨ蜩・` 竊・`"莠句漁逕ｨ蜩∬ｲｻ"`・・  - 蟇ｾ蠢懷､紋ｺ､騾壽焔谿ｵ繝ｻ邨瑚ｲｻ蛹ｺ蛻・〒ValidationError逋ｺ逕・  - 雋縺ｮ驥鷹｡阪〒ValidationError逋ｺ逕溘・蜀・〒騾夐℃

---

## 繧ｿ繧ｹ繧ｯ02: Bedrock繝｢繝・Ν險ｭ螳・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繧ｬ繝ｼ繝峨Ξ繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/02_skeleton_model_config.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/config/model_config.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_model_config.py`
- **螳溯｣・・螳ｹ**:
  - `ModelConfig` 繧ｯ繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ
  - `DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"` 繧定ｨｭ螳壹☆繧・  - `GUARDRAIL_ID` 縺ｯ迺ｰ蠅・､画焚 `GUARDRAIL_ID` 縺九ｉ蜿門ｾ励☆繧・  - `GUARDRAIL_VERSION` 縺ｯ迺ｰ蠅・､画焚 `GUARDRAIL_VERSION`・医ョ繝輔か繝ｫ繝・ `"DRAFT"`・峨°繧牙叙蠕励☆繧・  - `get_model()` 縺ｫ `@classmethod` 縺ｨ `@lru_cache(maxsize=1)` 繧帝←逕ｨ縺励※BedrockModel繧定ｿ斐☆
  - `guardrail_trace="enabled"` 繧定ｨｭ螳壹☆繧・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `get_model()` 縺・`BedrockModel` 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧定ｿ斐☆縺薙→
  - `get_model()` 縺悟酔荳繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧定ｿ斐☆縺薙→・・ru_cache縺ｫ繧医ｋ繧ｭ繝｣繝・す繝･・・
---

## 繧ｿ繧ｹ繧ｯ03: 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥虚菴懊ヱ繝ｩ繝｡繝ｼ繧ｿ險ｭ螳・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/逕ｳ隲句女莉倡ｪ灘哨繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/莠､騾夊ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/邨瑚ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/15_skeleton_settings.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/config/settings.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_settings.py`
- **螳溯｣・・螳ｹ**:
  - `_AgentSettings(BaseSettings)` 蝓ｺ蠎輔け繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ・・ax_iterations=10, max_attempts=6, initial_delay=4, max_delay=240・・  - `OrchestratorSettings(_AgentSettings)` 繧貞ｮ夂ｾｩ縺吶ｋ・・indow_size=30, max_turn_count=30, max_input_length=500, env_prefix="ECAAS_ORCHESTRATOR_"・・  - `TransportAgentSettings(_AgentSettings)` 繧貞ｮ夂ｾｩ縺吶ｋ・・indow_size=20, deadline_months=3, approval_threshold=10000, env_prefix="ECAAS_TRANSPORT_"・・  - `ExpenseAgentSettings(_AgentSettings)` 繧貞ｮ夂ｾｩ縺吶ｋ・・indow_size=20, deadline_months=3, approval_threshold=5000, env_prefix="ECAAS_EXPENSE_"・・  - `_Settings` 髮・ｴ・け繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺励～settings = _Settings()` 繧偵Δ繧ｸ繝･繝ｼ繝ｫ繝ｬ繝吶Ν縺ｧ螳夂ｾｩ縺吶ｋ
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `settings.orchestrator.window_size` 縺・0縺ｧ縺ゅｋ縺薙→
  - `settings.transport_agent.deadline_months` 縺・縺ｧ縺ゅｋ縺薙→
  - `settings.transport_agent.approval_threshold` 縺・0000縺ｧ縺ゅｋ縺薙→
  - `settings.expense_agent.deadline_months` 縺・縺ｧ縺ゅｋ縺薙→
  - `settings.expense_agent.approval_threshold` 縺・000縺ｧ縺ゅｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ04: 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝上Φ繝峨Λ繝ｼ隧ｳ邏ｰ險ｭ險・md`・・art 1: ErrorHandler・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/03_skeleton_error_handler.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/handlers/error_handler.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_error_handler.py`
- **螳溯｣・・螳ｹ**:
  - `ErrorHandler` 繧ｯ繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ・亥・繝｡繧ｽ繝・ラ縺ｯ `@staticmethod`縲√う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ蛹紋ｸ崎ｦ・ｼ・  - 蜈ｱ騾壹お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝｡繧ｽ繝・ラ繧貞ｮ溯｣・☆繧・ `handle_keyboard_interrupt`, `handle_loop_limit_error`, `handle_validation_error`, `handle_runtime_error`, `handle_unexpected_error`
  - 繝峨Γ繧､繝ｳ蝗ｺ譛峨お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝｡繧ｽ繝・ラ繧貞ｮ溯｣・☆繧・ `handle_throttling_error`, `handle_max_tokens_error`, `handle_context_window_error`, `handle_fare_data_error`, `handle_calculation_error`, `handle_file_save_error`
  - `handle_validation_error` 縺ｯ `error.errors()` 縺九ｉ繝輔ぅ繝ｼ繝ｫ繝牙錐繝ｻ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ繧呈歓蜃ｺ縺励※譌･譛ｬ隱槭Γ繝・そ繝ｼ繧ｸ繧堤函謌舌☆繧・  - 繝ｭ繧ｰ蜃ｺ蜉帙・陦後ｏ縺ｪ縺・ｼ亥他縺ｳ蜃ｺ縺怜・縺ｮ雋ｬ蜍呻ｼ・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-040縲・42: ValidationError繝ｻLoopLimitError繝ｻ莠域悄縺励↑縺・ｾ句､悶〒譌･譛ｬ隱槭Γ繝・そ繝ｼ繧ｸ縺瑚ｿ斐ｋ縺薙→
  - 蜷・`handle_*` 繝｡繧ｽ繝・ラ縺檎ｩｺ縺ｧ縺ｪ縺・律譛ｬ隱樊枚蟄怜・繧定ｿ斐☆縺薙→
  - `ErrorHandler` 繧偵う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ蛹悶○縺壹↓髱咏噪蜻ｼ縺ｳ蜃ｺ縺励〒縺阪ｋ縺薙→



---

## 繧ｿ繧ｹ繧ｯ05: ReAct繝ｫ繝ｼ繝怜宛蠕｡繝輔ャ繧ｯ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝上Φ繝峨Λ繝ｼ隧ｳ邏ｰ險ｭ險・md`・・art 2: LoopControlHook・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/04_skeleton_loop_control_hook.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/handlers/loop_control_hook.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_loop_control_hook.py`
- **螳溯｣・・螳ｹ**:
  - `LoopLimitError(Exception)` 繧ｫ繧ｹ繧ｿ繝萓句､悶け繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ・・urrent_iteration, max_iterations, agent_name 繝輔ぅ繝ｼ繝ｫ繝会ｼ・  - `LoopControlHook(HookProvider)` 繧ｯ繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ・・ax_iterations=10, agent_name="Agent"・・  - `register_hooks` 縺ｧ6縺､縺ｮ繧､繝吶Φ繝医↓繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ繧堤匳骭ｲ縺吶ｋ・・registry.add_callback()` 繧剃ｽｿ逕ｨ・・  - `_handle_before_invocation`: 繝ｫ繝ｼ繝励き繧ｦ繝ｳ繧ｿ繧・縺ｫ繝ｪ繧ｻ繝・ヨ
  - `_handle_before_model_call`: 繝ｫ繝ｼ繝怜屓謨ｰ繧棚NFO繝ｭ繧ｰ蜃ｺ蜉・  - `_handle_after_model_call`: `event.exception` 縺悟ｭ伜惠縺吶ｋ蝣ｴ蜷医・繧ｹ繧ｭ繝・・縲√き繧ｦ繝ｳ繧ｿ繧､繝ｳ繧ｯ繝ｪ繝｡繝ｳ繝医∽ｸ企剞繝√ぉ繝・け縺ｧLoopLimitError逋ｺ逕・  - `_handle_before_tool_call` / `_handle_after_tool_call`: `_get_tool_name(event)` 繝倥Ν繝代・縺ｧ繝・・繝ｫ蜷榊叙蠕励＠縺ｦINFO繝ｭ繧ｰ蜃ｺ蜉・  - `_handle_after_invocation`: 蜷郁ｨ医Ν繝ｼ繝怜屓謨ｰ繧棚NFO繝ｭ繧ｰ蜃ｺ蜉幢ｼ医Μ繧ｻ繝・ヨ縺励↑縺・ｼ・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-043縲・45: 繝ｫ繝ｼ繝嶺ｸ企剞譛ｪ貅縺ｧ繧ｨ繝ｩ繝ｼ縺ｪ縺励∽ｸ企剞蛻ｰ驕斐〒LoopLimitError逋ｺ逕・  - BeforeInvocationEvent縺ｧ繧ｫ繧ｦ繝ｳ繧ｿ縺・縺ｫ繝ｪ繧ｻ繝・ヨ縺輔ｌ繧九％縺ｨ
  - AfterModelCallEvent縺ｧevent.exception縺悟ｭ伜惠縺吶ｋ蝣ｴ蜷医↓繧ｫ繧ｦ繝ｳ繝医い繝・・縺後せ繧ｭ繝・・縺輔ｌ繧九％縺ｨ
  - AfterInvocationEvent縺ｧ繧ｫ繧ｦ繝ｳ繧ｿ縺後Μ繧ｻ繝・ヨ縺輔ｌ縺ｪ縺・％縺ｨ

---

## 繧ｿ繧ｹ繧ｯ06: 繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ謇ｿ隱阪い繝繝励ち繝ｼ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝上Φ繝峨Λ繝ｼ隧ｳ邏ｰ險ｭ險・md`・・art 3: HumanApprovalHook・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/05_skeleton_human_approval_hook.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/handlers/console_approval_adapter.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_console_approval_adapter.py`
- **螳溯｣・・螳ｹ**:
  - `console_approval_callback(tool_name: str, tool_params: dict) -> tuple[bool, str]` 髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - 驕ｸ謚櫁い繧定｡ｨ遉ｺ縺吶ｋ: `[1] OK・域価隱搾ｼ荏, `[2] 菫ｮ豁｣隕∵悍`, `[3] 繧ｭ繝｣繝ｳ繧ｻ繝ｫ`
  - choice="1" 竊・`(True, "")` 繧定ｿ斐☆
  - choice="2" 竊・菫ｮ豁｣蜀・ｮｹ繧貞・蜉帙＆縺・`(False, 菫ｮ豁｣蜀・ｮｹ)` 繧定ｿ斐☆
  - choice="3" 縺ｾ縺溘・縺昴・莉・竊・`(False, "CANCEL")` 繧定ｿ斐☆
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - choice="1" 縺ｧ `(True, "")` 縺瑚ｿ斐ｋ縺薙→
  - choice="2" 縺ｧ `(False, 菫ｮ豁｣蜀・ｮｹ)` 縺瑚ｿ斐ｋ縺薙→
  - choice="3" 縺ｧ `(False, "CANCEL")` 縺瑚ｿ斐ｋ縺薙→
  - 荳肴ｭ｣縺ｪ蜈･蜉帙〒繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺ｨ縺励※蜃ｦ逅・＆繧後ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ07: Human-in-the-Loop謇ｿ隱阪ヵ繝・け

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝上Φ繝峨Λ繝ｼ隧ｳ邏ｰ險ｭ險・md`・・art 3: HumanApprovalHook・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/05_skeleton_human_approval_hook.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/handlers/human_approval_hook.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_human_approval_hook.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ06・・onsole_approval_adapter.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `HumanApprovalHook(HookProvider)` 繧ｯ繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ
  - `__init__(self, target_tools: list[str], approval_callback: Callable | None = None)` 繧貞ｮ溯｣・☆繧具ｼ医ョ繝輔か繝ｫ繝医・ `console_approval_callback`・・  - `register_hooks` 縺ｧ `BeforeToolCallEvent` 縺ｫ繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ繧堤匳骭ｲ縺吶ｋ
  - `_handle_before_tool_call`: 繝・・繝ｫ蜷阪ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ 竊・`approval_callback` 蜻ｼ縺ｳ蜃ｺ縺・竊・邨先棡縺ｫ蠢懊§縺ｦ `event.cancel_tool` 繧定ｨｭ螳・  - approved=True: 繝・・繝ｫ螳溯｡瑚ｨｱ蜿ｯ・・ancel_tool縺ｯFalse縺ｮ縺ｾ縺ｾ・・  - approved=False, message="CANCEL": `event.cancel_tool = "逕ｳ隲九′繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺ｾ縺励◆縲・`
  - approved=False, message=菫ｮ豁｣蜀・ｮｹ: `event.cancel_tool = message`
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-046縲・48: 謇ｿ隱阪・菫ｮ豁｣隕∵悍繝ｻ繧ｭ繝｣繝ｳ繧ｻ繝ｫ繝ｻ蟇ｾ雎｡螟悶ヤ繝ｼ繝ｫ縺ｮ繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ

---

## 繧ｿ繧ｹ繧ｯ08: 繧ｻ繝・す繝ｧ繝ｳ邂｡逅・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繧ｻ繝・す繝ｧ繝ｳ繝槭ロ繝ｼ繧ｸ繝｣隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/06_skeleton_session_manager.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/session/session_manager.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_session_manager.py`
- **螳溯｣・・螳ｹ**:
  - `SessionManagerFactory` 繧ｯ繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ・亥・繝｡繧ｽ繝・ラ縺ｯ `@staticmethod` 縺ｾ縺溘・ `@classmethod`・・  - `DEFAULT_STORAGE_DIR = "storage/sessions"` 繧ｯ繝ｩ繧ｹ螟画焚繧貞ｮ夂ｾｩ縺吶ｋ
  - `generate_session_id()`: `datetime.now().strftime("%Y%m%d_%H%M%S")` + `secrets.token_hex(4)` 縺ｧ `{YYYYMMDD_HHMMSS}_{8譯∬恭謨ｰ蟄抑` 蠖｢蠑上・ID繧堤函謌舌☆繧・  - `create_session_manager(session_id, storage_dir=DEFAULT_STORAGE_DIR)`: `FileSessionManager` 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧堤函謌舌＠縺ｦ霑斐☆
  - `get_session_storage_path(session_id, storage_dir=DEFAULT_STORAGE_DIR)`: 繧ｻ繝・す繝ｧ繝ｳ繝・・繧ｿ縺ｮ菫晏ｭ伜・繝代せ繧定ｿ斐☆
  - 繝ｭ繧ｰ蜃ｺ蜉帙≠繧奇ｼ・_logger = logging.getLogger(__name__)` 繧貞ｮ夂ｾｩ縺吶ｋ・・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-050縲・52: 繧ｻ繝・す繝ｧ繝ｳID蠖｢蠑上・荳諢乗ｧ繝ｻFileSessionManager繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ逕滓・

---

## 繧ｿ繧ｹ繧ｯ09: 繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｿ繝ｼ繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ隧ｳ邏ｰ險ｭ險・md`・・遶: AG-001・・  - `artifacts/05_detailed-design/outputs/繝翫Ξ繝・ず繝ｻ讌ｭ蜍吶Ν繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・.2遶: KN-001・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/07_skeleton_prompt_orchestrator.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/prompt/prompt_orchestrator.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_prompt_orchestrator.py`
- **螳溯｣・・螳ｹ**:
  - `ORCHESTRATOR_SYSTEM_PROMPT` 螳壽焚繧貞ｮ夂ｾｩ縺吶ｋ・磯撕逧・ｮ壽焚縲∝虚逧・函謌舌↑縺暦ｼ・  - 險ｭ險域嶌3.2遶縺ｮ繝励Ο繝ｳ繝励ヨ蜈ｨ譁・ｒ縺昴・縺ｾ縺ｾ螳溯｣・☆繧具ｼ亥ｽｹ蜑ｲ螳夂ｾｩ繝ｻ逕ｳ隲狗ｨｮ蛻･蛻､譁ｭ蝓ｺ貅悶・蜃ｦ逅・ヵ繝ｭ繝ｼ繝ｻ遖∵ｭ｢莠矩・ｼ・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `ORCHESTRATOR_SYSTEM_PROMPT` 縺檎ｩｺ縺ｧ縺ｪ縺・枚蟄怜・縺ｧ縺ゅｋ縺薙→
  - `"transport_agent"` 縺ｨ `"expense_agent"` 縺後・繝ｭ繝ｳ繝励ヨ縺ｫ蜷ｫ縺ｾ繧後ｋ縺薙→
  - `"generate_transport_form"` 縺ｨ `"generate_expense_form"` 縺ｮ遖∵ｭ｢莠矩・′蜷ｫ縺ｾ繧後ｋ縺薙→



---

## 繧ｿ繧ｹ繧ｯ10: 莠､騾夊ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝医す繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ隧ｳ邏ｰ險ｭ險・md`・・遶: AG-002・・  - `artifacts/05_detailed-design/outputs/繝翫Ξ繝・ず繝ｻ讌ｭ蜍吶Ν繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・.3遶: KN-002・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/08_skeleton_prompt_specialist.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/prompt/prompt_transport.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_prompt_transport.py`
- **螳溯｣・・螳ｹ**:
  - `_TRANSPORT_SYSTEM_PROMPT_TEMPLATE` 繝・Φ繝励Ξ繝ｼ繝亥ｮ壽焚繧貞ｮ夂ｾｩ縺吶ｋ・医・繝ｬ繝ｼ繧ｹ繝帙Ν繝繝ｼ: `{applicant_name}`, `{application_date}`, `{deadline_date}`, `{approval_threshold_transport}`, `{transport_policies}`・・  - `get_transport_system_prompt(applicant_name, application_date, deadline_date, approval_threshold, transport_policies)` 髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - 險ｭ險域嶌4.2遶縺ｮ繝励Ο繝ｳ繝励ヨ蜈ｨ譁・ｒ繝・Φ繝励Ξ繝ｼ繝医→縺励※螳溯｣・☆繧・  - 讌ｭ蜍吶Ν繝ｼ繝ｫ蛟､・域悄髯舌・髢ｾ蛟､・峨・繝上・繝峨さ繝ｼ繝峨○縺壼ｼ墓焚縺九ｉ蜿励￠蜿悶ｋ・・9.12.3・・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `{applicant_name}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→
  - `{deadline_date}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→
  - `{approval_threshold_transport}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→
  - `{transport_policies}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ11: 邨瑚ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝医す繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ隧ｳ邏ｰ險ｭ險・md`・・遶: AG-003・・  - `artifacts/05_detailed-design/outputs/繝翫Ξ繝・ず繝ｻ讌ｭ蜍吶Ν繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・.4遶: KN-003・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/08_skeleton_prompt_specialist.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/prompt/prompt_expense.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_prompt_expense.py`
- **螳溯｣・・螳ｹ**:
  - `_EXPENSE_SYSTEM_PROMPT_TEMPLATE` 繝・Φ繝励Ξ繝ｼ繝亥ｮ壽焚繧貞ｮ夂ｾｩ縺吶ｋ・医・繝ｬ繝ｼ繧ｹ繝帙Ν繝繝ｼ: `{applicant_name}`, `{application_date}`, `{deadline_date}`, `{approval_threshold_expense}`, `{expense_policies}`・・  - `get_expense_system_prompt(applicant_name, application_date, deadline_date, approval_threshold, expense_policies)` 髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - 險ｭ險域嶌5.2遶縺ｮ繝励Ο繝ｳ繝励ヨ蜈ｨ譁・ｒ繝・Φ繝励Ξ繝ｼ繝医→縺励※螳溯｣・☆繧・  - 讌ｭ蜍吶Ν繝ｼ繝ｫ蛟､・域悄髯舌・髢ｾ蛟､・峨・繝上・繝峨さ繝ｼ繝峨○縺壼ｼ墓焚縺九ｉ蜿励￠蜿悶ｋ・・9.12.3・・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `{applicant_name}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→
  - `{deadline_date}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→
  - `{approval_threshold_expense}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→
  - `{expense_policies}` 縺梧ｭ｣縺励￥鄂ｮ謠帙＆繧後ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ12: 繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｿ繝ｼ繝昴Μ繧ｷ繝ｼ・医リ繝ｬ繝・ず・・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝翫Ξ繝・ず繝ｻ讌ｭ蜍吶Ν繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・.2遶: KN-001・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/knowledge/orchestrator_policies.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_knowledge_policies.py`
- **螳溯｣・・螳ｹ**:
  - `get_orchestrator_policies() -> str` 髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ・亥ｼ墓焚縺ｪ縺暦ｼ・  - 險ｭ險域嶌2.2遶縺ｮ繝翫Ξ繝・ず蜀・ｮｹ螳夂ｾｩ繧偵◎縺ｮ縺ｾ縺ｾ螳溯｣・☆繧具ｼ・D-01縲廱D-03縺ｮ繧ｭ繝ｼ繝ｯ繝ｼ繝峨Μ繧ｹ繝茨ｼ・  - 莉悶・蜀・Κ繝｢繧ｸ繝･繝ｼ繝ｫ縺ｸ縺ｮ萓晏ｭ倥↑縺暦ｼ育ｴ皮ｲ九↑繝・く繧ｹ繝郁ｿ泌唆・・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-060: `get_orchestrator_policies()` 縺檎ｩｺ縺ｧ縺ｪ縺・ユ繧ｭ繧ｹ繝医ｒ霑斐☆縺薙→

---

## 繧ｿ繧ｹ繧ｯ13: 莠､騾夊ｲｻ邊ｾ邂礼筏隲九・繝ｪ繧ｷ繝ｼ・医リ繝ｬ繝・ず・・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝翫Ξ繝・ず繝ｻ讌ｭ蜍吶Ν繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・.3遶: KN-002・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/knowledge/transport_policies.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_knowledge_policies.py`・医ち繧ｹ繧ｯ12縺ｨ蜷御ｸ繝輔ぃ繧､繝ｫ縺ｫ霑ｽ險假ｼ・- **螳溯｣・・螳ｹ**:
  - `get_transport_policies(deadline_months: int, approval_threshold: int) -> str` 髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - 險ｭ險域嶌2.3遶縺ｮ繝翫Ξ繝・ず蜀・ｮｹ螳夂ｾｩ繧断-string縺ｧ螳溯｣・☆繧具ｼ・RL-01縲廝RL-09・・  - `{deadline_months}` 縺ｨ `{approval_threshold:,}` 繧貞虚逧・ｱ暮幕縺吶ｋ
  - 莉悶・蜀・Κ繝｢繧ｸ繝･繝ｼ繝ｫ縺ｸ縺ｮ萓晏ｭ倥↑縺・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-061: `get_transport_policies(3, 10000)` 縺・`"3"` 縺ｨ `"10,000"` 繧貞性繧繝・く繧ｹ繝医ｒ霑斐☆縺薙→

---

## 繧ｿ繧ｹ繧ｯ14: 邨瑚ｲｻ邊ｾ邂礼筏隲九・繝ｪ繧ｷ繝ｼ・医リ繝ｬ繝・ず・・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繝翫Ξ繝・ず繝ｻ讌ｭ蜍吶Ν繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・.4遶: KN-003・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/knowledge/expense_policies.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_knowledge_policies.py`・医ち繧ｹ繧ｯ12繝ｻ13縺ｨ蜷御ｸ繝輔ぃ繧､繝ｫ縺ｫ霑ｽ險假ｼ・- **螳溯｣・・螳ｹ**:
  - `get_expense_policies(deadline_months: int, approval_threshold: int) -> str` 髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - 險ｭ險域嶌2.4遶縺ｮ繝翫Ξ繝・ず蜀・ｮｹ螳夂ｾｩ繧断-string縺ｧ螳溯｣・☆繧具ｼ・RL-10縲廝RL-17・・  - `{deadline_months}` 縺ｨ `{approval_threshold:,}` 繧貞虚逧・ｱ暮幕縺吶ｋ
  - 莉悶・蜀・Κ繝｢繧ｸ繝･繝ｼ繝ｫ縺ｸ縺ｮ萓晏ｭ倥↑縺・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-062: `get_expense_policies(3, 5000)` 縺・`"3"` 縺ｨ `"5,000"` 繧貞性繧繝・く繧ｹ繝医ｒ霑斐☆縺薙→



---

## 繧ｿ繧ｹ繧ｯ15: 莠､騾夊ｲｻ險育ｮ励ヤ繝ｼ繝ｫ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/莠､騾夊ｲｻ險育ｮ励ヤ繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/繝・・繧ｿ繝｢繝・Ν隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tools/transport_tools.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_transport_tools.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ01・・ata_models.py・峨√ち繧ｹ繧ｯ04・・rror_handler.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - 繝｢繧ｸ繝･繝ｼ繝ｫ繝ｬ繝吶Ν繧ｭ繝｣繝・す繝･螟画焚繧貞ｮ夂ｾｩ縺吶ｋ: `_train_fares`, `_train_fares_loaded`, `_fixed_fares`, `_fixed_fares_loaded`・育ｩｺ繝ｪ繧ｹ繝医↓繧医ｋ譛ｪ繝ｭ繝ｼ繝牙愛螳夂ｦ∵ｭ｢: R9.12.4・・  - `_TRAIN_FARES_PATH = "data/train_fares.json"`, `_FIXED_FARES_PATH = "data/fixed_fares.json"` 繧貞ｮ夂ｾｩ縺吶ｋ
  - `_load_train_fares() -> tuple[bool, str]`: train_fares.json繧定ｪｭ縺ｿ霎ｼ縺ｿTrainFareRecord縺ｧ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ縲√く繝｣繝・す繝･譖ｴ譁ｰ
  - `_load_fixed_fares() -> tuple[bool, str]`: fixed_fares.json繧定ｪｭ縺ｿ霎ｼ縺ｿ霎樊嶌縺ｨ縺励※菫晄戟縲√く繝｣繝・す繝･譖ｴ譁ｰ
  - `@tool` 繝・さ繝ｬ繝ｼ繧ｿ縺ｧ `calculate_transport_fare(departure, destination, transport_type, travel_date) -> dict` 繧貞ｮ溯｣・☆繧・  - 蜃ｦ逅・ヵ繝ｭ繝ｼ: 繝舌Μ繝・・繧ｷ繝ｧ繝ｳ 竊・繝・・繧ｿ隱ｭ縺ｿ霎ｼ縺ｿ 竊・莠､騾壽焔谿ｵ蛻・ｲ撰ｼ磯崕霆・邨瑚ｷｯ繝・・繝悶Ν讀懃ｴ｢縲√◎縺ｮ莉・蝗ｺ螳夐°雉・､懃ｴ｢・俄・ 邨先棡霑泌唆
  - 邨瑚ｷｯ譛ｪ逋ｻ骭ｲ譎ゅ・ `not_found=True` 縺ｧ霑斐☆
  - 繧ｨ繝ｩ繝ｼ霑泌唆繧ｭ繝ｼ蜷阪・ `TransportCalculatorOutput` 縺ｮ繝輔ぅ繝ｼ繝ｫ繝牙錐縺ｨ荳閾ｴ縺輔○繧具ｼ・error_message`・・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-001縲・07: 逋ｻ骭ｲ貂医∩邨瑚ｷｯ繝ｻ蝗ｺ螳夐°雉・・邨瑚ｷｯ譛ｪ逋ｻ骭ｲ繝ｻ蟇ｾ蠢懷､紋ｺ､騾壽焔谿ｵ繝ｻ繝・・繧ｿ繝輔ぃ繧､繝ｫ荳榊ｭ伜惠繝ｻ荳肴ｭ｣譌･莉伜ｽ｢蠑・
---

## 繧ｿ繧ｹ繧ｯ16: 逕ｳ隲区嶌逕滓・繝・・繝ｫ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/逕ｳ隲区嶌逕滓・繝・・繝ｫ隧ｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/繝・・繧ｿ繝｢繝・Ν隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tools/output_generator.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_output_generator.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ01・・ata_models.py・峨√ち繧ｹ繧ｯ04・・rror_handler.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `_TRANSPORT_TEMPLATE_PATH = "template/莠､騾夊ｲｻ邊ｾ邂礼筏隲区嶌_template.xlsx"`, `_EXPENSE_TEMPLATE_PATH = "template/邨瑚ｲｻ邊ｾ邂礼筏隲区嶌_template.xlsx"` 繧貞ｮ夂ｾｩ縺吶ｋ
  - `_write_transport_rows(ws, items, start_row)`: 遘ｻ蜍墓・邏ｰ陦後ｒExcel繧ｷ繝ｼ繝医↓譖ｸ縺崎ｾｼ繧・・=No, B=遘ｻ蜍墓律, C=蜃ｺ逋ｺ蝨ｰ, D=逶ｮ逧・慍, E=莠､騾壽焔谿ｵ, F=雋ｻ逕ｨ, G=讌ｭ蜍咏岼逧・ H=謇ｿ隱咲憾豕・ｼ・  - `_write_expense_rows(ws, items, start_row)`: 邨瑚ｲｻ譏守ｴｰ陦後ｒExcel繧ｷ繝ｼ繝医↓譖ｸ縺崎ｾｼ繧・・=No, B=雉ｼ蜈･譌･, C=蠎苓・蜷・ D=蜩∫岼, E=邨瑚ｲｻ蛹ｺ蛻・ F=驥鷹｡・ G=讌ｭ蜍咏岼逧・ H=謇ｿ隱咲憾豕・ｼ・  - `_save_workbook(workbook, file_path) -> tuple[bool, str]`: 繝輔ぃ繧､繝ｫ菫晏ｭ假ｼ・OError繝ｻPermissionError繝ｻException繧貞句挨謐墓拷・・  - `_generate_form(template_path, validated, write_rows_fn, output_filename) -> dict`: 蜈ｱ騾壹ヵ繧ｩ繝ｼ繝逕滓・蜃ｦ逅・ｼ・RY蜴溷援: R9.12.1・・  - `@tool(context=True)` 繝・さ繝ｬ繝ｼ繧ｿ縺ｧ `generate_transport_form(items, tool_context) -> dict` 繧貞ｮ溯｣・☆繧・  - `@tool(context=True)` 繝・さ繝ｬ繝ｼ繧ｿ縺ｧ `generate_expense_form(items, tool_context) -> dict` 繧貞ｮ溯｣・☆繧・  - invocation_state縺九ｉ `applicant_name`繝ｻ`application_date` 繧貞叙蠕励☆繧・  - 蜃ｺ蜉帙ヵ繧｡繧､繝ｫ繝代せ縺ｯ繝・・繝ｫ蜀・Κ縺ｧ繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝励ｒ繧ゅ→縺ｫ逕滓・縺吶ｋ・・LM縺ｮ繝代Λ繝｡繝ｼ繧ｿ縺ｨ縺励※蜿励￠蜿悶ｉ縺ｪ縺・ｼ・  - 繧ｨ繝ｩ繝ｼ霑泌唆繧ｭ繝ｼ蜷阪・ `TransportFormOutput`繝ｻ`ExpenseFormOutput` 縺ｮ繝輔ぅ繝ｼ繝ｫ繝牙錐縺ｨ荳閾ｴ縺輔○繧具ｼ・error_message`・・- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - TC-UNIT-010縲・14: 譛牙柑縺ｪ譏守ｴｰ縺ｧ縺ｮ逕ｳ隲区嶌逕滓・繝ｻ繝・Φ繝励Ξ繝ｼ繝井ｸ榊ｭ伜惠繝ｻ遨ｺ譏守ｴｰ繝ｪ繧ｹ繝・
---

## 繧ｿ繧ｹ繧ｯ17: 繧ｬ繝ｼ繝峨Ξ繝ｼ繝ｫCloudFormation

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/繧ｬ繝ｼ繝峨Ξ繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/16_guardrails_cloudformation_yaml.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/guardrails/guardrails_cloudformation.yaml`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: 縺ｪ縺暦ｼ・AML繝輔ぃ繧､繝ｫ縺ｮ縺溘ａ・・- **螳溯｣・・螳ｹ**:
  - 繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝峨・繧ｵ繝ｳ繝励ΝYAML繧偵・繝ｼ繧ｹ縺ｫ縲√ぎ繝ｼ繝峨Ξ繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險域嶌縺ｮ險ｭ螳壹ｒ蜿肴丐縺吶ｋ
  - 繧ｳ繝ｳ繝・Φ繝・・繝ｪ繧ｷ繝ｼ・・IOLENCE繝ｻPROMPT_ATTACK繝ｻMISCONDUCT繝ｻHATE繝ｻSEXUAL繝ｻINSULTS・峨ｒ險ｭ螳壹☆繧・  - PII繝輔ぅ繝ｫ繧ｿ・・REDIT_DEBIT_CARD_CVV・峨ｒ險ｭ螳壹☆繧・  - BlockedInputMessaging繝ｻBlockedOutputsMessaging繧呈律譛ｬ隱槭〒險ｭ螳壹☆繧・
---

## 繧ｿ繧ｹ繧ｯ18: 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥・騾壹Θ繝ｼ繝・ぅ繝ｪ繝・ぅ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/莠､騾夊ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/邨瑚ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/繧ｻ繝・す繝ｧ繝ｳ繝槭ロ繝ｼ繧ｸ繝｣隧ｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/繝上Φ繝峨Λ繝ｼ隧ｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/17_skeleton_base_agent.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/agents/base_agent.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_base_agent.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ03・・ettings.py・峨√ち繧ｹ繧ｯ05・・oop_control_hook.py・峨√ち繧ｹ繧ｯ07・・uman_approval_hook.py・峨√ち繧ｹ繧ｯ08・・ession_manager.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `calculate_deadline(application_date: str, deadline_months: int) -> str`: 逕ｳ隲区律縺九ｉ逕ｳ隲区悄髯舌ｒ險育ｮ暦ｼ・dateutil.relativedelta` 菴ｿ逕ｨ縲√ヱ繝ｼ繧ｹ螟ｱ謨玲凾縺ｯ `"隕∫｢ｺ隱・` 繧定ｿ斐☆・・  - `create_specialist_agent(session_id, system_prompt, tools, agent_name, window_size, max_iterations, max_attempts, initial_delay, max_delay) -> Agent`: Session/HumanApprovalHook/LoopControlHook縺ｮ逕滓・縺ｨAgent繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺ｮ邨・∩遶九※繧貞・騾壼喧
  - `invoke_specialist_agent(query, tool_context, agent_id, deadline_months, build_agent) -> str`: invocation_state蜿門ｾ励・deadline險育ｮ励・繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥他縺ｳ蜃ｺ縺励・萓句､門・逅・ｒ蜈ｱ騾壼喧
  - 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ: LoopLimitError 竊・`_logger.warning` + `ErrorHandler.handle_loop_limit_error(e)` 霑泌唆縲・xception 竊・`_logger.error(exc_info=True)` + `ErrorHandler.handle_unexpected_error(e)` 霑泌唆
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `calculate_deadline("2026-05-10", 3)` 縺・`"2026-02-10"` 繧定ｿ斐☆縺薙→
  - `calculate_deadline("invalid", 3)` 縺・`"隕∫｢ｺ隱・` 繧定ｿ斐☆縺薙→
  - `create_specialist_agent()` 縺・`Agent` 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧定ｿ斐☆縺薙→・・edrock繧偵Δ繝・け・・
---

## 繧ｿ繧ｹ繧ｯ19: 繧ｪ繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｿ繝ｼ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/逕ｳ隲句女莉倡ｪ灘哨繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/11_skeleton_orchestrator_agent.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/agents/orchestrator_agent.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_orchestrator_agent.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ02・・odel_config.py・峨√ち繧ｹ繧ｯ03・・ettings.py・峨√ち繧ｹ繧ｯ05・・oop_control_hook.py・峨√ち繧ｹ繧ｯ08・・ession_manager.py・峨√ち繧ｹ繧ｯ09・・rompt_orchestrator.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `OrchestratorAgent` 繧ｯ繝ｩ繧ｹ繧貞ｮ夂ｾｩ縺吶ｋ
  - `__init__(self, session_id: str)`: session_id繧貞女縺大叙繧翫∫筏隲玖・錐蜿朱寔繝ｻ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝亥・譛溷喧繧定｡後≧
  - `_collect_user_name()`: CLI讓呎ｺ門・蜉帙〒逕ｳ隲玖・錐繧貞庶髮・☆繧具ｼ育ｩｺ譁・ｭ励・蝣ｴ蜷医・蜀榊・蜉帙ｒ菫・☆・・  - `_build_agent()`: Agent繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧堤函謌舌☆繧具ｼ・indow_size=30, hooks=[LoopControlHook], tools=[transport_agent, expense_agent]・・  - `run()`: 蟇ｾ隧ｱ繝ｫ繝ｼ繝励ｒ螳溯｡後☆繧具ｼ・xit/quit/邨ゆｺ・〒break縲〉eset/繝ｪ繧ｻ繝・ヨ/譛蛻昴°繧峨〒逕ｳ隲玖・錐蜿朱寔縺ｸ謌ｻ繧具ｼ・  - invocation_state縺ｯ霎樊嶌繝ｪ繝・Λ繝ｫ縺ｧ貂｡縺・ `{"applicant_name": ..., "application_date": ..., "session_id": ...}`
  - 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ: KeyboardInterrupt竊鍛reak縲´oopLimitError竊団ontinue縲，ontextWindowOverflowException竊団ontinue縲｀axTokensReachedException竊団ontinue縲ヽuntimeError竊団ontinue縲・xception竊団ontinue
  - 繧ｦ繧ｧ繝ｫ繧ｫ繝繝｡繝・そ繝ｼ繧ｸ繧定｡ｨ遉ｺ縺吶ｋ
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - 逕ｳ隲玖・錐縺檎ｩｺ譁・ｭ励・蝣ｴ蜷医↓蜀榊・蜉帙′菫・＆繧後ｋ縺薙→・医Δ繝・け菴ｿ逕ｨ・・  - exit/quit/邨ゆｺ・さ繝槭Φ繝峨〒蟇ｾ隧ｱ繝ｫ繝ｼ繝励′邨ゆｺ・☆繧九％縺ｨ・医Δ繝・け菴ｿ逕ｨ・・  - invocation_state縺ｫ `applicant_name`繝ｻ`application_date`繝ｻ`session_id` 縺悟性縺ｾ繧後ｋ縺薙→



---

## 繧ｿ繧ｹ繧ｯ20: 莠､騾夊ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/莠､騾夊ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ隧ｳ邏ｰ險ｭ險・md`・・遶・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/agents/transport_agent.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_transport_agent.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ10・・rompt_transport.py・峨√ち繧ｹ繧ｯ13・・ransport_policies.py・峨√ち繧ｹ繧ｯ15・・ransport_tools.py・峨√ち繧ｹ繧ｯ16・・utput_generator.py・峨√ち繧ｹ繧ｯ18・・ase_agent.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `_build_transport_agent(session_id, applicant_name, application_date, deadline) -> Agent` 繝薙Ν繝蛾未謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - `settings.transport_agent` 縺九ｉ險ｭ螳壹ｒ蜿門ｾ励☆繧・  - `get_transport_system_prompt(applicant_name, application_date, deadline_date, approval_threshold, transport_policies)` 縺ｧ繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ繧堤函謌舌☆繧・  - `get_transport_policies(deadline_months, approval_threshold)` 縺ｧ繝昴Μ繧ｷ繝ｼ繧貞叙蠕励☆繧・  - `create_specialist_agent()` 縺ｧ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医ｒ逕滓・縺吶ｋ・・ools=[calculate_transport_fare, generate_transport_form]・・  - `@tool(context=True)` 縺ｧ `transport_agent(query, tool_context) -> str` 繝・・繝ｫ髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - `invoke_specialist_agent(query, tool_context, agent_id="AG-002", deadline_months=settings.transport_agent.deadline_months, build_agent=_build_transport_agent)` 繧貞他縺ｳ蜃ｺ縺・  - 繝・・繝ｫ隱ｬ譏・ `"莠､騾夊ｲｻ邊ｾ邂礼筏隲九ｒ蜃ｦ逅・☆繧九らｧｻ蜍墓ュ蝣ｱ繧貞庶髮・＠縲∽ｺ､騾夊ｲｻ繧定ｨ育ｮ励＠縺ｦ逕ｳ隲区嶌繧堤函謌舌☆繧九・`
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `transport_agent` 繝・・繝ｫ髢｢謨ｰ縺梧枚蟄怜・繧定ｿ斐☆縺薙→・・edrock繧偵Δ繝・け・・  - LoopLimitError逋ｺ逕滓凾縺ｫ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ譁・ｭ怜・縺瑚ｿ斐ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ21: 邨瑚ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/邨瑚ｲｻ邊ｾ邂礼筏隲九お繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`
  - `artifacts/05_detailed-design/outputs/繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ隧ｳ邏ｰ險ｭ險・md`・・遶・・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/agents/expense_agent.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_expense_agent.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ11・・rompt_expense.py・峨√ち繧ｹ繧ｯ14・・xpense_policies.py・峨√ち繧ｹ繧ｯ16・・utput_generator.py・峨√ち繧ｹ繧ｯ18・・ase_agent.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `_build_expense_agent(session_id, applicant_name, application_date, deadline) -> Agent` 繝薙Ν繝蛾未謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - `settings.expense_agent` 縺九ｉ險ｭ螳壹ｒ蜿門ｾ励☆繧・  - `get_expense_system_prompt(applicant_name, application_date, deadline_date, approval_threshold, expense_policies)` 縺ｧ繧ｷ繧ｹ繝・Β繝励Ο繝ｳ繝励ヨ繧堤函謌舌☆繧・  - `get_expense_policies(deadline_months, approval_threshold)` 縺ｧ繝昴Μ繧ｷ繝ｼ繧貞叙蠕励☆繧・  - `create_specialist_agent()` 縺ｧ繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医ｒ逕滓・縺吶ｋ・・ools=[generate_expense_form]・・  - `@tool(context=True)` 縺ｧ `expense_agent(query, tool_context) -> str` 繝・・繝ｫ髢｢謨ｰ繧貞ｮ夂ｾｩ縺吶ｋ
  - `invoke_specialist_agent(query, tool_context, agent_id="AG-003", deadline_months=settings.expense_agent.deadline_months, build_agent=_build_expense_agent)` 繧貞他縺ｳ蜃ｺ縺・  - 繝・・繝ｫ隱ｬ譏・ `"邨瑚ｲｻ邊ｾ邂礼筏隲九ｒ蜃ｦ逅・☆繧九らｵ瑚ｲｻ諠・ｱ繧貞庶髮・＠縲∫ｵ瑚ｲｻ蛹ｺ蛻・ｒ蛻､譁ｭ縺励※逕ｳ隲区嶌繧堤函謌舌☆繧九・`
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `expense_agent` 繝・・繝ｫ髢｢謨ｰ縺梧枚蟄怜・繧定ｿ斐☆縺薙→・・edrock繧偵Δ繝・け・・  - LoopLimitError逋ｺ逕滓凾縺ｫ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ譁・ｭ怜・縺瑚ｿ斐ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ22: 繝｡繧､繝ｳ繧ｨ繝ｳ繝医Μ繝ｼ繝昴う繝ｳ繝・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/逕ｳ隲句女莉倡ｪ灘哨繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝郁ｩｳ邏ｰ險ｭ險・md`・・.3遶: 繝ｭ繧ｰ蜃ｺ蜉幢ｼ・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/13_skeleton_main.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/main.py`
- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: `artifacts/06_code-generation/src/tests/unit/test_main.py`
- **萓晏ｭ・*: 繧ｿ繧ｹ繧ｯ19・・rchestrator_agent.py・峨′蜈医↓螳御ｺ・＠縺ｦ縺・ｋ縺薙→
- **螳溯｣・・螳ｹ**:
  - `load_dotenv()` 縺ｧ `.env` 繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ繧
  - 繝ｭ繧ｰ險ｭ螳・ LOG_LEVEL迺ｰ蠅・､画焚蜿門ｾ励～logs/` 繝・ぅ繝ｬ繧ｯ繝医Μ菴懈・縲・繝上Φ繝峨Λ繝ｼ讒区・・・onsole/app.log/error.log・峨ヽotatingFileHandler・・0MBﾃ・荳紋ｻ｣・峨ゞTF-8繧ｨ繝ｳ繧ｳ繝ｼ繝・ぅ繝ｳ繧ｰ
  - `logging.getLogger("strands").setLevel(logging.WARNING)` 縺ｧStrands繝ｭ繧ｰ繧呈椛蛻ｶ縺吶ｋ
  - `main()` 髢｢謨ｰ: `SessionManagerFactory.generate_session_id()` 縺ｧsession_id繧堤函謌舌＠縲～OrchestratorAgent(session_id).run()` 繧貞ｮ溯｡後☆繧・  - 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ: KeyboardInterrupt 竊・`ErrorHandler.handle_keyboard_interrupt()` 繧定｡ｨ遉ｺ縺励※INFO繝ｭ繧ｰ縲・xception 竊・`ErrorHandler.handle_unexpected_error(e)` 繧定｡ｨ遉ｺ縺励※ERROR繝ｭ繧ｰ・・xc_info=True・峨～sys.exit(1)`
- **蜊倅ｽ薙ユ繧ｹ繝亥・螳ｹ**:
  - `main()` 縺梧ｭ｣蟶ｸ縺ｫ襍ｷ蜍輔・邨ゆｺ・☆繧九％縺ｨ・・rchestratorAgent繧偵Δ繝・け・・  - KeyboardInterrupt逋ｺ逕滓凾縺ｫsys.exit縺悟他縺ｰ繧後↑縺・％縺ｨ
  - Exception逋ｺ逕滓凾縺ｫsys.exit(1)縺悟他縺ｰ繧後ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ23: 髱咏噪繝・・繧ｿ繝輔ぃ繧､繝ｫ驟咲ｽｮ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**:
  - `artifacts/05_detailed-design/outputs/莠､騾夊ｲｻ險育ｮ励ヤ繝ｼ繝ｫ隧ｳ邏ｰ險ｭ險・md`・・遶: 繝・・繧ｿ險ｭ險茨ｼ・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: `.kiro/artifact-workflow/templates/06_code-generation/14_design_data_files.md`
- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**:
  - `artifacts/06_code-generation/src/data/train_fares.json`・・materials/06_code-generation/train_fares.json` 縺九ｉ繧ｳ繝斐・・・  - `artifacts/06_code-generation/src/data/fixed_fares.json`・・materials/06_code-generation/fixed_fares.json` 縺九ｉ繧ｳ繝斐・・・  - `artifacts/06_code-generation/src/template/莠､騾夊ｲｻ邊ｾ邂礼筏隲区嶌繝・Φ繝励Ξ繝ｼ繝・xlsx`・・materials/06_code-generation/莠､騾夊ｲｻ逕ｳ隲区嶌_template.xlsx` 縺九ｉ繧ｳ繝斐・・・  - `artifacts/06_code-generation/src/template/邨瑚ｲｻ邊ｾ邂礼筏隲区嶌繝・Φ繝励Ξ繝ｼ繝・xlsx`・・materials/06_code-generation/邨瑚ｲｻ邊ｾ邂礼筏隲区嶌_template.xlsx` 縺九ｉ繧ｳ繝斐・・・- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: 縺ｪ縺暦ｼ医ヵ繧｡繧､繝ｫ繧ｳ繝斐・縺ｮ縺溘ａ・・- **螳溯｣・・螳ｹ**:
  - `materials/06_code-generation/` 縺九ｉ蜷・ヵ繧｡繧､繝ｫ繧呈欠螳壹・繝代せ縺ｫ繧ｳ繝斐・縺吶ｋ
  - `data/` 繝・ぅ繝ｬ繧ｯ繝医Μ縺ｨ `template/` 繝・ぅ繝ｬ繧ｯ繝医Μ繧剃ｽ懈・縺吶ｋ

---

## 繧ｿ繧ｹ繧ｯ24: 繝励Ο繧ｸ繧ｧ繧ｯ繝郁ｨｭ螳壹ヵ繧｡繧､繝ｫ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ險ｭ險域嶌**: 縺ｪ縺暦ｼ医・繝ｭ繧ｸ繧ｧ繧ｯ繝郁ｦ冗ｴ・↓蝓ｺ縺･縺擾ｼ・- **蜿ら・縺吶ｋ繧ｹ繧ｱ繝ｫ繝医Φ繧ｳ繝ｼ繝・*: 縺ｪ縺・- **謌先棡迚ｩ縺ｮ繝輔ぃ繧､繝ｫ繝代せ**:
  - `artifacts/06_code-generation/src/pyproject.toml`
  - `artifacts/06_code-generation/src/.env.template`
  - `artifacts/06_code-generation/src/.gitignore`
  - `artifacts/06_code-generation/src/README.md`
  - 蜷・ョ繧｣繝ｬ繧ｯ繝医Μ縺ｮ `__init__.py`・・onfig/, models/, agents/, handlers/, tools/, prompt/, knowledge/, session/, storage/・・- **蜊倅ｽ薙ユ繧ｹ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**: 縺ｪ縺・- **螳溯｣・・螳ｹ**:
  - `pyproject.toml`: 萓晏ｭ倥ヱ繝・こ繝ｼ繧ｸ・・trands-agents, strands-agents-tools, boto3, pydantic, pydantic-settings, python-dotenv, python-dateutil, openpyxl, pytest, pytest-cov・峨ｒ螳夂ｾｩ縺吶ｋ
  - `.env.template`: LOG_LEVEL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, GUARDRAIL_ID, GUARDRAIL_VERSION 繧貞ｮ夂ｾｩ縺吶ｋ
  - `.gitignore`: `.env`, `output/`, `logs/`, `storage/`, `__pycache__/`, `.pytest_cache/` 繧帝勁螟悶☆繧・  - 蜷・ョ繧｣繝ｬ繧ｯ繝医Μ縺ｫ遨ｺ縺ｮ `__init__.py` 繧剃ｽ懈・縺吶ｋ

---

## 繧ｿ繧ｹ繧ｯ25: 繝・ぅ繝ｬ繧ｯ繝医Μ讒矩讀懆ｨｼ

- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **蜿ら・縺吶ｋ隕冗ｴ・*: `.kiro/steering/00_rule_directory_structure.md`
- **讀懆ｨｼ蟇ｾ雎｡繝・ぅ繝ｬ繧ｯ繝医Μ**: `artifacts/06_code-generation/src/`
- **讀懆ｨｼ蜀・ｮｹ**:
  - R1貅匁侠遒ｺ隱・ `src/` 逶ｴ荳九・繝・ぅ繝ｬ繧ｯ繝医Μ縺瑚ｨｱ蜿ｯ繝ｪ繧ｹ繝茨ｼ・onfig/, models/, agents/, handlers/, tools/, prompt/, knowledge/, session/, storage/, data/, template/, sample/, output/, logs/, evals/, docs/, tests/, guardrails/・峨・縺ｿ縺ｧ縺ゅｋ縺薙→
  - R2貅匁侠遒ｺ隱・ 蜷・ヵ繧｡繧､繝ｫ縺梧ｭ｣縺励＞繝・ぅ繝ｬ繧ｯ繝医Μ縺ｫ驟咲ｽｮ縺輔ｌ縲∝多蜷崎ｦ丞援縺ｫ蠕薙▲縺ｦ縺・ｋ縺薙→・井ｾ・ `*_agent.py` 竊・`agents/`縲～*_tools.py` 縺ｾ縺溘・ `*_generator.py` 竊・`tools/`縲～*_policies.py` 竊・`knowledge/`縲～prompt_*.py` 竊・`prompt/`・・- **驕募渚譎ゅ・蝣ｱ蜻雁ｽ｢蠑・*:
  - `笞・・[驕募渚遞ｮ蛻･]: [繝輔ぃ繧､繝ｫ繝代せ] 竊・[菫ｮ豁｣譁ｹ豕評`
- **驕募渚譎ゅ・蟇ｾ蠢・*: 讀懷・縺輔ｌ縺滄＆蜿阪ｒ縺吶∋縺ｦ菫ｮ豁｣縺励※縺九ｉ繧ｹ繝・・繧ｿ繧ｹ繧貞ｮ御ｺ・↓縺吶ｋ縺薙→

---

## 繧ｿ繧ｹ繧ｯ26: 邨仙粋繝・せ繝・
- **繧ｹ繝・・繧ｿ繧ｹ**: [ ] 譛ｪ逹謇・- **繝・せ繝亥ｯｾ雎｡**:
  - AG-001 竊・AG-002 騾｣謳ｺ・井ｺ､騾夊ｲｻ髢｢騾｣繧ｭ繝ｼ繝ｯ繝ｼ繝峨〒transport_agent縺ｸ蟋碑ｭｲ・・  - AG-001 竊・AG-003 騾｣謳ｺ・育ｵ瑚ｲｻ髢｢騾｣繧ｭ繝ｼ繝ｯ繝ｼ繝峨〒expense_agent縺ｸ蟋碑ｭｲ・・  - invocation_state縺ｮ莨晄眺・・pplicant_name繝ｻapplication_date繝ｻsession_id縺梧ｭ｣縺励￥貂｡縺輔ｌ繧具ｼ・  - HumanApprovalHook縺ｨgenerate_transport_form/generate_expense_form縺ｮ騾｣謳ｺ
  - 繧ｻ繝・す繝ｧ繝ｳ豌ｸ邯壼喧・・torage/sessions/縺ｫ繝輔ぃ繧､繝ｫ縺檎函謌舌＆繧後ｋ・・- **邨仙粋繝・せ繝医さ繝ｼ繝峨・繝輔ぃ繧､繝ｫ繝代せ**:
  - `artifacts/06_code-generation/src/tests/integration/test_agent_routing.py`・・C-INT-001縲・04・・  - `artifacts/06_code-generation/src/tests/integration/test_tool_call_flow.py`・・C-INT-010縲・13・・  - `artifacts/06_code-generation/src/tests/integration/test_session_persistence.py`・・C-INT-020縲・21・・- **邨仙粋繝・せ繝亥・螳ｹ**:
  - TC-INT-001: AG-001縺御ｺ､騾夊ｲｻ髢｢騾｣繧ｭ繝ｼ繝ｯ繝ｼ繝峨〒transport_agent縺ｸ蟋碑ｭｲ縺吶ｋ縺薙→・・edrock繧偵Δ繝・け・・  - TC-INT-002: AG-001縺檎ｵ瑚ｲｻ髢｢騾｣繧ｭ繝ｼ繝ｯ繝ｼ繝峨〒expense_agent縺ｸ蟋碑ｭｲ縺吶ｋ縺薙→・・edrock繧偵Δ繝・け・・  - TC-INT-003: AG-001縺悟愛譁ｭ荳崎・譎ゅ↓驕ｸ謚櫁い繧呈署遉ｺ縺吶ｋ縺薙→・・edrock繧偵Δ繝・け・・  - TC-INT-004: invocation_state縺梧ｭ｣縺励￥AG-002縺ｸ莨晄眺縺輔ｌ繧九％縺ｨ
  - TC-INT-010: AG-002縺檎ｧｻ蜍墓ュ蝣ｱ蜿朱寔蠕後↓calculate_transport_fare繧貞他縺ｳ蜃ｺ縺吶％縺ｨ
  - TC-INT-011: HumanApprovalHook縺携enerate_transport_form蜻ｼ縺ｳ蜃ｺ縺怜燕縺ｫ逋ｺ轣ｫ縺吶ｋ縺薙→
  - TC-INT-012: 繝ｦ繝ｼ繧ｶ繝ｼOK驕ｸ謚槫ｾ後↓generate_transport_form縺悟他縺ｳ蜃ｺ縺輔ｌ繧九％縺ｨ
  - TC-INT-013: 繝ｦ繝ｼ繧ｶ繝ｼ繧ｭ繝｣繝ｳ繧ｻ繝ｫ譎ゅ↓generate_transport_form縺悟他縺ｳ蜃ｺ縺輔ｌ縺ｪ縺・％縺ｨ
  - TC-INT-020: 繧ｻ繝・す繝ｧ繝ｳ繝輔ぃ繧､繝ｫ縺茎torage/sessions/縺ｫ逕滓・縺輔ｌ繧九％縺ｨ
  - TC-INT-021: 譌｢蟄倥そ繝・す繝ｧ繝ｳ繝輔ぃ繧､繝ｫ縺九ｉ莨夊ｩｱ螻･豁ｴ縺悟ｾｩ蜈・＆繧後ｋ縺薙→

