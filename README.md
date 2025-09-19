# DataLink

## 목적

다음 목적을 위한 프로젝트

* 평소 관심 있는 주제를 linked data 형태로 저장하고 관리
* 그 내용을 web에 게시하기

## 방법

Model: 관심 주제 데이터 (linked data 형식, yaml file로 관리)

* `datalink.yaml` 파일에 각각의 데이터 소스 정보 입력 및 관리
* 이 파일에는 linked data 형식으로 데이터를 생성하고 관리함
* 예를 들어 영화배우, 영화, 책, 음악 등 다양한 데이터 소스를 연결하여 관리할 수 있음, 외부 링크도 추가

View: Static Web Page로 배포

* material for mkdocs 테마를 사용
* 메인 페이지에는 datalink.yaml에 입력된 linked data를 기반으로 네트워크 그래프를 시각화하여 표시
* 각 node를 클릭하면 해당 데이터 소스에 대한 상세 페이지로 이동

Controler: datalink.yaml 속 데이터를 바탕으로 페이지 생성에 필요한 부분 자동화

* [mkdocs-macros-plugin](https://mkdocs-macros-plugin.readthedocs.io/en/latest/) 및 custom python script 사용
* mkdocs build 시점에 datalink.yaml 파일을 읽어와
  * linked data를 생성하고, 이를 기반으로 네트워크 그래프를 생성
  * 각 상세 페이지 동적으로 생성

## 현재 구조

### 데이터 플로우
1. **YAML 파일** (`data/datalink/*.yaml`) → **Python 스크립트** (`generate_pages.py`) → **JSON 파일** (`site/data/*.json`)
2. **클라이언트** → **AJAX 요청** → **JSON 데이터** → **동적 렌더링**

### 주요 컴포넌트

#### Backend (Python)
- `core_datalink.py`: YAML 데이터 로드 및 파싱 유틸리티
- `generate_pages.py`: 빌드 시점에 JSON 데이터 파일 생성
- `main.py`: MkDocs 매크로 플러그인 훅

#### Frontend (JavaScript)
- `network.js`: 네트워크 그래프 시각화 (vis-network 기반)
- `entity.js`: 개별 엔티티 페이지 렌더링 및 라우팅
- `gallery.js`: 이미지 갤러리 및 라이트박스 기능

#### 페이지 구조
- `index.md`: 메인 페이지 (네트워크 그래프)
- `entities/index.md`: 엔티티 목록 페이지
- `entities/entity.md`: 단일 엔티티 뷰어 (hash 라우팅)

### 빌드 과정
1. **YAML 로드**: `data/datalink/` 폴더의 모든 YAML 파일 읽기
2. **JSON 생성**:
   - `site/data/network.json`: 네트워크 그래프용 노드/엣지 데이터
   - `site/data/entities-meta.json`: 엔티티 메타데이터
   - `site/data/relationships.json`: 모든 관계 데이터
   - `site/data/entities/{id}.json`: 개별 엔티티 상세 데이터
3. **정적 페이지 생성**: MkDocs Material 테마 적용

## 개발 및 배포

### 로컬 개발
```bash
# 개발 서버 실행
uv run mkdocs serve

# 프로덕션 빌드
uv run mkdocs build
```

### 데이터 추가
1. `data/datalink/` 폴더에 새 YAML 파일 생성
2. 엔티티와 관계 정의
3. 빌드 시 자동으로 JSON 데이터 및 페이지 생성

### 이미지 추가
- 외부 이미지: YAML의 `image_links` 배열에 URL 추가
- 로컬 이미지: `docs/images/{entity_id}/` 폴더에 이미지 파일 저장

## 기술 스택

- **Static Site Generator**: MkDocs + Material Theme
- **Data Processing**: Python (PyYAML)
- **Visualization**: vis-network.js
- **Frontend**: Vanilla JavaScript (ES6+)
- **Build Tool**: mkdocs-gen-files, mkdocs-macros-plugin
