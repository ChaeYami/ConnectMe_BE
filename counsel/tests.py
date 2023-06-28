from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from user.models import User, Profile
from counsel.models import (
    Counsel,
    CounselComment,
    CounselReply,
)

class CounselListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)

        # cls.counsel_data = {"title":"test title", "content":"test content"}
        # cls.counsel = Counsel.objects.create(**cls.counsel_data, user = cls.user)

        cls.user.is_active = True
        cls.user.save()

    def setUp(self):
        self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]

    # 전체 게시글 조회
    def test_all_counsel_list(self):
        response = self.client.get(
            path=reverse("counsel_view"),
            HTTP_AUTHORIZATION = f"Bearer{self.access_token}",
        )
        self.assertEqual(response.status_code, 200)


''' 게시글 작성 '''
class CounselViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title":"test title", "content":"test content"}
        # cls.counsel = Counsel.objects.create(**cls.counsel_data, user = cls.user)

        cls.user.is_active = True
        cls.user.save()

    def setUp(self):
        self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]

    ''' 로그인 테스트 '''
    def test_login(self):
        url = reverse("user:login_view")
        data = {
            'account': self.account,
            'password': self.password
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 로그인 요청이 성공적으로 처리되었는지 확인


    # 게시글 작성 성공
    def test_counsel_create(self):
        response = self.client.post(
            path=reverse("counsel_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
            data=self.counsel_data,
            )

        self.assertEqual(response.status_code, 200)

    # 게시글 작성 실패 - 비로그인
    def test_fail_if_not_logged_in_counsel_post(self):
        response = self.client.post(
            path=reverse("counsel_view"),
            data=self.counsel_data,
            )
        self.assertEqual(response.status_code, 401) # Unauthorized

    # 게시글 작성 실패 - 제목없음
    def test_counsel_create_no_title(self):
        response = self.client.post(
            path=reverse("counsel_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
            data={"title" : "", "content" : "test content"},
            )
        self.assertEqual(response.status_code, 400) # serializer is_valid = False

    # 게시글 작성 실패 - 내용없음
    def test_counsel_create_no_content(self):
        response = self.client.post(
            path=reverse("counsel_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
            data={"title" : "test title", "content" : ""},
            )
        self.assertEqual(response.status_code, 400) # serializer is_valid = False


''' 게시글 상세, 수정, 삭제 '''

class CounselDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)

        cls.counsel_data = [
            {"title":"test title1", "content":"test content1"},
            {"title":"test title2", "content":"test content2"},
            {"title":"test title3", "content":"test content3"},
            {"title":"test title4", "content":"test content4"},
            {"title":"test title5", "content":"test content5"},
        ]

        cls.counsel =[]

        for i in range(5):
            cls.counsel.append(
                Counsel.objects.create(**cls.counsel_data[i], user = cls.user)
            )

    def setUp(self):
        # self.access_token = self.client.post(reverse('user:login_view'), self.user_data).data['access']
        self.client.force_authenticate(user=self.user) # 토큰없이 로그인


    '''상세보기'''
    def test_counsel_detail(self):
        response = self.client.get(
            path=reverse("counsel_detail_view", kwargs={"counsel_id" : 5}),
            # HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)


    '''수정하기'''
    def test_counsel_detail_update(self):
        self.counsel_data = {
            "title":"update test title", "content":"update test content"
            }
        response = self.client.put(
            path=reverse("counsel_detail_view", kwargs={"counsel_id":5}),
            data=self.counsel_data,
            # HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Counsel.objects.count(),5)
        self.assertEqual(response.data["title"], "update test title")
        self.assertEqual(response.data["content"], "update test content")

    '''삭제'''
    def test_counsel_detail_delete(self):
        response = self.client.delete(
            path=reverse("counsel_detail_view", kwargs={"counsel_id":5})
            # HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Counsel.objects.count(),4)
        self.assertEqual(response.data,{'message': '삭제 완료'})


""" 게시글 좋아요 """
class CounselLikeViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title": "test Title", "content": "test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user=cls.user)
        cls.counsel_2 = Counsel.objects.create(**cls.counsel_data, user=cls.user)
        cls.counsel_2.like.add(cls.user)


    def setUp(self):
        # self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)


    '''좋아요 누르기'''
    def test_counsel_like(self):
        url = reverse("counsel_like_view", kwargs={"counsel_id": self.counsel.id})

        response = self.client.post(url)
        # print(response.data)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data, {"message":"좋아요"})

    '''좋아요 취소하기'''
    def test_counsel_like_cancel(self):
        url = reverse("counsel_like_view", kwargs={"counsel_id": self.counsel_2.id})

        response = self.client.post(url)
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message":"좋아요 취소"})


""" 댓글 """
class CommentViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title":"test title", "content":"test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user = cls.user)

        cls.comment_data = {"content":"test content"}

    def setUp(self):
        self.client.force_authenticate(user=self.user) # 토큰없이 로그인

    '''댓글작성'''
    def test_counsel_comment_create(self):
        response = self.client.post(
            path = reverse("counsel_comment_view", kwargs={"counsel_id" : self.counsel.id}),
            data=self.comment_data,
            # HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
        )
        # print(CounselComment)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CounselComment.objects.count(), 1)
        self.assertEqual(CounselComment.objects.get().content, self.comment_data["content"])

    '''댓글 리스트'''
    def test_counsel_comment_list(self):
        self.comments=[]
        for _ in range(5):
            self.comments.append(
                CounselComment.objects.create(
                    content = "comment", counsel = self.counsel, user= self.user
                )
            )

        response = self.client.get(
            path=reverse("counsel_comment_view", kwargs={"counsel_id":self.counsel.id}),

        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselComment.objects.count(), 5)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["content"], "comment")


""" 댓글 상세 (수정/삭제) """
class CommentDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)


        cls.counsel_data = {"title": "test Title", "content": "test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user=cls.user)

        cls.comment_data = {"content": "test comment"}
        cls.comment_data = [
            {"content": "test 1"},
            {"content": "test 2"},
            {"content": "test 3"},
            {"content": "test 4"},
            {"content": "test 5"},
        ]

        cls.comment = []
        for _ in range(5):
            cls.comment.append(
                CounselComment.objects.create(
                    content="comment", counsel=cls.counsel, user=cls.user
                )
            )

    def setUp(self):
        # self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)


    '''댓글수정'''
    def test_counsel_comment_update(self):
        comment_id = self.comment[0].id  # 삭제할 댓글의 ID
        self.comment_data = {
            "content":"update test comment"
            }
        response = self.client.put(
            path=reverse("counsel_detail_comment_view", kwargs={"counsel_id":1, "counsel_comment_id": comment_id}),
            data=self.counsel_data,
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        # print(response.data)
        # print(CounselComment.objects.count())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselComment.objects.count(), 5)
        self.assertEqual(response.data, {'meesage': '수정완료'})

    '''댓글삭제'''
    def test_counsel_comment_delete(self):
        comment_id = self.comment[0].id  # 삭제할 댓글의 ID
        response = self.client.delete(
            path=reverse("counsel_detail_comment_view", kwargs={"counsel_id":1, "counsel_comment_id": comment_id}),
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselComment.objects.count(), 4)
        self.assertEqual(response.data, {'message': '삭제 완료'})


""" 대댓글 """


class ReplyViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = "test1account"
        cls.email = "test1@naver.com"
        cls.phone = "01012345678"
        cls.password = "test1234!!"
        cls.user_data = {"account": "test1account", "password": "test1234!!"}
        cls.user = User.objects.create_user(
            account=cls.account, email=cls.email, phone=cls.phone, password=cls.password
        )
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title": "test title", "content": "test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user=cls.user)

        cls.comment = CounselComment.objects.create(
            content="comment", counsel=cls.counsel, user=cls.user
        )
        cls.reply_data = {"content": "test reply"}

    def setUp(self):
        self.client.force_authenticate(user=self.user)  # 토큰없이 로그인

    """대댓글 작성"""

    def test_counsel_reply_create(self):
        response = self.client.post(
            path=reverse(
                "counsel_reply_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_comment_id": self.comment.id,
                },
            ),
            data=self.reply_data,
            # HTTP_AUTHORIZATION = f"Bearer {self.access_token}",
        )
        # print(response.status_code)
        # print(CounselReply.objects.count())
        # print(CounselReply.objects.get().content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselReply.objects.count(), 1)
        self.assertEqual(CounselReply.objects.get().content, self.reply_data["content"])

    """대댓글 리스트"""

    def test_counsel_reply_list(self):
        self.reply = []
        for _ in range(5):
            self.reply.append(
                CounselReply.objects.create(
                    content="test reply", counsel=self.counsel, comment = self.comment, user=self.user
                )
            )

        response = self.client.get(
            path=reverse(
                "counsel_reply_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_comment_id": self.comment.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselReply.objects.count(), 5)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["content"], self.reply_data["content"])


""" 대댓글 상세 (수정/삭제) """

class CommentDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = "test1account"
        cls.email = "test1@naver.com"
        cls.phone = "01012345678"
        cls.password = "test1234!!"
        cls.user_data = {"account": "test1account", "password": "test1234!!"}
        cls.user = User.objects.create_user(
            account=cls.account, email=cls.email, phone=cls.phone, password=cls.password
        )
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title": "test Title", "content": "test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user=cls.user)

        cls.comment = CounselComment.objects.create(
            content="comment", counsel=cls.counsel, user=cls.user
        )

        cls.reply_data = [
            {"content": "test reply 1"},
            {"content": "test reply 2"},
            {"content": "test reply 3"},
            {"content": "test reply 4"},
            {"content": "test reply 5"},
        ]

        cls.reply = []
        for _ in range(5):
            cls.reply.append(
                CounselReply.objects.create(
                    content="test reply", counsel=cls.counsel, comment=cls.comment, user=cls.user
                )
            )

    def setUp(self):
        # self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)

    """대댓글수정"""

    def test_counsel_reply_update(self):
        self.reply_data = {"content": "update test reply"}
        response = self.client.put(
            path=reverse(
                "counsel_reply_detail_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_reply_id": self.reply[0].id,
                },
            ),
            data=self.counsel_data,
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'message': '성공.'})
        self.assertEqual(CounselReply.objects.count(), 5)


    '''댓글삭제'''
    def test_counsel_comment_delete(self):
        response = self.client.delete(
            path=reverse(
                "counsel_reply_detail_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_reply_id": self.reply[0].id,
                },
            ),
        )
        self.assertEqual(response.data,{'message': '삭제완료'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(CounselReply.objects.count(),4)

""" 댓글 좋아요 """


class CounselCommentLikelViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = "test1account"
        cls.email = "test1@naver.com"
        cls.phone = "01012345678"
        cls.password = "test1234!!"
        cls.user_data = {"account": "test1account", "password": "test1234!!"}
        cls.user = User.objects.create_user(
            account=cls.account, email=cls.email, phone=cls.phone, password=cls.password
        )
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title": "test Title", "content": "test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user=cls.user)

        cls.comment = CounselComment.objects.create(
            content="comment", counsel=cls.counsel, user=cls.user
        )
        cls.comment_2 = CounselComment.objects.create(
            content="comment 2", counsel=cls.counsel, user=cls.user
        )
        cls.comment_2.like.add(cls.user)

    def setUp(self):
        # self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)

    """좋아요 누르기"""
    def test_counsel_commnet_like(self):

        response = self.client.post(
            path=reverse(
                "counsel_comment_like_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_comment_id": self.comment.id,
                },
            )
        )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data, '댓글 좋아요')

    """좋아요 취소하기"""
    def test_counsel_commnet_like_cancel(self):
        response = self.client.post(
            path=reverse(
                "counsel_comment_like_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_comment_id": self.comment_2.id,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, '댓글 좋아요 취소')


""" 대댓글 좋아요 """


class CounselReplyLikelViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = "test1account"
        cls.email = "test1@naver.com"
        cls.phone = "01012345678"
        cls.password = "test1234!!"
        cls.user_data = {"account": "test1account", "password": "test1234!!"}
        cls.user = User.objects.create_user(
            account=cls.account, email=cls.email, phone=cls.phone, password=cls.password
        )
        Profile.objects.create(user=cls.user)

        cls.counsel_data = {"title": "test Title", "content": "test content"}
        cls.counsel = Counsel.objects.create(**cls.counsel_data, user=cls.user)

        cls.comment = CounselComment.objects.create(
            content="comment", counsel=cls.counsel, user=cls.user
        )

        cls.reply = CounselReply.objects.create(
            content="test reply",
            counsel=cls.counsel,
            comment=cls.comment,
            user=cls.user,
        )
        cls.reply_2 = CounselReply.objects.create(
            content="test reply 2",
            counsel=cls.counsel,
            comment=cls.comment,
            user=cls.user,
        )
        cls.reply_2.like.add(cls.user)

    def setUp(self):
        # self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)

    """좋아요 누르기"""

    def test_counsel_reply_like(self):
        response = self.client.post(
            path=reverse(
                "counsel_reply_like_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_reply_id": self.reply.id,
                },
            )
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data, '좋아요')


    """좋아요 취소하기"""

    def test_counsel_comment_like_cancel(self):
        response = self.client.post(
            path=reverse(
                "counsel_reply_like_view",
                kwargs={
                    "counsel_id": self.counsel.id,
                    "counsel_reply_id": self.reply_2.id,
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, '좋아요 취소')
