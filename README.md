<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=8FB4E1&height=200&section=header&text=%20ConnectME&fontSize=80&fontColor=ffffff"/>
<img width="500" alt="Connectme_logo" src="https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/c0c57819-39dd-42b9-8b11-45243e32a269">
</div>


🔗 Shortcut Link
------
**📱배포 : https://connectme.co.kr/**  
**🐋 Front-End : [Front-End Link](https://github.com/ChaeYami/ConnectMe_FE)**  
**💙 DOCS : [사회화지원소 팀노션](https://rhetorical-cilantro-7e4.notion.site/538c12449cf94e28b0c20a9f4ac0a3fc?v=96c787ffabfa458586546ec93833852b&pvs=4)**


***
📚 stacks 
------




|Category|Stacks|
|---|---|
| Backend | <img src="https://img.shields.io/badge/python 3.10.6 -3776AB?style=for-the-badge&logo=python&logoColor=white">  <img src="https://img.shields.io/badge/django 4.2.2-092E20?style=for-the-badge&logo=django&logoColor=white">  <img src="https://img.shields.io/badge/djangorestframework 3.14.0-092E20?style=for-the-badge&logo=django&logoColor=white"> <img src="https://img.shields.io/badge/simple jwt 5.2.2-092E20?style=for-the-badge&logo=django&logoColor=white">  <img src="https://img.shields.io/badge/selenium -43B02A?style=for-the-badge&logo=selenium&logoColor=white">  <img src="https://img.shields.io/badge/Channels 4.0.0-092E20?style=for-the-badge&logo=django&logoColor=white"> <img src="https://img.shields.io/badge/Redis -DC382D?style=for-the-badge&logo=redis&logoColor=white">  |
| Server | <img src="https://img.shields.io/badge/amazonec2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white"> <img src="https://img.shields.io/badge/gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white"> <img src="https://img.shields.io/badge/nginx 1.18.0-009639?style=for-the-badge&logo=nginx&logoColor=white"> <img src="https://img.shields.io/badge/docker 20.10.21 -2496ED?style=for-the-badge&logo=docker&logoColor=white"> <img src="https://img.shields.io/badge/amazons3 -569A31?style=for-the-badge&logo=amazons3&logoColor=white"> <img src="https://img.shields.io/badge/daphne-092E20?style=for-the-badge&logo=django&logoColor=white">  |
| Frontend | <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white">  <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/css3-1572B6?style=for-the-badge&logo=css3&logoColor=whit">  |
| Database | <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">|





***

🐳 Connect ME 
------
> 개발기간 : 2023.06.05 ~ 2023.07.10

![Connect ME](https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/59e83cdf-aedc-4425-9572-479c42123a92)



🐬 기능
------
### 회원기능

<details>
<summary>회원가입, 로그인</summary>
<div markdown = '1'></div>

- SMS(전화번호)인증 (아이디 찾기)
- 이메일 인증 (비밀번호 재설정)
- 소셜로그인
- 공개 프로필 / 비공개 프로필(개인정보)
- 만료된 토큰 사용자 자동 로그아웃

</details>

<details>
<summary>개인정보 관리</summary>
<div markdown='1'></div>

- 전화번호 변경 (SMS 인증)  
- 비밀번호 변경  
- 계정 비활성화 / 재활성화  
- 비활성화 계정 30일 후 자동 삭제  

</details>

<details>
<summary>프로필</summary>
<div markdown='1'></div>

- 친구신청 / 수락 / 거절 / 삭제
- 프로필 사진첩
- 공개 프로필 수정

</details>

<details>
<summary>신고기능</summary>
<div markdown='1'></div>

- 신고하기
- 누적 신고 3회시 임시 차단
- 임시 차단 후 24시간 경과시 자동 차단 해제
- 관리자 확인 가능

</details>


<details>
<summary>친구(유저) 추천</summary>
<div markdown='1'></div>

- 회원 정보(나이, 지역, MBTI)에 따른 유저 추천 목록

</details>



### 채팅 기능

<details>
<summary>1:1 채팅</summary>
<div markdown='1'></div>

- 채팅하기 버튼 -> 채팅방 자동 생성 / 입장
- 채팅방 참가 권한 인증 (jwt token)
- 입장/퇴장 메시지 출력
- 이전 채팅 메시지 불러오기 (50개까지)
- 참가중인 채팅방 목록

</details>

### 모임생성 (만남의 광장)

<details>
<summary>모임 모집 글 CRUD</summary>
<div markdown='1'></div>

- 작성 / 수정 / 삭제 / 좋아요
- 모임 날짜, 시간, 인원, 주소, 
- 모임 장소 보여주기 (지도API)
- 다중 이미지 업로드
- 댓글 작성/수정/삭제   
- 대댓글 작성/수정/삭제 

</details>

<details>
<summary>모임 참가하기 기능 </summary>
<div markdown='1'></div>

- 참가하기 / 취소하기
- 참가 인원 카운트
- 인원 제한

</details>

<details>
<summary>모임 상태 기능  </summary>
<div markdown='1'></div>

- 모집중, 모집 종료, 진행중, 모임종료, 자리없음

</details>


<details>
<summary>검색기능</summary>
<div markdown='1'></div>

- 모임 모집 글 검색  
- 지역 검색  

</details>


### 장소추천

<details>
<summary>장소 추천 글 CRUD </summary>
<div markdown='1'></div>

- 맛집 추천 글 작성/수정/삭제(관리자) / 조회(사용자)
- 사용자의 위치에 따른 맛집 추천 (지도 API, 위치 API)
- 다중 이미지 업로드  
- 맛집 추천 데이터 -> 크롤링  
- 북마크 : 북마크 모아보기
- 검색

</details>


<details>
<summary>댓글</summary>
<div markdown='1'></div>

- 댓글 작성/수정/삭제
- 대댓글 작성/수정/삭제

</details>

### 고민상담

<details>
<summary>고민상담 글 CRUD</summary>
<div markdown='1'></div>

- 상담 글 작성/수정/삭제/좋아요
- 상담 글 리스트   
- 상담 글 리스트 페이지네이션
- 익명기능

</details>


<details>
<summary>댓글</summary>
<div markdown='1'></div>

- 댓글 리스트/작성/수정/삭제/좋아요  
- 대댓글 리스트/작성/수정/삭제/좋아요
- 익명기능

</details>


🐬 POSITION
------


<details>
<summary>🤍 서채연(팀장)  </summary>
<div markdown='1'></div>

- User 앱 전반

    - 회원가입, 로그인, 계정 비활성화 / 소셜로그인 / 친구신청,수락,삭제 / 유저 신고 기능 등
    - SMS 인증(아이디 찾기) / 이메일 인증(비밀번호 재설정)
- counsel 앱
- Amazon S3 static 파일 업로드 + cloudfront 배포
- Validator 생성 및 적용
- 팀원 코드 피드백 및 리팩토링
- counsel app 테스트코드
- 팀 문서(노션,README) 작성 및 관리

</details>

<details>
<summary>🤍 노탁근(부팀장)  </summary>
<div markdown='1'></div>

- AWS, Docker, Nginx 배포 (Backend, server)
- 신고 유저 차단 기능

    - django-apscheduler
- 채팅 기능
    - 실시간 1:1채팅
    - django-channels
    - 채팅방 참가 권한 인증
- 실시간 알림 기능 (진행중)
    - django-channels
- 코드 리팩토링

</details>

<details>
<summary>🤍 이상민 </summary>
<div markdown='1'></div>

- Place 앱 전반
  
    - 맛집추천 CRUD : 권한 기반 접근 / 댓글, 대댓글 CRUD / 다중이미지 업로드 등
    - 맛집 추천 크롤링
- counsel 앱
- 유저 프로필 앨범 기능 / 위치 API - 유저 위치 저장
- user app 테스트코드
- place app 테스트코드

</details>

<details>
<summary>🤍 정재준  </summary>
<div markdown='1'></div>

- Meeting 앱 전반
    - meeting 게시글 CRUD / 댓글, 대댓글 CRUD / 다중이미지 업로드
    - 모임 상태 기능(자동 모집종료) - django-apscheduler
    - 모임 참가하기 기능 / 북마크 기능

- counsel 앱
</details>

<details>
<summary>🤍 장한울</summary>
<div markdown='1'></div>

- Counsel 앱 전반
    - counsel 게시글 CRUD / 댓글, 대댓글 CRUD
- meeting app 테스트코드

</details>

🐬 API , Dataset
------
- 소셜로그인
  - 구글 : Google OAuth API
  - 카카오 : KaKao OAuth 2.0 API
- SMS(전화번호)인증 : NAVER Cloud Simple & Easy Notification Service - SMS API
- 지도 : Kakao Maps API
- 위치 : Geolocation API
- 맛집 추천 크롤링 데이터 : [메뉴판닷컴](https://www.menupan.com/)


***


🐬 Service Architecture
------
![ConnectME 서비스 아키텍쳐](https://github.com/ChaeYami/ConnectMe_BE/assets/126448023/cb109020-f9a3-40e1-93dd-36938ed99af7)


🐬 ERD
------

![Connect ME (5)](https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/b1181afb-f7b4-48a8-9635-89e2a8a4d9c1)



🐬 Wireframe
------
![Group 21](https://github.com/ChaeYami/ConnectMe_BE/assets/120750451/fca58593-6d58-4302-9dae-a87af4e43e11)

