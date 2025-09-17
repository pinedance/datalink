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

## 구현

AI를 이용하여 초기 코드 작성







