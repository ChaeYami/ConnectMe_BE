# chat/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
