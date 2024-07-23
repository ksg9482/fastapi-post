# FastApi-Post

## Introduce
간단한 게시판 작성 프로젝트입니다.

## Pre-Require
* Python 3.11.9
* poetry

## Installation
가상환경 설정
```
poetry install
```

가상환경 실행
```
poetry shell
```
## Start
서버 실행
```
Dev: uvicorn main:app --reload
Prod: uvicorn main:app
```

## API
API 예시
```
POST /posts - 포스트 생성
GET /posts?page=1 - 전체 포스트 리스트
GET /posts/{post_id} - post_id 포스트

POST /users/login - 로그인
```

API 상세
```
http://localhost:8000/docs
```

## ERD
* mermaid.js
```mermaid
erDiagram
    POST ||--o{ COMMENT:""
    POST {
        int id PK "포스트 ID"
        str title "포스트 제목"
        str content "포스트 내용"
        datetime created_at "포스트 생성일자"
        datetime updated_at "포스트 갱신일자"
        int author_id FK "작성자 ID"
    }
    
    USER ||--o{ POST: ""
    USER ||--o{ COMMENT: ""
    USER {
        int id PK "유저 ID"
        str nickname "유저닉네임"
        str password "유저 비밀번호"
        datetime created_at "포스트 생성일자"
        datetime updated_at "포스트 갱신일자"
    }

    COMMENT {
        int id PK ""
        str content ""
        int author_id FK ""
        int post_id FK ""
    }
```