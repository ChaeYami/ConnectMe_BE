from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase

from .serializers import *
from user.models import User
from place.models import Place, PlaceComment

import random
import tempfile
from PIL import Image




def get_temporary_image(temp_file):
    '''
    임의 이미지 생성
    '''
    size = (10, 10)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file

class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser_data = {
            "account": "test",
            "email": "t@t.com",
            "password": "test",
            "phone": "01012345678",
        }
        cls.superuser = User.objects.create_superuser(**cls.superuser_data)
        cls.user_data1 = {
            "account": "basicuser",
            "email": "basicuser@test.com",
            "password": "test1234!!",
            "phone": "01012345670",
        }
        cls.user1 = User.objects.create_user(**cls.user_data1)
        cls.place_data = {
            "content": "test content",
            "sort": "test_sort",
            "address": "test_address",
            "score": "2.2",
            "price": "test_price",
            "hour": "test_hour",
            "holiday": "test_holiday",
        }
        cls.category_data = ["카페", "식사", "주점"]
        cls.place = []
        cls.comment = []
        cls.place_image_data = {
            "image":[],
        }
        for i in range(10):
            cls.place.append(
                Place.objects.create(title=f"test{i}", category=random.choice(cls.category_data), **cls.place_data, user=cls.superuser)
            )
        for i in range(3):
            cls.comment.append(
                PlaceComment.objects.create(content=f"comment{i}", place=cls.place[i], user=cls.user1)
            )
        for i in range(4):
            temp_file = tempfile.NamedTemporaryFile(suffix=".png")
            temp_file.name = f"image{i+1}.png"
            image_data = SimpleUploadedFile(temp_file.name, temp_file.read(), content_type="image/png")
            cls.place_image_data["image"].append(image_data)
        
        cls.superuser.is_active = True
        cls.superuser.save()
        cls.user1.is_active = True
        cls.user1.save()
    
    def setUp(self):
        self.super_user_access_token = self.client.post(reverse("login_view"), self.superuser_data).data.get("access")
        self.basic_user_access_token = self.client.post(reverse("login_view"), self.user_data1).data.get("access")

