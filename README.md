<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=8FB4E1&height=200&section=header&text=%20Connect%20Me&fontSize=80&fontColor=ffffff"/>
<img width="500" alt="Connectme_logo" src="https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/c0c57819-39dd-42b9-8b11-45243e32a269">
</div>


📱 배포
------
https://connectme.co.kr/

📚 stacks 
------

<img src="https://img.shields.io/badge/python 3.10.6 -3776AB?style=for-the-badge&logo=python&logoColor=white">  <img src="https://img.shields.io/badge/django 4.2.2-092E20?style=for-the-badge&logo=django&logoColor=white">  <img src="https://img.shields.io/badge/djangorestframework 3.14.0-092E20?style=for-the-badge&logo=django&logoColor=white">  <img src="https://img.shields.io/badge/selenium -43B02A?style=for-the-badge&logo=selenium&logoColor=white"> 
 <br> <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white">  <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
<br>  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">  <img src="https://img.shields.io/badge/amazonec2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white"> <img src="https://img.shields.io/badge/gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white"> <img src="https://img.shields.io/badge/nginx 1.18.0-009639?style=for-the-badge&logo=nginx&logoColor=white"> <img src="https://img.shields.io/badge/docker 20.10.21 -2496ED?style=for-the-badge&logo=docker&logoColor=white">
<br><img src="https://img.shields.io/badge/amazons3 -569A31?style=for-the-badge&logo=amazons3&logoColor=white">


***

🐳 Connect ME : 함께 놀고 소통하며 즐거움을 찾는 커뮤니티 🎉
------
> 2023.06.05 ~
  

🐋 Front-End 
------
[Front-End Link](https://github.com/ChaeYami/ConnectMe_FE)

🐬 기획
------
🎉 다 같이 놀자! 🎉
- 함께 맛집도 찾아가고, 공통의 취미를 즐기며, 새로운 친구들을 만나고 싶은 분들을 위한 특별한 커뮤니티💫   

🌟 소통을 위한 다양한 공간 🌟  
- 채팅, 게시판, 모임 등을 통해 쉽게 다른 회원들과 소통하고 교류할 수 있습니다. 

🌍 원하는 곳에서 다양한 친구들과 함께해보세요! 🌍
- 원하는 지역에서 많은 친구와 함께 즐거운 시간을 보낼 수 있습니다. 함께 맛집을 탐방하거나, 공통의 취미를 통해 새로운 친구들을 만나보세요. 이제 더 이상 바쁜 친구들을 재촉할 필요가 없습니다!

🐬 기능 - 작성중
------
### 회원기능
<details>
<summary>회원가입, 로그인 `jwt token` </summary>
<div markdown="1">
- 회원가입시 SMS(전화번호)인증, 이메일 인증  
- 소셜로그인  
</div>
</details>
- 개인정보 관리(비공개프로필), 공개프로필, 비활성화, 재활성화, 비활성화 계정 30일후 삭제  
SMS 인증(회원가입, 아이디 찾기), 이메일 인증(회원가입, 비밀번호 재설정), 소셜로그인  
친구신청, 수락, 거절, 삭제   
신고, 누적신고 임시차단, 차단 자동 해제  
친구 추천 - 회원정보(나이, 지역, MBTI)에 따른 유저 목록


### 모임생성 (만남의 광장)
모임 모집 글 작성/수정/삭제/좋아요  - 모임 날짜, 시간, 인원, 주소, 장소(지도API), 다중 이미지 업로드
모임 참가하기 기능 - 참가하기/취소하기, 참가 인원 카운트, 인원 제한
모임 상태 기능 -  모집중, 모집 종료, 진행중, 모임종료, 자리없음
모임 모집 글/지역 검색 기능   
댓글 작성/수정/삭제   
대댓글 작성/수정/삭제  



### 채팅



### 장소추천
맛집 추천 글 작성/수정/삭제 -> 관리자만 , 조회 -> 사용자 , 다중 이미지 업로드
맛집 추천 데이터 - 크롤링 / 지도 API
사용자의 위치에 따른 맛집 리스트 추천
맛집 추천 글 북마크, 북마크 글 모아보기
댓글 작성/수정/삭제
대댓글 작성/수정/삭제


### 고민상담
상담 글 작성/수정/삭제/조회/좋아요  
댓글 리스트/작성/수정/삭제/좋아요  
대댓글 리스트/작성/수정/삭제/좋아요  
상담 글 리스트 페이지네이션


🐬 POSITION
------
🤍 서채연(팀장)  
- User 앱 전반
    - 회원가입, 로그인 / 소셜로그인 / 친구신청,수락,삭제 등 / 유저 신고 기능 등 user 앱 기능 전반
    - SMS 인증 - 아이디 찾기 / 이메일 인증 - 비밀번호 재설정
- Amazon S3 static 파일 업로드 + cloudfront 배포
- Validator 생성 및 적용
- 팀원 코드 피드백 및 리팩토링
- counsel app 테스트코드
  
🤍 노탁근(부팀장)  
- Docker, AWS 배포
    - nginx, Backend, PostgreSQL
- 신고 유저 차단 기능
    - django-apscheduler
- 채팅, 알림기능 (진행중)
    - redis, daphne, django-channels

🤍 이상민  
- Place 앱 전반
    - 맛집추천 CRUD : 권한 기반 접근 / 댓글, 대댓글 CRUD / 다중이미지 업로드 등 place 앱 기능 전반
    - 맛집 추천 크롤링
- 유저 프로필 앨범 기능 / 위치 API - 유저 위치 저장
- user app 테스트코드
- place app 테스트코드

🤍 정재준  
- Meeting 앱 전반
    - meeting 게시글 CRUD / 댓글, 대댓글 CRUD / 다중이미지 업로드 

🤍 장한울
- Counsel 앱 전반
    - counsel 게시글 CRUD / 댓글, 대댓글 CRUD
- meeting app 테스트코드

***
🐬 ERD
------
![Connect ME](https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/b20a578d-cc72-43c7-ba50-98eb0fd5a90c)



🐬 와이어프레임
------
![Group 21](https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/fca58593-6d58-4302-9dae-a87af4e43e11)


🐬 서비스 아키텍쳐
------
![ConnectME 중간발표 서비스 아키텍쳐](https://github.com/PunciaTail/drf_homework/assets/120395814/a506d3db-88c8-4e2d-87fa-747d18a1e74e)



🐬 팀 프로젝트 문서 
------
[사회화지원소 팀노션](https://rhetorical-cilantro-7e4.notion.site/538c12449cf94e28b0c20a9f4ac0a3fc?v=96c787ffabfa458586546ec93833852b&pvs=4)
