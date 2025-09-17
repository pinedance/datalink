# About DataLink

DataLink은 평소 관심 있는 주제들을 연결된 데이터(Linked Data) 형태로 저장하고 관리하여, 웹에 시각화된 형태로 게시하는 프로젝트입니다.

## 프로젝트 목적

- **관심 주제 관리**: 영화, 책, 음악, 인물 등 다양한 주제의 데이터를 체계적으로 관리
- **관계 시각화**: 엔터티 간의 관계를 네트워크 그래프로 직관적으로 표현
- **웹 게시**: 정적 웹사이트 형태로 누구나 쉽게 접근할 수 있도록 게시

## 기술 구조

### Model: 데이터 관리
- **파일 형식**: YAML 파일 (`datalink.yaml`)
- **데이터 구조**: 엔터티(entities)와 관계(relationships)로 구성된 연결된 데이터
- **지원 타입**: 인물(Person), 영화(Movie), 장르(Genre), 책(Book), 음악(Music) 등

### View: 웹 시각화
- **테마**: Material for MkDocs
- **메인 페이지**: 인터랙티브 네트워크 그래프
- **상세 페이지**: 각 엔터티별 정보와 관계를 표시하는 동적 생성 페이지

### Controller: 자동화
- **빌드 시스템**: MkDocs + Python 스크립트
- **플러그인**:
  - `mkdocs-macros-plugin`: 동적 콘텐츠 생성
  - `mkdocs-gen-files`: 빌드 시점 페이지 생성
- **시각화**: vis-network.js 라이브러리

## 주요 기능

### 🌐 네트워크 그래프 시각화
- 인터랙티브한 네트워크 그래프로 엔터티 간 관계 표현
- 타입별 색상 구분으로 직관적인 이해 지원
- 클릭/호버 이벤트로 상세 정보 탐색 가능

### 📄 동적 페이지 생성
- 각 엔터티별 상세 페이지 자동 생성
- 관계 정보, 속성, 외부 링크 등 포괄적 정보 제공
- 반응형 디자인으로 다양한 디바이스 지원

### 🎨 반응형 디자인
- Material Design 기반의 현대적인 UI
- 다크/라이트 테마 자동 전환
- 모바일 친화적인 반응형 레이아웃

## 데이터 예시

현재 시스템에는 다음과 같은 샘플 데이터가 포함되어 있습니다:

{{ load_datalink() }}

{% set data = load_datalink() %}
{% for entity_type in data.entities | map(attribute='type') | unique %}
- **{{ entity_type.title() }}**: {{ data.entities | selectattr('type', 'equalto', entity_type) | list | length }}개
{% endfor %}

## 사용법

1. `datalink.yaml` 파일에 새로운 엔터티와 관계 추가
2. `mkdocs build` 또는 `mkdocs serve` 실행
3. 빌드 과정에서 자동으로 페이지 생성 및 네트워크 그래프 업데이트

## 기술 스택

- **Python**: 데이터 처리 및 페이지 생성
- **MkDocs**: 정적 사이트 생성기
- **Material for MkDocs**: UI 테마
- **vis-network.js**: 네트워크 시각화
- **YAML**: 데이터 저장 형식

---

DataLink 프로젝트는 개인의 관심사를 체계적으로 정리하고 공유하기 위한 도구로, 지속적인 발전과 개선을 통해 더욱 유용한 플랫폼으로 성장할 예정입니다.