class PlaceViewTest(BaseTestCase):
    '''
    핫플레이스 북마크 모아보기, 작성하기
    
    - 북마크 모아보기 : 사용자의 핫플레이스 북마크 목록을 불러옵니다.
    - 작성 : is_staff 권한으로 접근합니다.
    - 게시글은 다중 이미지를 허용합니다.
    '''
    def test_bookmark_place_list(self):
        self.place[0].bookmark.add(self.user1)
        self.place[2].bookmark.add(self.user1)
        response = self.client.get(
            path=reverse("place_view"), 
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    def test_place_create(self):
        place_data = {
            **self.place_data,
            "title": "create test",
            "category":"식사",
            "image": self.place_image_data["image"],
        }
        response = self.client.post(
            path=reverse("place_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
            data=place_data,
            )
        self.assertEqual(response.status_code, 200)
        
    def test_fail_basic_user_create_place(self):
        place_data = {
            **self.place_data,
            "image": self.place_image_data["image"],
        }
        response = self.client.post(
            path=reverse("place_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=place_data, 
            )
        self.assertEqual(response.status_code, 403)
        
class PlaceDetailViewTest(BaseTestCase):
    '''
    핫플레이스 상세보기, 수정, 삭제, 북마크
    
    - 상세 열람 : 가입된 사용자는 핫플레이스를 열람할 수 있습니다.
    - 수정/삭제 : is_staff 권한으로 접근합니다.
    - 북마크 추가/취소 
    '''
    def test_the_one_place_deatil(self):
        response = self.client.get(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[0].id}), 
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
        
    def test_place_edit(self):
        self.place_data = {
            "title": "updated test Title2",
            "content": "updated test content",
            "category": "식사",
            "sort": "updated test_sort",
            "address": "updated test_address",
            "score": "0",
            "price": "updated test_price",
            "hour": "updated test_hour",
            "holiday": "updated test_holiday",
        }
        response = self.client.patch(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[1].id}),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
            data=self.place_data,
        )
        self.assertEqual(response.status_code, 200)
        
    def test_fail_basic_user_edit_place(self):
        self.place_data = {
            "title": "updated fail test Title3",
            "content": "updated fail test content",
            "category": "주점",
            "sort": "updated fail test_sort",
            "address": "updated fail test_address",
            "score": "1",
            "price": "updated fail test_price",
            "hour": "updated fail test_hour",
            "holiday": "updated fail test_holiday",
        }
        response = self.client.patch(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[1].id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=self.place_data,
        )
        self.assertEqual(response.status_code, 403)
        
        
    def test_place_delete(self):
        response = self.client.delete(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[2].id}),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    def test_fail_basic_user_delete_place(self):
        response = self.client.delete(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[2].id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
    
    
    def test_place_bookmark(self):
        response = self.client.post(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[3].id}), 
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    def test_place_cancel_bookmark(self):
        self.place[0].bookmark.add(self.user1)
        response = self.client.post(
            path=reverse("place_detail_view", kwargs={"place_id" : self.place[3].id}), 
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    
    
    
class PlaceLikeViewTest(BaseTestCase):
    '''
    핫플레이스 좋아요
    
    - 좋아요 추가/취소
    '''
    def test_add_like_place(self):
        response = self.client.post(
            path=reverse("place_like_view", kwargs={"place_id" : self.place[0].id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_remove_like_place(self):
        self.place[0].like.add(self.user1)
        response = self.client.post(
            path=reverse("place_like_view", kwargs={"place_id" : self.place[0].id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
        
class PlaceCommentViewTest(BaseTestCase):
    '''
    핫플레이스 게시글의 댓글 목록, 댓글 작성
    
    - 댓글 목록 : 게시글의 댓글 목록을 불러옵니다.
    - 댓글 작성 : 가입된 사용자는 댓글을 작성할 수 있습니다.
    '''
    def test_comment_list_in_place(self):
        response = self.client.get(
            path=reverse("place_comment_view", kwargs={"place_id": self.place[0].id}), 
            HTTP_AUTHORIZATION=f"Bearer {self.basic_user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    def test_comment_create(self):
        comment = {
            "content":"test_comment",
        }
        response = self.client.post(
            path=reverse("place_comment_view", kwargs={"place_id": self.place[0].id}), 
            HTTP_AUTHORIZATION=f"Bearer {self.basic_user_access_token}",
            data=comment,
        )
        self.assertEqual(response.status_code, 200)
        
class PlaceCommentDetailViewTest(BaseTestCase):
    '''
    핫플레이스 단일댓글 열람, 답글 작성, 댓글 수정, 삭제
    
    - 단일댓글 열람 : 가입된 사용자는 단일 댓글을 열람할 수 있습니다.
    - 답글 작성 : 1. 가입된 사용자는 답글을 작성할 수 있습니다. 2. 답글은 한 번만 작성할 수 있습니다.
    - 댓글 수정 : 작성자는 댓글을 수정할 수 있습니다.
    - 댓글 삭제 : 작성자는 댓글을 삭제할 수 있습니다.
    - 단, 답글이 남아있는 댓글을 내용을 삭제하고 댓글은 남아있게 됩니다.
    '''
    def test_the_one_comment_in_place(self):
        place_id = self.place[0].id
        comment_id = self.comment[0].id
        response = self.client.get(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_reply_create(self):
        place_id = self.place[0].id
        comment_id = self.comment[0].id
        user_id = self.user1.id
        reply_data = {
            "content":"create_comment",
            "place_id":place_id, 
            "user_id":user_id,
        }
        response = self.client.post(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=reply_data,
            )
        self.assertEqual(response.status_code, 200)
        
    def test_fail_double_reply_create(self):
        place_id = self.place[0].id
        comment_id = self.comment[0].id
        user_id = self.user1.id
        reply_data = {
            "content":"create_comment",
            "place_id":place_id, 
            "user_id":user_id,
        }
        response = self.client.post(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=reply_data,
            )
        
        comment_id = response.json()["id"]

        second_reply_data = {
            "content": "create_second_comment",
            "place_id": place_id,
            "user_id": user_id,
        }
        response = self.client.post(
            path=reverse("place_comment_detail_view", kwargs={"place_id": place_id, "place_comment_id": comment_id}),
            HTTP_AUTHORIZATION=f"Bearer {self.basic_user_access_token}",
            data=second_reply_data,
        )
        self.assertEqual(response.status_code, 403)
    
    def test_edit_comment(self):
        place_id = self.place[0].id
        comment_id = self.comment[0].id
        comment_data = {
            "content":"test_edit_comment",
        }
        response = self.client.put(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=comment_data,
            )
        self.assertEqual(response.status_code, 200)    
    
    def test_delete_comment(self):
        place_id = self.place[0].id
        comment_id = self.comment[0].id
        response = self.client.delete(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_delete_when_exist_comment(self):
        place_id = self.place[0].id
        comment_id = self.comment[0].id
        user_id = self.user1.id
        reply_data = {
            "content":"test_reply_delete_when_exist_comment",
            "place_id":place_id, 
            "user_id":user_id,
        }
        response = self.client.post(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=reply_data,
            )
        
        response = self.client.delete(
            path=reverse("place_comment_detail_view", kwargs={"place_id" : place_id, "place_comment_id":comment_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    
class PlaceImageViewTest(BaseTestCase):
    '''
    핫플레이스 이미지 추가, 삭제
    
    - 이미지 추가 : is_staff 권한으로 다중이미지 추가 가능합니다.
    - 이미지 삭제 : is_staff 권한으로 삭제가 가능합니다.
    '''
    def test_add_images(self):
        place_id = self.place[0].id
        response = self.client.post(
            path=reverse("place_image_view", kwargs={"place_id" : place_id, "place_image_id":1}),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
            data=self.place_image_data,
            )
        self.assertEqual(response.status_code, 200)
        
    def test_fail_basic_user_add_images(self):
        place_id = self.place[0].id
        response = self.client.post(
            path=reverse("place_image_view", kwargs={"place_id" : place_id, "place_image_id":1}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data=self.place_image_data,
            )
        self.assertEqual(response.status_code, 403)
        
    def test_delete_images(self):
        place_id = self.place[0].id
        response = self.client.post(
            path=reverse("place_image_view", kwargs={"place_id" : place_id, "place_image_id":1}),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
            data=self.place_image_data,
            )
        
        place_image_id = response.data[0]["id"]
        response = self.client.delete(
            path=reverse("place_image_view", kwargs={"place_id" : place_id, "place_image_id":place_image_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_fail_basic_user_delete_images(self):
        place_id = self.place[0].id
        response = self.client.post(
            path=reverse("place_image_view", kwargs={"place_id" : place_id, "place_image_id":1}),
            HTTP_AUTHORIZATION = f"Bearer {self.super_user_access_token}",
            data=self.place_image_data,
            )
        
        place_image_id = response.data[0]["id"]
        response = self.client.delete(
            path=reverse("place_image_view", kwargs={"place_id" : place_id, "place_image_id":place_image_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 403)
        

class PlaceCategoryViewTest(BaseTestCase):
    '''
    핫플레이스 카테고리 정렬

    -카테고리 : 기본, 식사, 주점, 카페
    '''
    def test_basic_category(self):
        response = self.client.get(
            path=reverse("place_category_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_meal_category(self):
        search_query = "식사"
        response = self.client.get(
            path=reverse("place_category_view") + f"?search={search_query}",
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_cafe_category(self):
        search_query = "카페"
        response = self.client.get(
            path=reverse("place_category_view") + f"?search={search_query}",
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)
        
    def test_drink_category(self):
        search_query = "주점"
        response = self.client.get(
            path=reverse("place_category_view") + f"?search={search_query}",
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            )
        self.assertEqual(response.status_code, 200)


class PlaceSearchViewTest(BaseTestCase):
    '''
    핫플레이스 검색
    
    -검색 : 제목으로 검색
    '''
    def test_place_search(self):
        search_query = "test7"
        response = self.client.get(
            path=reverse("place_search_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.basic_user_access_token}",
            data={"search": search_query},
            )
        self.assertEqual(response.status_code, 200)
