# 모델 생성 추상화 기능

## 개요

모델 생성 시 `type`이 `'self-hosting'`인 경우, 파일 업로드와 모델 생성을 자동으로 처리하는 추상화 기능이 구현되었습니다.

## 기능

### 1. 자동 파일 업로드
- `type`이 `'self-hosting'`이고 `path`에 로컬 파일 경로가 지정된 경우
- 자동으로 `upload_model_file()`을 호출하여 파일을 업로드
- 응답의 `temp_file_path`를 `path` 필드에 설정
- 최종적으로 `create_model()`을 호출하여 모델 생성

### 2. 통합된 인터페이스

#### SDK 사용법

**Parameter Style (권장)**
```python
from adxp_sdk.models.hub import AXModelHub

hub = AXModelHub(credentials)

# 기본 사용법
result = hub.create_model(
    name="my-model",
    model_type="self-hosting",
    file_path="/path/to/model.bin"
)

# 고급 사용법
result = hub.create_model(
    name="gpt-model",
    model_type="language",
    display_name="GPT-3.5",
    description="Large language model for text generation",
    size="175B",
    token_size="2048",
    serving_type="serverless",
    is_private=True,
    file_path="/path/to/gpt-model.bin",
    tags=["llm", "gpt", "text-generation"],
    languages=["ko", "en"],
    tasks=["completion", "chat"],
    inference_param={"temperature": 0.7, "max_tokens": 100},
    default_params={"model": "gpt-3.5-turbo"}
)
```

**Dict Style (고급 사용자용)**
```python
# 기존 방식과 동일하게 dict로 전달
result = hub.create_model({
    "name": "my-model",
    "type": "self-hosting",
    "path": "/path/to/model.bin"  # 자동으로 업로드됨
})
```

#### CLI 사용법

**Parameter Style (권장)**
```bash
# 기본 사용법
adxp-cli model create --name "my-model" --type "self-hosting" --path "/path/to/model.bin"

# 고급 사용법
adxp-cli model create \
  --name "gpt-model" \
  --type "language" \
  --display-name "GPT-3.5" \
  --description "Large language model for text generation" \
  --size "175B" \
  --token-size "2048" \
  --serving-type "serverless" \
  --is-private \
  --path "/path/to/gpt-model.bin" \
  --tags "llm" "gpt" "text-generation" \
  --languages "ko" "en" \
  --tasks "completion" "chat" \
  --inference-param '{"temperature": 0.7, "max_tokens": 100}' \
  --default-params '{"model": "gpt-3.5-turbo"}'
```

**JSON File Style**
```bash
# JSON 파일로 모델 생성
adxp-cli model create --json model_config.json
```

## 지원되는 모든 필드

### 필수 필드
- `name` (str): 모델 이름
- `type` (str): 모델 타입 (`self-hosting`, `external`, `language` 등)

### 선택 필드
- `display_name` (str): 표시 이름
- `description` (str): 모델 설명
- `size` (str): 모델 크기
- `token_size` (str): 토큰 크기
- `dtype` (str): 데이터 타입
- `serving_type` (str): 서빙 타입 (예: `serverless`)
- `is_private` (bool): 비공개 여부
- `is_valid` (bool): 유효성 여부
- `license` (str): 라이선스 정보
- `readme` (str): README 내용
- `path` (str): 모델 파일 경로 (self-hosting 타입에서 필수)
- `provider_id` (str): 프로바이더 ID
- `project_id` (str): 프로젝트 ID
- `last_version` (int): 마지막 버전 번호
- `is_custom` (bool): 커스텀 모델 여부
- `custom_code_path` (str): 커스텀 코드 경로

### JSON 파라미터 필드
- `inference_param` (Dict): 추론 파라미터
- `quantization` (Dict): 양자화 파라미터
- `default_params` (Dict): 기본 파라미터

### 리스트 필드
- `tags` (List[str]): 태그 목록
- `languages` (List[str]): 언어 목록
- `tasks` (List[str]): 작업 목록

## 사용 스타일 비교

### Parameter Style (권장)
**장점:**
- IDE 자동완성 지원
- 타입 안전성
- 명확한 파라미터 이름
- 학습하기 쉬움

**사용 시기:**
- 간단한 모델 생성
- 대부분의 사용자

### Dict Style (고급)
**장점:**
- 유연한 구조
- 복잡한 설정에 적합
- 기존 API와 동일한 방식

**사용 시기:**
- 복잡한 모델 설정
- 고급 사용자

## 주의사항

1. **Self-hosting 모델**: `type`이 `'self-hosting'`인 경우 `path` 필드가 필수이며, 자동으로 파일 업로드가 수행됩니다.

2. **파일 경로**: 이미 `/tmp/`로 시작하는 경로는 업로드되지 않습니다 (이미 업로드된 파일로 간주).

3. **JSON 파라미터**: CLI에서 JSON 파라미터를 사용할 때는 유효한 JSON 문자열을 입력해야 합니다.

4. **통합된 인터페이스**: 하나의 메서드로 두 가지 스타일을 모두 지원하여 사용자 선택의 자유를 제공합니다. 