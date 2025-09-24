# Entity 추가 가이드라인

## 작업 순서
1. 키워드로부터 추가 정보를 외부 URL에서 수집
2. 적절한 YAML 파일에 entity 추가
3. 필요한 relationship 생성
4. 데이터 일관성 검증

## 파일 구조
- `@data/datalink/people_actor_western.yaml` - 서양 배우
- `@data/datalink/people_actor_chinese.yaml` - 중국 배우
- `@data/datalink/people_actor_korean.yaml` - 한국 배우
- `@data/datalink/people_actor_japanese.yaml` - 일본 배우
- `@data/datalink/people_director_western.yaml` - 서양 감독
- `@data/datalink/people_composer.yaml` - 작곡가
- `@data/datalink/media_western.yaml` - 서양 영화/드라마
- `@data/datalink/media_chinese.yaml` - 중국 드라마
- `@data/datalink/media_japanese.yaml` - 일본 드라마
- 필요하다면 새로 생성

## 국가별 주요 External URL Sources

### 한국
- 나무위키: `https://namu.wiki/w/[이름]`
- 기본 패턴 사용

### 중국
- 바이두 바이커: `https://baike.baidu.com/item/[중국어이름]`
- 나무위키: `https://namu.wiki/w/[한국어이름]` (있는 경우)

### 일본
- 나무위키: `https://namu.wiki/w/[일본이름]`
- 기본적으로 나무위키 우선

### 서양
- IMDb: `https://www.imdb.com/name/[id]/` (배우/감독)
- IMDb: `https://www.imdb.com/title/[id]/` (영화/드라마)
- Wikipedia: `https://en.wikipedia.org/wiki/[이름]`
- 나무위키: `https://namu.wiki/w/[한국어이름]` (있는 경우)

## 중요 규칙

1. **External URL 수집**: 주어진 키워드로 적절한 소스에서 정보 수집
2. **ID 명명**: 영어 소문자 + 언더스코어 사용
3. **Relationship 검증**: 참조하는 entity가 존재하는지 확인
4. **태그 활용**: 특별한 속성은 tags 배열에 추가 (예: ["목소리가 좋은 배우"])
5. **일관성 유지**: 기존 데이터 구조와 동일한 형식 사용
6. **적절한 파일 선택**: 국가/언어별로 올바른 파일에 추가

## 작업 후 검증
- 모든 relationship이 유효한 entity를 참조하는지 확인
- 동일 인물/작품이 여러 파일에 중복되지 않았는지 확인
- External links가 접근 가능한지 확인