from django.urls import path, include
from .views import RegisterView, LoginView, \
    ReferralDashboardView, UserProfileView, \
    AskedQuestionsView, MostViewsQuestionsView, \
    QuestionCreateView, UpvoteQuestionView, DownvoteQuestionView, MostVotedQuestionsView, \
    NewQuestionsView, UserQuestionsAnswersListView, \
    FilterQuestionsView, AnswerListCreateView, QuestionDetailView, MostAnsweredQuestionsView, \
    UserCountView, UpdateProfileView, PollCreateView, PollDetailView, UserPollsListView, \
    RecentPollsView, MostViewedPollsView, MostPolledPollsView, UpvotePostView, FilterQuestionsByCompanyView, \
    FilterQuestionsBySectorView, AnswerDetailView, \
    FilterPollsView, PollChoiceUpdateView, CommunitiesView, CompaniesView, CompanyProfileView, \
    IndustriesSectorsView, SearchBarView, CommentAPIView, UserAnswersListView, TopCompaniesView, TagsByTrendingView, \
    TotalAnswersView, TotalQuestionsView, CompanyFilterbySectorView, fetch_data, DisplayData, PasswordResetRequestView, \
    PasswordResetConfirmView
from .views import GroupView, ManageGroupView, GroupPostsCreateAndListView, LogoutView, NotificationListView, \
    UserQuestionsListView, TagListView, CompanyProfileByNameView
from myproject.urls import schema_view
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('refer/', ReferralDashboardView.as_view(), name='refer'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('groups/', GroupView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupView.as_view(), name='group-detail'),
    path('managegroup/<int:group_id>/', ManageGroupView.as_view(), name='managegroup'),
    path('groups-home/<int:group_id>/posts/', GroupPostsCreateAndListView.as_view(), name='group-posts'),
    path('posts/<int:post_id>/upvote/', UpvotePostView.as_view(), name='upvote_post'),
    path('posts/<int:post_id>/comments/', CommentAPIView.as_view(), name='comment-list-create'),
    path('comments/<int:comment_id>/', CommentAPIView.as_view(), name='comment-delete'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-count/', UserCountView.as_view(), name='user-count'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    path('ask_a_question/', QuestionCreateView.as_view(), name='ask_a_question'),
    path('answer_a_question/<int:question_id>/', AnswerListCreateView.as_view(), name='answer-create'),
    path('question/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('user/<int:user_id>/questions_answers/', UserQuestionsAnswersListView.as_view(),
         name='user_questions_answers'),
    path('asked_questions/', UserQuestionsListView.as_view(), name='asked_questions'),
    path('asked_answers/', UserAnswersListView.as_view(), name='user-answers'),
    path('new_questions/', NewQuestionsView.as_view(), name='new_questions'),
    path('most_answered_questions/', MostAnsweredQuestionsView.as_view(), name='most_answered_questions'),
    # top 10 companies
    path('most_visited_Questions/', MostViewsQuestionsView.as_view(), name='most_visited_Questions'),
    path('best_answers/', MostAnsweredQuestionsView.as_view(), name='best_answers'),
    path('upvote_question/<int:question_id>/', UpvoteQuestionView.as_view(), name='upvote_question'),
    path('downvote_question/<int:question_id>/', DownvoteQuestionView.as_view(), name='downvote_question'),
    path('most_voted_question/', MostVotedQuestionsView.as_view(), name='most_voted_questions'),
    path('filter_questions_view/', FilterQuestionsView.as_view(), name='filter-questions'),
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    path('polls/create/', PollCreateView.as_view(), name='create_poll'),
    path('polls/<int:id>/', PollDetailView.as_view(), name='view_poll'),
    path('polls/<int:poll_id>/vote/', PollChoiceUpdateView.as_view(), name='poll_vote'),
    path('polls_by_user/', UserPollsListView.as_view(), name='user_polls'),
    path('recent_polls_view/', RecentPollsView.as_view(), name='recent_polls'),
    path('most_viewed_polls_view/', MostViewedPollsView.as_view(), name='most_viewed_polls'),
    path('most_polled_polls/', MostPolledPollsView.as_view(), name='most_polled_polls'),
    path('filter_polls_view/', FilterPollsView.as_view(), name='filter_polls'),
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    path('communities/', CommunitiesView.as_view(), name='communities'),
    path('companies/', CompaniesView.as_view(), name='companies'),
    path('company_profile_view/<int:id>/', CompanyProfileView.as_view(), name='company_profile_view'),
    path('company_by_sector/<str:sector>/', CompanyFilterbySectorView.as_view(), name='company_by_sector_view'),
    path('industries_sectors/', IndustriesSectorsView.as_view(), name='industries_sectors'),
    path('search_bar/', SearchBarView.as_view(), name='search_bar'),  #add company profile search
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('trending_tags/', TagsByTrendingView.as_view(), name='tags-by-trending'),
    path('total_questions/', TotalQuestionsView.as_view(), name='total_questions'),
    path('total_answers/', TotalAnswersView.as_view(), name='total_answers'),
    path('company_profile/<str:name>/', CompanyProfileByNameView.as_view(), name='company_profile_view'),
    path('filter_by_sector/<str:sector_name>/', FilterQuestionsBySectorView.as_view(), name='filter_by_sector'),
    path('filter_by_company/<str:company_name>/', FilterQuestionsByCompanyView.as_view(), name='filter_by_company'),
    path('answer/<int:id>/', AnswerDetailView.as_view(), name='answer-detail'),
    path('top-companies/', TopCompaniesView.as_view(), name='top-companies'),
    path('answer_an_answer/<int:answer_id>/', AnswerListCreateView.as_view(), name='answer-answer-create'),
    path('fetch-data/<str:ticker>/', fetch_data, name='fetch_data'),
    path('display-data/<str:ticker>/', DisplayData.as_view(), name='display-data'),

]
