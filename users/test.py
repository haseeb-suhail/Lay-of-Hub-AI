from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Question, Answer, Company, Sector, Community, Notification, Tag, User_Model

class QuestionCreateTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_question(self):
        url = reverse('ask_a_question')
        data = {
            "title": "How to implement WebRTC in Django?",
            "caption": "I need help with WebRTC in Django.",
            "community": "Developers",
            "is_anonymous": False,
            "company_ids": [],
            "sector_ids": [],
            "tag_names": ["WebRTC", "Django"]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Question.objects.get().title, "How to implement WebRTC in Django?")

class AnswerCreateTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)

    def test_create_answer(self):
        url = reverse('answer-create', args=[self.question.id])
        data = {
            "content": "This is an answer.",
            "is_anonymous": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.question.answers.count(), 1)
        self.assertEqual(self.question.answers.first().content, "This is an answer.")

class QuestionDetailTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)

    def test_get_question_detail(self):
        url = reverse('question-detail', args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Question 1")

class UserQuestionsAnswersTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.answer = self.question.answers.create(content="This is an answer.", user=self.user)

    def test_get_user_questions_answers(self):
        url = reverse('user_questions_answers', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(len(response.data['answers']), 1)

class UserAskedQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)

    def test_get_user_asked_questions(self):
        url = reverse('asked_questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")

class UserAskedAnswersTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.answer = self.question.answers.create(content="This is an answer.", user=self.user)

    def test_get_user_asked_answers(self):
        url = reverse('user-answers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "This is an answer.")

class NewQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)

    def test_get_new_questions(self):
        url = reverse('new_questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")

class MostAnsweredQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.answer = self.question.answers.create(content="This is an answer.", user=self.user)

    def test_get_most_answered_questions(self):
        url = reverse('most_answered_questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")


class MostViewedQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user, view_count=10)

    def test_get_most_viewed_questions(self):
        url = reverse('most_visited_Questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")

class UpvoteQuestionTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)

    def test_upvote_question(self):
        url = reverse('upvote_question', args=[self.question.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(self.question.votes, 1)

class DownvoteQuestionTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user, votes=1)

    def test_downvote_question(self):
        url = reverse('downvote_question', args=[self.question.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(self.question.votes, 0)

class MostVotedQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user, votes=10)

    def test_get_most_voted_questions(self):
        url = reverse('most_voted_questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")

class FilterQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.company1 = Company.objects.create(name="10x Genomics Inc.", symbol="TXG")
        self.sector1 = Sector.objects.create(sub_sector="Agricultural Inputs", industry="Agriculture", sector="Farming")
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.question.companies.add(self.company1)
        self.question.sectors.add(self.sector1)

    def test_filter_questions(self):
        url = reverse('filter-questions')
        data = {
            "companies": [self.company1.id],
            "sectors": [self.sector1.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(response.data['questions'][0]['title'], "Question 1")

class CommunitiesTests(APITestCase):
    def setUp(self):
        self.community = Community.objects.create(name="Developers")

    def test_get_communities(self):
        url = reverse('communities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Developers")

class CompaniesTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="10x Genomics Inc.", symbol="TXG")

    def test_get_companies(self):
        url = reverse('companies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "10x Genomics Inc.")

class CompanyProfileViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="10x Genomics Inc.", symbol="TXG")
        self.client = APIClient()

    def test_get_company_profile(self):
        url = reverse('company_profile_view', args=[self.company.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "10x Genomics Inc.")

class IndustriesSectorsTests(APITestCase):
    def setUp(self):
        self.sector = Sector.objects.create(sub_sector="Agricultural Inputs", industry="Agriculture", sector="Farming")

    def test_get_industries_sectors(self):
        url = reverse('industries_sectors')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sector'], "Farming")

class SearchBarTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.company = Company.objects.create(name="10x Genomics Inc.", symbol="TXG")
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.question.companies.add(self.company)

    def test_search_bar(self):
        url = reverse('search_bar')
        response = self.client.get(url, {'keyword': 'Genomics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(response.data['questions'][0]['title'], "Question 1")

class NotificationsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        Notification.objects.create(user=self.user, message="You have a new notification.")

    def test_get_notifications(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], "You have a new notification.")

class TagsTests(APITestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="WebRTC")

    def test_get_tags(self):
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "WebRTC")

class TrendingTagsTests(APITestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="WebRTC")

    def test_get_trending_tags(self):
        url = reverse('tags-by-trending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "WebRTC")

class TotalQuestionsTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)

    def test_get_total_questions(self):
        url = reverse('total_questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_questions'], 1)

class TotalAnswersTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.answer = self.question.answers.create(content="This is an answer.", user=self.user)

    def test_get_total_answers(self):
        url = reverse('total_answers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_answers'], 1)

class CompanyProfileViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="10x Genomics Inc.",
            symbol="TXG",
            name_on_website="10x Genomics",
            public_or_private="Public",
            industry="Health Information Services",
            industry_clean="Health Care/Life Sciencies",
            sector="Healthcare Provision",
            clean_name="10xGenomics",
            website_url="www.layoffhub.ai/10xGenomics"
        )
        self.client = APIClient()

    def test_get_company_profile(self):
        url = reverse('company_profile_view', args=[self.company.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "10x Genomics Inc.")



class FilterQuestionsBySectorTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.sector = Sector.objects.create(sub_sector="Agricultural Inputs", industry="Agriculture", sector="Farming")
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.question.sectors.add(self.sector)

    def test_filter_by_sector(self):
        url = reverse('filter_by_sector', args=["Farming"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")

class FilterQuestionsByCompanyTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.company = Company.objects.create(name="10x Genomics Inc.", symbol="TXG")
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.question.companies.add(self.company)

    def test_filter_by_company(self):
        url = reverse('filter_by_company', args=["10x Genomics"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Question 1")

class AnswerDetailTests(APITestCase):
    def setUp(self):
        self.user = User_Model.objects.create_user(username='testuser', password='testpass')
        self.question = Question.objects.create(title="Question 1", caption="Caption 1", author=self.user)
        self.answer = self.question.answers.create(content="This is an answer.", user=self.user)

    def test_get_answer_by_id(self):
        url = reverse('answer-detail', args=[self.answer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "This is an answer.")

