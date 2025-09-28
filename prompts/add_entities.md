# Entity 추가 실전 가이드

## 핵심 작업 흐름

### 1단계: TodoWrite 도구로 작업 계획 수립
```
TodoWrite: [
  "키워드 '{키워드}'에 대한 정보 수집",
  "적절한 YAML 파일 찾기 및 entity 추가",
  "기존 entities와의 relationship 확인 및 추가",
  "데이터 일관성 검증"
]
```

### 2단계: WebFetch로 정보 수집
**국가별 URL 패턴:**
- 한국: `https://namu.wiki/w/{이름}`
- 중국: `https://namu.wiki/w/{한국어이름}` 또는 `https://baike.baidu.com/item/{중국어이름}`
- 일본: `https://namu.wiki/w/{일본이름}`
- 서양: `https://www.imdb.com/name/{id}/` 또는 `https://en.wikipedia.org/wiki/{이름}`

**WebFetch 프롬프트 예시:**
```
"{키워드}에 대한 기본 정보를 추출해주세요. 이름, 국적, 생년월일, 주요 작품, 배우인지 감독인지 등의 정보를 포함해서 정리해주세요."
```

### 3단계: 적절한 YAML 파일 확인
**Glob 도구 사용:**
```
Glob pattern: "data/datalink/*.yaml"
```

**파일명 규칙:**
- `people_actor_{country}.yaml` - 배우
- `people_director_{country}.yaml` - 감독
- `people_composer.yaml` - 작곡가
- `media_{country}.yaml` - 영화/드라마

### 4단계: 기존 데이터와 relationship 확인 (중요!)

**4-1. 인물 추가 시 - 출연 작품 검색:**
```
Grep pattern: "{인물의 다양한 이름 패턴}"
glob: "data/datalink/*.yaml"
output_mode: "content"
-i: true
```

**4-2. 작품 추가 시 - 출연진/제작진 검색:**
작품 정보 수집 후 주연/조연 배우들을 검색:
```
WebFetch prompt: "{작품명}의 전체 출연진 리스트를 추출해주세요. 주연뿐만 아니라 조연, 특별출연 등 모든 배우들의 이름을 정리해주세요."
```

그 후 각 배우명으로 기존 데이터 검색:
```
Grep pattern: "{배우1}|{배우2}|{배우3}"
glob: "data/datalink/*.yaml"
```

### 5단계: Entity 추가
**Read 도구로 기존 파일 구조 확인 후 Edit/MultiEdit 사용**

**ID 명명 규칙:**
- 영어 소문자 + 언더스코어
- 예: `zhang_ruonan`, `nan_hong`, `christopher_nolan`

**필수 필드:**
- `id`: 고유 식별자
- `type`: "인물" 또는 "TV시리즈" 등
- `name`: 원어명 (한국어명)
- `description`: 간단한 설명
- `properties`: 상세 정보
- `external_links`: 참고 URL

### 6단계: Relationship 추가
**단방향 관계만 생성:**
- 배우 → 작품: `from: actor_id, to: media_id, type: starred_in`
- 감독 → 작품: `from: director_id, to: media_id, type: directed`
- 작곡가 → 작품: `from: composer_id, to: media_id, type: composed`

**배우 파일에만 추가** (미디어 파일에는 중복 추가하지 않음)

## 검색 패턴 예시

### 중국 배우/작품 검색:
```
Grep pattern: "{한국어이름}|{중국어이름}|{영어이름}"
```

### 일본 배우/작품 검색:
```
Grep pattern: "{일본어이름}|{한국어이름}|{로마자이름}"
```

### 서양 배우/작품 검색:
```
Grep pattern: "{영어이름}|{한국어이름}"
```

## 실제 작업 예시

### 예시 1: "난홍" 드라마 추가
1. `WebFetch("https://namu.wiki/w/난홍")` - 기본 정보 수집
2. `Glob("data/datalink/*chinese*.yaml")` - 중국 미디어 파일 찾기
3. `Read("media_chinese.yaml")` - 기존 구조 확인
4. `Edit()` - 난홍 entity 추가
5. `Grep("백경정|白敬亭|장약남|章若楠", "**/*.yaml")` - 출연진 검색
6. `Edit()` - 발견된 relationship 추가

### 예시 2: 조연진 relationship 확인
1. `WebFetch()` - 추가 출연진 정보 수집
2. `Grep("장묘이|张淼怡|진호삼|陈虎三", "**/*.yaml")` - 다중 검색
3. `Edit()` - 매칭된 배우들의 relationship 추가

## 자주하는 실수 방지

❌ **하지 말아야 할 것:**
- 미디어 파일에 relationship 중복 추가 (linked data 일관성 위배)
- 검색 없이 바로 entity 추가
- 단일 이름으로만 검색 (다양한 이름 패턴 고려 안함)

✅ **해야 할 것:**
- 항상 다양한 이름 패턴으로 검색 (원어명, 한국어명, 영어명)
- 배우 파일에만 relationship 추가
- 작업 전 TodoWrite로 계획 수립

## 검증 체크리스트

- [ ] 모든 relationship이 존재하는 entity를 참조하는가?
- [ ] 중복된 entity가 없는가?
- [ ] External links가 접근 가능한가?
- [ ] ID 명명 규칙을 따랐는가?
- [ ] 단방향 relationship인가? (배우→작품만)

