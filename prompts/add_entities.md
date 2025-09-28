# Entity 추가 가이드라인

## 작업 순서

1. 키워드로부터 추가 정보를 web search
2. 외부 URL이 주어졌다면 이를 확인
3. 적절한 YAML 파일에 entity 추가
4. 기존 entities와의 relationship 확인 및 생성
5. 데이터 일관성 검증

## 파일 구조 예시

yaml file 명명 규칙:
* [entity 대분류: people, media 등  종류별로 구분된 이름] + [entity 소분류: actor, director 등 성격] + [entity 성격: 국가/언어별 구분] + `.yaml`

예시:
- `@data/datalink/people_actor_western.yaml` - 서양 배우
- `@data/datalink/people_actor_chinese.yaml` - 중국 배우
- `@data/datalink/people_actor_korean.yaml` - 한국 배우
- `@data/datalink/people_actor_japanese.yaml` - 일본 배우
- `@data/datalink/people_director_western.yaml` - 서양 감독
- `@data/datalink/people_composer.yaml` - 작곡가
- `@data/datalink/media_western.yaml` - 서양 영화/드라마
- `@data/datalink/media_chinese.yaml` - 중국 드라마
- `@data/datalink/media_japanese.yaml` - 일본 드라마

기존 파일이 없다면 위 규칙에 따라 새로 생성

## 주요 External URL Sources

국가별로 주요 외부 URL 소스는 다음과 같다.

한국
- 나무위키: `https://namu.wiki/w/[이름]`

중국
- 바이두 바이커: `https://baike.baidu.com/item/[중국어이름]`
- 나무위키: `https://namu.wiki/w/[한국어이름]` (있는 경우)

일본
- 나무위키: `https://namu.wiki/w/[일본이름]`
- 기본적으로 나무위키 우선

서양
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

## Relationship 확인 방법

기존 entities와의 relationship 확인 및 생성:
1. **인물 entity 추가 시**: 해당 인물이 출연한 작품이 기존 데이터에 있는지 검색
2. **작품 entity 추가 시**: 출연진/제작진이 기존 데이터에 있는지 검색
3. **Relationship 생성**: 발견된 연결점에 대해 relationship 추가
   - 배우 → 작품: `from: actor_id, to: media_id, type: starred_in`
   - 감독 → 작품: `from: director_id, to: media_id, type: directed`

## 작업 후 검증

- 모든 relationship이 유효한 entity를 참조하는지 확인
- 동일 인물/작품이 여러 파일에 중복되지 않았는지 확인
- External links가 접근 가능한지 확인
- 추가된 relationship이 올바른 entity ID를 참조하는지 확인