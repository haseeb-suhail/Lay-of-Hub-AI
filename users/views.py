import os
from datetime import datetime
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlunquote, urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.generics import ListAPIView
from tabulate import tabulate
from .config import num_months_timeframes, stocks_folder_path, ciks_file_path, \
    start_date, headers
from .helpers import process_form4s, get_CIK
from .sec_api import save_form4s_to_csv, get_filing_metadata
from .serializers import UpdateProfileSerializer, \
    CommentSerializer, QuestionSerializer, PollChoiceSerializer, CompanySerializer, PollSerializer, AnswerSerializer, \
    NotificationSerializer, GroupSerializer, PostSerializer, CommentSerializer, \
    UserProfileSerializer, PasswordResetRequestSerializer, PasswordResetSerializer
from .models import Question, Poll, Answer, Community, Comment, Notification, User_Model, Upvote, Downvote
from django.db.models import Count, F
from django.http import Http404
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer, ReferralSerializer, TagSerializer
from django.contrib.auth import get_user_model, update_session_auth_hash
from .models import Referral
from rest_framework.parsers import MultiPartParser, FormParser
from django.urls import reverse
from .models import Group, Post
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.generics import UpdateAPIView
from django.contrib.auth.models import User
from django.http import JsonResponse

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User_Model.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# views.py

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            'username': user.username,
            # 'profile_image': user.profile_image,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'refresh': str(refresh),
            'access': str(access),
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(User_Model, email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"https://layoffhub.ai/forgot-password?uid={uid}&token={token}"

            try:
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link to reset your password: {reset_url}",
                    from_email='support@layoffhub.ai',
                    recipient_list=[email],
                )
                return Response({'message': 'Password reset link sent.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User_Model.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User_Model.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)


class ReferralDashboardView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReferralSerializer

    def get(self, request, *args, **kwargs):

        user = request.user
        referral_code = user.referral_code  # Get the user's referral code
        referral_url = f'{referral_code}'

        return Response({
            'referral_url': referral_url,
            'referral_points': user.referral_points,
            'total_points_awarded': user.total_points_awarded,
            'referrals': ReferralSerializer(user.given_referrals.all(), many=True).data
        }, status=status.HTTP_200_OK)



#for profile
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        print("Serialized Data:", serializer.data)  # Debugging print
        return Response({
            'user': serializer.data,
            'badge': user.badge
        }, status=status.HTTP_200_OK)


class UpdateProfileView(UpdateAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save()
        if 'new_password' in self.request.data:
            update_session_auth_hash(self.request, user)  # Keep the user logged in


#drop down button views

#for groups
class GroupView(generics.GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        # Allow anyone to view groups (GET), but require authentication for posting (POST)
        if self.request.method == 'POST' and 'PUT' and 'DELETE':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            group = self.get_object()
            serializer = self.get_serializer(group)
            return Response(serializer.data)
        else:
            groups = self.get_queryset()
            serializer = self.get_serializer(groups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(created_by=self.request.user)
            group.admins.add(self.request.user)
            group.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        pk = self.kwargs.get('pk')
        return generics.get_object_or_404(Group, pk=pk)


class IsGroupMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        group = obj.group
        user = request.user

        # Check if the user is a member, moderator, or admin
        return user in group.admins.all() or \
            user in group.moderators.all() or \
            user in group.members.all()


class ManageGroupView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsGroupMemberOrAdmin]
    serializer_class = GroupSerializer

    def post(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        action = request.data.get('action')
        user_identifier = request.data.get('user_identifier')

        group = get_object_or_404(Group, id=group_id)

        try:
            if '@' in user_identifier:
                user = User.objects.get(email=user_identifier)
            else:
                user = User.objects.get(username=user_identifier)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not (request.user in group.admins.all() or
                request.user in group.moderators.all() or
                request.user in group.members.all()):
            return Response({'error': 'You do not have permission to manage this group'},
                            status=status.HTTP_403_FORBIDDEN)

        if action == 'add_member':
            group.members.add(user)
            message = f"You have been added as a member of the group '{group.name}' by {request.user.username}."
        elif action == 'remove_member':
            group.members.remove(user)
            message = f"You have been removed from the group '{group.name}' by {request.user.username}."
        elif action == 'make_admin':
            group.admins.add(user)
            group.moderators.remove(user)
            message = f"You have been made an admin of the group '{group.name}' by {request.user.username}."
        elif action == 'make_moderator':
            group.moderators.add(user)
            message = f"You have been made a moderator of the group '{group.name}' by {request.user.username}."
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the notification
        Notification.objects.create(user=user, message=message)

        return Response({'status': 'Action completed successfully'}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)

        if not (request.user in group.admins.all() or request.user in group.moderators.all()):
            return Response({'error': 'You do not have permission to update this group'},
                            status=status.HTTP_403_FORBIDDEN)

        previous_name = group.name
        previous_description = group.description

        serializer = self.get_serializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Check if name or description has changed
            new_name = group.name
            new_description = group.description

            if previous_name != new_name or previous_description != new_description:
                for member in group.members.all():
                    message = f"The group '{previous_name}' has been updated by {request.user.username}."
                    if previous_name != new_name:
                        message += f"\n- Name changed from '{previous_name}' to '{new_name}'."
                    if previous_description != new_description:
                        message += f"\n- Description changed from '{previous_description}' to '{new_description}'."

                    # Create the notification for each member
                    Notification.objects.create(user=member, message=message)

            return Response({'status': 'Group updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsGroupMemberOrAdmin]
    serializer_class = GroupSerializer

    def get_object(self):
        group_id = self.kwargs.get('group_id')
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise Http404

        # Check if the requesting user is an admin, moderator, or member of the group
        if self.request.user not in group.admins.all() and \
                self.request.user not in group.moderators.all() and \
                self.request.user not in group.members.all():
            self.permission_denied(self.request)

        return group

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        admins = group.admins.all()
        moderators = group.moderators.all()
        members = group.members.all()

        response_data = {
            'name': group.name,
            'description': group.description,
            'admins': UserSerializer(admins, many=True).data,
            'moderators': UserSerializer(moderators, many=True).data,
            'members': UserSerializer(members, many=True).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GroupPostsCreateAndListView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMemberOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)

        if not (self.request.user in group.admins.all() or
                self.request.user in group.moderators.all() or
                self.request.user in group.members.all()):
            raise PermissionDenied("You do not have access to this group.")

        return group.posts.all()

    def perform_create(self, serializer):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)

        if not (self.request.user in group.admins.all() or
                self.request.user in group.moderators.all() or
                self.request.user in group.members.all()):
            raise PermissionDenied("You do not have permission to add posts to this group.")

        post = serializer.save(author=self.request.user, group=group, approved=True)
        message = f"A new post '{post.heading}' has been created in your group '{group.name}'."

        # Notify all members, admins, and moderators
        all_recipients = group.members.all() | group.admins.all() | group.moderators.all()
        for member in all_recipients:
            Notification.objects.create(user=member, message=message)

        return Response({'status': 'Post created successfully'}, status=status.HTTP_201_CREATED)


class UpvotePostView(APIView):
    def post(self, request, post_id):
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        # Add upvote
        result = post.add_upvote(user)
        message = f"Your post '{post.heading}' has been upvoted by {user.username}!"
        Notification.objects.create(user=post.author, message=message)

        if result == "You have already upvoted this post.":
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": result}, status=status.HTTP_200_OK)


class CommentAPIView(APIView):

    def get_permissions(self):
        # Allow anyone to view groups (GET), but require authentication for posting (POST)
        if self.request.method == 'POST' and 'DELETE':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            message = f"Your post '{post.heading}' has a new comment by {request.user.username}!"
            Notification.objects.create(user=post.author, message=message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        if request.user != comment.author and request.user != comment.post.author:
            raise PermissionDenied("You do not have permission to delete this comment.")

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

        # Notify post author
        # Notification.objects.create(user=comment.post.author, message=f"New comment on your post by {self.request.user}")


class UserCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user_count = User.objects.count()
        return Response({
            'total_users': user_count
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Debugging line to print the refresh token
            print(f"Received refresh token: {refresh_token}")

            # Blacklist the token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # This will blacklist the token
            except TokenError:
                return Response({"detail": "Token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionCreateView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Save the question with or without author based on is_anonymous field
        author = self.request.user if not serializer.validated_data.get('is_anonymous') else None
        serializer.save(author=author)


class AnswerListCreateView(generics.ListCreateAPIView):
    serializer_class = AnswerSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        parent_answer_id = self.kwargs.get('answer_id', None)
        if parent_answer_id:
            return Answer.objects.filter(parent_answer_id=parent_answer_id)
        else:
            question_id = self.kwargs.get('question_id')
            return Answer.objects.filter(question_id=question_id, parent_answer__isnull=True)

    def perform_create(self, serializer):
        parent_answer_id = self.kwargs.get('answer_id', None)
        parent_answer = None
        question = None

        if parent_answer_id:
            parent_answer = Answer.objects.get(id=parent_answer_id)
            question = parent_answer.question
        else:
            question_id = self.kwargs.get('question_id')
            question = Question.objects.get(id=question_id)

        serializer.save(user=self.request.user, question=question, parent_answer=parent_answer)

        # Notify the original answer's author if it's an answer to an answer
        if parent_answer and parent_answer.user:
            message = f"Your answer has a new response by {self.request.user.username}!"
            Notification.objects.create(user=parent_answer.user, message=message)


class QuestionDetailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
            question.view_count += 1
            question.save()
            serializer = QuestionSerializer(question, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)


class UserQuestionsListView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get_queryset(self):
        # Return all questions, regardless of the user
        return Question.objects.all().prefetch_related('answers', 'companies', 'sectors', 'tags')


class UserAnswersListView(generics.ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get_queryset(self):
        # Return all answers, regardless of the user
        return Answer.objects.all().prefetch_related('user')


class UserQuestionsAnswersListView(generics.ListAPIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Handle the case where the user does not exist
            return Question.objects.none()

        # Return questions authored by the specified user
        return Question.objects.filter(author=user).prefetch_related('answers', 'companies', 'sectors', 'tags')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        question_serializer = QuestionSerializer(queryset, many=True)

        user_id = self.kwargs['user_id']
        # Fetch answers for the specified user_id, regardless of whether the request user is authenticated
        answers = Answer.objects.filter(user_id=user_id).prefetch_related('user')
        answer_serializer = AnswerSerializer(answers, many=True)

        return Response({
            'questions': question_serializer.data,
            'answers': answer_serializer.data
        })


class AskedQuestionsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Question.objects.all().prefetch_related('answers', 'companies', 'sectors', 'tags')
    serializer_class = QuestionSerializer


class NewQuestionsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Question.objects.all().order_by('-date_posted')
    serializer_class = QuestionSerializer


class MostAnsweredQuestionsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.annotate(answer_count=Count('answers')).order_by('-answer_count')


class MostViewsQuestionsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.order_by('-view_count')


class UpvoteQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id, *args, **kwargs):
        user = request.user

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already upvoted this question
        if Upvote.objects.filter(user=user, question=question).exists():
            return Response({'error': 'You have already upvoted this question'}, status=status.HTTP_400_BAD_REQUEST)

        # Create an upvote
        Upvote.objects.create(user=user, question=question)

        # Update the vote count
        question.votes += 1
        question.save()

        # Create a notification for the question author
        message = f"Your question '{question.title}' has been upvoted by {user.username}!"
        Notification.objects.create(user=question.author, message=message)

        return Response({'status': 'upvoted'}, status=status.HTTP_200_OK)


class DownvoteQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id, *args, **kwargs):
        user = request.user

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already downvoted this question
        if Downvote.objects.filter(user=user, question=question).exists():
            return Response({'error': 'You have already downvoted this question'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a downvote
        Downvote.objects.create(user=user, question=question)

        # Update the vote count
        question.votes -= 1
        question.save()

        # Create a notification for the question author
        message = f"Your question '{question.title}' has been downvoted by {user.username}!"
        Notification.objects.create(user=question.author, message=message)

        return Response({'status': 'downvoted'}, status=status.HTTP_200_OK)


class MostVotedQuestionsView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.order_by('-votes')


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Question, Company, Sector, Tag
from .serializers import QuestionSerializer


class FilterQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company_ids = request.data.get('companies', [])
        sector_ids = request.data.get('sectors', [])
        tag_names = request.data.get('tags', [])
        community = request.data.get('community', None)
        username = request.data.get('username', None)

        query = Q()

        if company_ids:
            query &= Q(companies__id__in=company_ids)

        if sector_ids:
            query &= Q(sectors__id__in=sector_ids)

        if tag_names:
            query &= Q(tags__name__in=tag_names)

        if community:
            query &= Q(community=community)

        if username:
            query &= Q(author__username=username)

        questions = Question.objects.filter(query).distinct()

        question_serializer = QuestionSerializer(questions, many=True)

        results = {
            'questions': question_serializer.data,
        }

        return Response(results, status=status.HTTP_200_OK)


'''USAGE 
{
    "companies": [1, 2],
    "sectors": [1],
    "tags": ["tag1", "tag2"],
    "community": "CommunityName",
    "username": "AuthorUsername"
}
'''

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView


class PollCreateView(CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.data.get('is_anonymous') == 'true':
            serializer.save()
        else:
            serializer.save(author=self.request.user)


class PollChoiceUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)
        serializer = PollChoiceSerializer(data=request.data)
        if serializer.is_valid():
            poll.update_poll_choice(serializer.validated_data['choice'])
            message = f"User '{request.user.username}' has made a choice in your poll '{poll.title}'."
            Notification.objects.create(user=poll.author, message=message)
            return Response({"detail": "Poll choice updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        poll = self.get_object()
        poll.increment_view_count()
        serializer = self.get_serializer(poll)
        return Response(serializer.data)


class UserPollsListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PollSerializer

    def get_queryset(self):
        user = self.request.user
        return Poll.objects.filter(author=user)


class RecentPollsView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Poll.objects.all().order_by('-date_posted')
    serializer_class = PollSerializer


class MostViewedPollsView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Poll.objects.all().order_by('-view_count')
    serializer_class = PollSerializer


class MostPolledPollsView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PollSerializer

    def get_queryset(self):
        return Poll.objects.annotate(
            total_votes=F('choice1_votes') + F('choice2_votes') + F('choice3_votes')
        ).order_by('-total_votes')


class FilterPollsView(APIView):
    def post(self, request):
        company_ids = request.data.get('companies', [])
        sector_ids = request.data.get('sectors', [])
        community = request.data.get('community', '')
        username = request.data.get('username', '')

        query = Q()

        if company_ids:
            query |= Q(companies__id__in=company_ids)

        if sector_ids:
            query |= Q(sectors__id__in=sector_ids)

        if community:
            query |= Q(community=community)

        if username:
            query |= Q(author__username=username)

        polls = Poll.objects.filter(query).distinct()

        serializer = PollSerializer(polls, many=True)

        results = {
            'polls': serializer.data,
        }

        return Response(results, status=status.HTTP_200_OK)


from .serializers import CommunitySerializer, CompanySerializer, SectorSerializer, PollSerializer, QuestionSerializer, \
    AnswerSerializer, UserSerializer


class CommunitiesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer


class CompaniesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyFilterbySectorView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySerializer

    def get_queryset(self):
        # Replace hyphens with slashes in the sector
        sector = self.kwargs.get('sector').replace('-', '/')
        return Company.objects.filter(sector__iexact=sector)  # Case-insensitive exact match

    def get(self, request, *args, **kwargs):
        companies = self.get_queryset()
        serializer = self.get_serializer(companies, many=True)  # Use many=True for multiple objects
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = 'id'


class IndustriesSectorsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer


class SearchBarView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        keyword = request.query_params.get('keyword', None)
        if not keyword:
            return Response({"detail": "Keyword is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Search in Questions
        questions = Question.objects.filter(
            Q(title__icontains=keyword) |
            Q(caption__icontains=keyword) |
            Q(companies__name__icontains=keyword) |
            Q(sectors__sub_sector__icontains=keyword) |
            Q(tags__name__icontains=keyword) |
            Q(community__icontains=keyword) |
            Q(author__username__icontains=keyword)
        ).distinct()

        # Search in Answers
        answers = Answer.objects.filter(content__icontains=keyword).distinct()

        # Search in Users
        users = User_Model.objects.filter(
            Q(username__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(first_name__icontains=keyword) |
            Q(last_name__icontains=keyword)
        ).distinct()

        # Search in Polls
        polls = Poll.objects.filter(
            Q(title__icontains=keyword) |
            Q(caption__icontains=keyword) |
            Q(choice1__icontains=keyword) |
            Q(choice2__icontains=keyword) |
            Q(choice3__icontains=keyword) |
            Q(companies__name__icontains=keyword) |
            Q(sectors__sub_sector__icontains=keyword) |
            Q(tags__name__icontains=keyword) |
            Q(community__icontains=keyword) |
            Q(author__username__icontains=keyword)
        ).distinct()

        question_serializer = QuestionSerializer(questions, many=True)
        answer_serializer = AnswerSerializer(answers, many=True)
        user_serializer = UserSerializer(users, many=True)
        poll_serializer = PollSerializer(polls, many=True)

        return Response({
            'questions': question_serializer.data,
            'answers': answer_serializer.data,
            'users': user_serializer.data,
            'polls': poll_serializer.data
        }, status=status.HTTP_200_OK)


#For notifications testing
class NotificationListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.all()


class TagListView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagsByTrendingView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Tag.objects.annotate(
        trending_score=Count('questions')
    ).order_by('-trending_score')
    serializer_class = TagSerializer


class TotalQuestionsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        total_questions = Question.objects.count()
        return Response({
            'total_questions': total_questions
        }, status=200)


class TotalAnswersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        total_answers = Answer.objects.count()
        return Response({
            'total_answers': total_answers
        }, status=200)  # Closing parenthesis was missing here.


class CompanyProfileByNameView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = 'name'

    def get(self, request, *args, **kwargs):
        name = self.kwargs.get("name")
        company = get_object_or_404(Company, name__iexact=name)  # Case-insensitive exact match

        serializer = self.get_serializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FilterQuestionsBySectorView(ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        sector_name = self.kwargs.get('sector_name')
        return Question.objects.filter(sectors__sector__icontains=sector_name)


# views.py
class FilterQuestionsByCompanyView(ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        company_name = self.kwargs.get('company_name')
        return Question.objects.filter(companies__name__icontains=company_name)


class AnswerDetailView(RetrieveAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class TopCompaniesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Annotate each company with the count of related questions and answers
        companies = Company.objects.annotate(
            question_count=Count('questions', distinct=True),
            answer_count=Count('questions__answers', distinct=True)
        ).order_by('-question_count', '-answer_count')

        # Serialize the results
        serializer = CompanySerializer(companies, many=True)

        return Response(serializer.data, status=200)


def fetch_data(request, ticker):
    # Get CIK
    cik = get_CIK(ticker=ticker, ciks_file_path=ciks_file_path, headers=headers)
    if not cik:
        print(f"CIK for ticker {ticker} not found. Please check the ticker and try again.")
        return

    print(f"CIK for ticker {ticker}: {cik}")

    # --------------------------------------------------------------------------------
    # Use CIK to get Form 4s metadata
    metadata = get_filing_metadata(cik)

    if not metadata or "filings" not in metadata or "recent" not in metadata["filings"]:
        print(f"Failed to retrieve filings metadata for CIK: {cik}")
        return

    all_forms = pd.DataFrame.from_dict(metadata["filings"]["recent"])
    form4s = all_forms[all_forms["form"] == "4"].copy()
    form4s["reportDate"] = pd.to_datetime(form4s['reportDate']).dt.date
    form4s = form4s[form4s["reportDate"] >= start_date]
    form4s["accessionNumber"] = form4s["accessionNumber"].str.replace("-", "")
    save_form4s_to_csv(ticker, form4s)

    # --------------------------------------------------------------------------------
    # Use Form 4s metadata to get Form 4s
    process_form4s(cik=cik, ticker=ticker)
    return JsonResponse({"message": "Data fetched and processed successfully for ticker: " + ticker})


class DisplayData(APIView):
    def get(self, request, ticker):
        ticker_file_path = f"{stocks_folder_path}/{ticker}.csv"
        form4s_file_path = f"{stocks_folder_path}/{ticker}_form4_details.csv"

        if not os.path.exists(ciks_file_path):
            return Response({"error": "CIK file not found!"}, status=status.HTTP_404_NOT_FOUND, content_type="application/json")

        if not os.path.exists(ticker_file_path):
            return Response({"error": "Ticker file not found!"}, status=status.HTTP_404_NOT_FOUND, content_type="application/json")

        if not os.path.exists(form4s_file_path):
            return Response({"error": "Form 4s file not found!"}, status=status.HTTP_404_NOT_FOUND, content_type="application/json")

        # Load CSV data
        ticker_df = pd.read_csv(ticker_file_path, dtype={"accessionNumber": str}, parse_dates=["reportDate"])
        ticker_df["reportDate"] = ticker_df["reportDate"].dt.date
        form4s_df = pd.read_csv(form4s_file_path)

        # Get filter parameter from request
        filter_type = request.GET.get('filter', 'all').lower()

        # Filter the data based on the filter_type
        if filter_type == 'sell':
            form4s_df = form4s_df[form4s_df['Transaction'].isin(['Sale', 'Automatic Sale'])]
        elif filter_type == 'buy':
            form4s_df = form4s_df[form4s_df['Transaction'].isin(['Purchase', 'Option Execute'])]

        response_data = []

        for num_months in num_months_timeframes:
            cutoff_date = (datetime.today() - relativedelta(months=num_months)).date()
            filtered_ticker_df = ticker_df[ticker_df["reportDate"] >= cutoff_date]

            accession_nos = filtered_ticker_df["accessionNumber"].tolist()
            form4s_df["accessionNumber"] = form4s_df["accessionNumber"].astype(str).str.zfill(18)
            filtered_form4s_df = form4s_df[form4s_df["accessionNumber"].isin(accession_nos)]

            # Replace NaN values with None (which translates to null in JSON)
            filtered_form4s_df = filtered_form4s_df.replace({np.nan: None})

            # Rename the keys as required
            renamed_filtered_form4s_df = filtered_form4s_df.rename(columns={
                "Last Date": "last_date",
                "Owner Type": "owner_type",
                "Shares Held": "shares_held",
                "Shares Traded": "shares_traded"
            })

            # Convert the filtered DataFrame to a list of dictionaries
            filtered_data = renamed_filtered_form4s_df.to_dict(orient="records")

            response_data.append({
                f"data_last_{num_months}_months": filtered_data
            })

        # Return the response as a JSON array
        return Response(response_data, status=status.HTTP_200_OK, content_type="application/json")
