#serializers.py
from django.contrib.auth.backends import BaseBackend
from .models import Referral, User_Model
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import Group, Post, Comment, Answer, Poll, Company, Sector, Tag, Community, Upvote, Notification
from django.utils.http import urlquote

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)  # Accepts both username and email
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError('Both username and password are required.')

        # Authenticate using the custom backend
        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid credentials.')

        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User_Model
        fields = ('username', 'first_name', 'last_name', 'password', 'confirm_password', 'email','agreement','referred_by_code')
        extra_kwargs = {
            'email': {'required': True, 'validators': [UniqueValidator(queryset=User.objects.all())]},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "The two password fields must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User_Model.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.referral_code = self.generate_unique_referral_code()
        user.save()

        # Handle referral points
        referred_by_code = self.context['request'].data.get('referred_by_code', None)
        if referred_by_code:
            try:
                referrer = User_Model.objects.get(referral_code=referred_by_code)
                # Award points to the referrer
                referral_points = 10  # Points awarded for referral
                referrer.add_points(referral_points, is_referral=True)

                # Create a referral record
                Referral.objects.create(referred_by=referrer, referred_to=user, points_awarded=referral_points)

                # Notify referrer about the new registration
                message = f"Your referral code was used for a new registration. You have been awarded {referral_points} points."
                Notification.objects.create(user=referrer, message=message)
            except User_Model.DoesNotExist:
                pass

        user.update_badges()
        return user

    def generate_unique_referral_code(self):
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not User.objects.filter(referral_code=code).exists():
                return code


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'email', 'profile_image',
                  'address',
                  'phone',
                  'country',
                  'state',
                  'zip_code')


class UpdateProfileSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    confirm_new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User_Model
        fields = [
            'id', 'profile_image', 'username', 'first_name', 'last_name', 'current_password', 'new_password',
            'confirm_new_password', 'address', 'phone', 'country', 'state', 'zip_code'
        ]
        read_only_fields = ['email']  # Email should be read-only

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if new_password and new_password != confirm_new_password:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})

        if new_password:
            try:
                validate_password(new_password)  # Validate new password based on Django settings
            except Exception as e:
                raise serializers.ValidationError({'new_password': str(e)})

        return data

    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('confirm_new_password', None)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.country = validated_data.get('country', instance.country)
        instance.state = validated_data.get('state', instance.state)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ('referred_by', 'referred_to', 'created_at')


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, User_Email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            if '@' in User_Email:
                user = UserModel.objects.get(email=User_Email)
            else:
                user = UserModel.objects.get(username=User_Email)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.CharField()  # Change to CharField for username

    def validate(self, data):
        email = data.get('email')
        if not User_Model.objects.filter(email=email).exists():
            raise serializers.ValidationError("User does not exist.")
        return data


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data



#for groups
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description')


class PostSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_blank=True)  # For URL input
    image_file = serializers.ImageField(required=False, allow_null=True)  # For file uploads

    class Meta:
        model = Post
        fields = ['author', 'author_username', 'heading', 'content', 'image', 'image_file', 'created_at', 'approved']
        read_only_fields = ['author', 'created_at']

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        image_url = data.get('image', None)
        image_file = data.get('image_file', None)

        if image_url and (image_url.startswith('http://') or image_url.startswith('https://')):
            # Handle image URL
            internal_data['image'] = image_url
            internal_data['image_file'] = None
        elif image_file:
            # Handle file upload
            internal_data['image'] = None
            internal_data['image_file'] = image_file
        else:
            # Handle the case where no image is provided
            internal_data['image'] = None
            internal_data['image_file'] = None

        return internal_data

    def create(self, validated_data):
        # No need to check for image URL or image file requirement here
        return super().create(validated_data)


class UpvoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upvote
        fields = ['post', 'user', 'post_author', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at')


# --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------
class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = '__all__'  # Or specify the exact fields you need
        extra_fields = ['question_count', 'answer_count']

    def get_field_names(self, declared_fields, info):
        # This method dynamically adds extra fields to the serializer's fields
        fields = super(CompanySerializer, self).get_field_names(declared_fields, info)
        if hasattr(self.Meta, 'extra_fields'):
            return fields + self.Meta.extra_fields
        return fields


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


from rest_framework import serializers
from .models import Question, Company, Sector, Tag, Community


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        fields = ['username', 'profile_image']


class AnswerSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    child_answers = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'user', 'content', 'date_posted', 'is_anonymous', 'parent_answer', 'child_answers']
        read_only_fields = ['user', 'date_posted', 'child_answers']

    def get_child_answers(self, obj):
        child_answers = obj.child_answers.all()
        return AnswerSerializer(child_answers, many=True).data


class QuestionSerializer(serializers.ModelSerializer):
    company_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    sector_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    tag_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    companies = CompanySerializer(many=True, read_only=True)
    sectors = SectorSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    user = UserDetailSerializer(read_only=True)
    author_username = serializers.SerializerMethodField()  # Field to include author username
    author_profile_image = serializers.SerializerMethodField()  # Field to include author profile image

    class Meta:
        model = Question
        fields = [
            'id', 'user', 'title', 'community', 'view_count', 'image', 'featured_image', 'caption', 'is_anonymous',
            'company_ids', 'sector_ids', 'tag_names', 'companies', 'sectors', 'tags', 'answers',
            'date_posted', 'author_username', 'author_profile_image', 'votes'
        ]
        read_only_fields = ['companies', 'sectors', 'tags', 'answers']

    def get_author_profile_image(self, obj):
        if obj.author and obj.author.profile_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(urlquote(obj.author.profile_image.url))
        return None

    def get_author_username(self, obj):
        return obj.author.username if obj.author else None

    def create(self, validated_data):
        company_ids = validated_data.pop('company_ids', [])
        sector_ids = validated_data.pop('sector_ids', [])
        tag_names = validated_data.pop('tag_names', [])

        question = Question.objects.create(**validated_data)

        for company_id in company_ids:
            try:
                company = Company.objects.get(id=company_id)
                question.companies.add(company)
            except Company.DoesNotExist:
                pass

        for sector_id in sector_ids:
            try:
                sector = Sector.objects.get(id=sector_id)
                question.sectors.add(sector)
            except Sector.DoesNotExist:
                pass

        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)

        return question


class QuestionVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'votes']


class PollSerializer(serializers.ModelSerializer):
    company_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    sector_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    companies = CompanySerializer(many=True, read_only=True)
    sectors = SectorSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'community', 'view_count', 'image', 'caption', 'date_posted', 'author', 'is_anonymous',
            'companies', 'sectors', 'tags', 'choice1', 'choice2', 'choice3', 'choice1_votes', 'choice2_votes',
            'choice3_votes',
            'company_ids', 'sector_ids', 'tag_names', 'author_username'
        ]
        read_only_fields = ['companies', 'sectors', 'tags', 'author_username']

    def get_author_username(self, obj):
        return obj.author.username if obj.author else "Anonymous"

    def create(self, validated_data):
        company_ids = validated_data.pop('company_ids', [])
        sector_ids = validated_data.pop('sector_ids', [])
        tag_names = validated_data.pop('tag_names', [])

        poll = Poll.objects.create(**validated_data)

        for company_id in company_ids:
            try:
                company = Company.objects.get(id=company_id)
                poll.companies.add(company)
            except Company.DoesNotExist:
                pass

        for sector_id in sector_ids:
            try:
                sector = Sector.objects.get(id=sector_id)
                poll.sectors.add(sector)
            except Sector.DoesNotExist:
                pass

        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            poll.tags.add(tag)

        return poll


class PollChoiceSerializer(serializers.Serializer):
    choice = serializers.ChoiceField(choices=['choice1', 'choice2', 'choice3'])

    def validate_choice(self, value):
        if value not in ['choice1', 'choice2', 'choice3']:
            raise serializers.ValidationError("Invalid choice.")
        return value


#For notification testing
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user', 'message', 'created_at', 'is_read')
