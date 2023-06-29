from django.urls import reverse
from rest_framework.test import APITestCase
from user.models import User
from meeting.models import Meeting
from meeting.models import MeetingComment


class MeetingBaseTestCase(APITestCase):
    """모임글기능 테스틑 준비

    모임글기능 테스트를 위한 부모 클래스입니다.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(
            account="testuser1",
            email="testuser1@test.com",
            phone="01012345678",
        )
        cls.user_login_data = {"account": "testuser1", "password": "@testuser1234"}

        cls.meeting = MeetingComment.objects.create(author=cls.user)
        cls.meeting_create_date = {
            "user": "edit",
            "title": "edit",
            "content": "edit",
            "created_at": "edit",
            "updated_at": "edit",
            "bookmark": "edit",
        }
        cls.meeting_edit_data = {
            "user": "edit",
            "title": "edit",
            "content": "edit",
            "created_at": "edit",
            "updated_at": "edit",
            "bookmark": "edit",
        }
        cls.meeting = MeetingComment.objects.create(
            author=cls.user, Meeting=cls.meeting
        )
        cls.meeting_create_data = {"content": "test"}
        cls.meeting_edit_data = {"content": "edit"}
        cls.user = User.objects.create = {"content": "edit"}

    def setUp(self) -> None:
        login_user = self.client.post(reverse("token"), self.user_login_data).data
        self.access = login_user["access"]
        self.refresh = login_user["refresh"]


class Meeting(MeetingBaseTestCase):
    """모임 글 작성 및 조회 테스트


    모임 글 테스트를 합니다.
    """

    def test_meeting_writing(self):
        """모임 글 테스트

        모임글 테스트 입니다.
        """

        url = reverse("meeting") + "?page=1&filter=meeting"
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)

    def test_meeting_bookmark(self):
        """북마크 모임글 조회

        북마크 모임글 조회 테스트입니다.
        """

        url = reverse("bookmark") + "?page=1&filter=bookmarked"
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )

        self.assertEqual(response.status_code, 200)

    def test_meeting_user(self):
        """작성자 모임글 조회

        작성자 모임글 조회 테스트입니다.
        """

        url = reverse("meeting") + "?user=1&filter=user&user_id=1"
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)


class MeetingDetailTestCase(MeetingBaseTestCase):
    """모임글상세 테스트

    모임글상세보기, 수정, 삭제를 테스트합니다.
    """

    def test_meeting_create_detail(self):
        """모임글 상세보기

        모임글 상세보기 테스트입니다.
        """
        url = reverse(
            "meeting_detail", kwargs={"meeting_comment": self.meeting.comment}
        )
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)

    def test_article_put(self):
        """모임글 수정

        모임글 수정 테스트입니다.
        """

        url = reverse(
            "meeting_detail", kwargs={"meeting_comment": self.meeting.comment}
        )
        data = self.meeting_edit_data
        response = self.client.put(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
            data=data,
        )
        self.assertAlmostEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "수정완료"})

    def test_meeting_delet(self):
        """모임글 삭제

        모임글 삭제 테스트입니다.
        """

        url = reverse(
            "meeting_detail", kwargs={"meeting_comment": self.meeting.comment}
        )
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer{self.access}",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, {"message": "삭제완료"})


class MeetingComment(MeetingBaseTestCase):
    """댓글 테스트

    댓글 조회, 생성, 수정, 삭제를 테스트합니다.
    """

    def test_comment_list(self):
        """댓글 조회

        댓글 조회 테스트입니다.
        """
        url = (
            reverse("meeting_comment", kwargs={"meeting_comment": self.meeting.comment})
            + "?page=1"
        )
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)

        """댓글 생성
        
        댓글 생성 테스트입니다.
        """
        ur1 = reverse(
            "meeting_comment", kwargs={"meeting_comment": self.meeting.comment}
        )
        data = self.meeting_create_data
        response = self.client.post(
            path=ur1,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
            data=data,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"message": "작성완료"})

    def test_comment_edit(self):
        """댓글 수정

        댓글 수정 테스트입니다.
        """

        ur1 = reverse(
            "meeting_comment_detail_view", kwargs={"meeting_comment": self.meeting}
        )
        data = self.meeting_edit_data
        response = self.client.put(
            path=ur1,
            HTTO_AUTHORIZATION=f"Bearer {self.access}",
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "수정완료"})

    def test_comment_delete(self):
        """댓글 삭제


        댓글 삭제 테스트입니다.
        """

        ur1 = reverse(
            "meeting_comment_detail_view",
            kwargs={"meeting_comment": self.meeting.comment},
        )
        response = self.client.delete(
            path=ur1,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertAlmostEqual(response.status_code, 204)
        self.assertEqual(response.data, {"message": "삭제완료"})


# Create your tests here.
