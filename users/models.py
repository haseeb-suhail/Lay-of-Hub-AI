#models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from PIL import Image

class User_Model(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)  # Ensure this is unique
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referral_points = models.IntegerField(default=0)  # To track points from referrals
    total_points_awarded = models.IntegerField(default=0)  # Total points awarded to the user
    upvotes = models.IntegerField(default=0)  # Track upvotes
    downvotes = models.IntegerField(default=0)
    badge = models.CharField(max_length=255, null=True, blank=True)  # Store badge name
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    agreement = models.BooleanField(default=True)
    referred_by_code = models.CharField(max_length=100, blank=True, null=True)


    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    PASSWORD_FIELD = 'password'

    def __str__(self):
        return self.email

    def update_badges(self):
        if self.total_points_awarded >= 5000:
            badge_name = 'Oracle'
        elif self.total_points_awarded >= 1000:
            badge_name = 'Elder'
        elif self.total_points_awarded >= 500:
            badge_name = 'Guru'
        elif self.total_points_awarded >= 250:
            badge_name = 'Master of Scuttlebutt'
        elif self.total_points_awarded >= 100:
            badge_name = 'Rumor Connoisseur'
        elif self.total_points_awarded >= 50:
            badge_name = 'Contributor'
        else:
            badge_name = 'Layoff Whisperer'

        if self.badge != badge_name:
            self.badge = badge_name
            self.save()

        message = (f"Congratulations {self.username}! You have been awarded the '{badge_name}'")
        Notification.objects.create(user=self, message=message)

    def add_points(self, points, is_referral=False):
        self.total_points_awarded += points
        if is_referral:
            self.referral_points += points
        self.save()
        self.update_badges()


class Referral(models.Model):
    referred_by = models.ForeignKey(User_Model, on_delete=models.CASCADE, related_name='given_referrals')
    referred_to = models.ForeignKey(User_Model, on_delete=models.CASCADE, related_name='received_referrals')
    points_awarded = models.IntegerField(default=0)  # Track points awarded for this referral
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Award points to the referrer if points haven't been awarded for this referral
        if not self.points_awarded:
            referral_points = 10  # Example point value
            self.referred_by.add_points(referral_points, is_referral=True)  # Add points to the referrer
            self.points_awarded = referral_points
        super().save(*args, **kwargs)



class Badge(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    users = models.ManyToManyField(User_Model, related_name='badges')

    def __str__(self):
        return self.name


# Group Model
class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_groups', blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member_groups', blank=True)
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='moderator_groups', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_groups', on_delete=models.CASCADE,
                                   null=True, blank=True)

    def __str__(self):
        return self.name


# Comment Model
class Post(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    author_username = models.CharField(max_length=150, blank=True,
                                       null=True)  # Add this field if you want to store username directly
    heading = models.CharField(max_length=255, null=True, blank=True)  # Add this field for the post heading
    content = models.TextField()  # This is the description/post text
    image = models.URLField(blank=True, null=True)  # For image URL
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)  # For image file
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Set author_username to the author's username before saving
        if not self.author_username:
            self.author_username = self.author.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.heading

    def add_upvote(self, user):
        # Check if an upvote record exists for this user and post
        if Upvote.objects.filter(post=self, user=user).exists():
            return "You have already upvoted this post."

        # Create an Upvote record if it doesn't exist
        Upvote.objects.create(post=self, user=user, post_author=self.author)

        # Increment the upvote count for the post
        self.upvotes += 1
        self.save()

        # Award points to the post author
        if self.author:
            self.author.upvotes += 1  # Increment upvotes for the user
            self.author.add_points(1)  # Award 1 point for each upvote
            self.author.update_badges()  # Update badges based on new points
            self.author.save()  # Ensure the user data is saved

        return "Upvote added successfully."

    def update_upvote_count(self):
        self.upvote_count = self.upvotes.count()
        self.save()

    def add_downvote(self, user):
        # Check if a downvote record exists for this user and post
        if Downvote.objects.filter(post=self, user=user).exists():
            return "You have already downvoted this post."

        # Create a Downvote record if it doesn't exist
        Downvote.objects.create(post=self, user=user, post_author=self.author)

        # Increment the downvote count for the post
        self.downvotes += 1
        self.save()

        # Deduct points from the post author
        if self.author:
            self.author.downvotes += 1  # Increment downvotes for the user
            self.author.add_points(-1)  # Deduct 1 point for each downvote
            self.author.update_badges()  # Update badges based on new points
            self.author.save()  # Ensure the user data is saved

        return "Downvote added successfully."

    def update_downvote_count(self):
        self.downvotes = self.downvote_records.count()  # Correct the attribute access
        self.save()

class Question(models.Model):
    title = models.CharField(max_length=255)
    community = models.CharField(max_length=255, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    featured_image = models.ImageField(upload_to='featured_images/', blank=True, null=True)
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    caption = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    companies = models.ManyToManyField('Company', blank=True, related_name='questions')
    sectors = models.ManyToManyField('Sector', blank=True, related_name='questions')
    tags = models.ManyToManyField('Tag', blank=True, related_name='questions')
    votes = models.IntegerField(default=0)

    def __str__(self):
        if self.is_anonymous:
            return f'Anonymous Question {self.id}'
        return f'{self.author.username}\'s Question' if self.author else f'Anonymous Question {self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and self.image.path:
            try:
                img = Image.open(self.image.path)
                if img.height > 400 or img.width > 400:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
            except FileNotFoundError:
                pass


class Upvote(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='upvote_records',null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_upvotes', null=True)
    post_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_upvotes',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('Question', related_name='upvotes_records', on_delete=models.CASCADE, null=True)  # Updated related_name

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):
        return f"{self.user.username} upvoted post {self.post.id} by {self.post_author.username}"

class Downvote(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='downvote_records',null=True)  # Added related_name
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_downvotes',
        null = True# Updated related_name
    )
    post_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_downvotes',
        null=True# Updated related_name
    )
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('Question', related_name='downvotes_records', on_delete=models.CASCADE, null=True)  # Updated related_name
    class Meta:
        unique_together = ('question', 'user')

# Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]


#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
from django.db import models
from PIL import Image


class Company(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=50)
    name_on_website = models.CharField(max_length=255)
    public_or_private = models.CharField(max_length=50)
    industry = models.CharField(max_length=255)
    industry_clean = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)
    clean_name = models.CharField(max_length=255)
    website_url = models.URLField()
    picture = models.ImageField(upload_to='company_pictures/', blank=True, null=True)  # Picture field

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            img = Image.open(self.picture.path)
            if img.height > 400 or img.width > 400:
                output_size = (400, 400)
                img.thumbnail(output_size)
                img.save(self.picture.path)


class Sector(models.Model):
    sub_sector = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.sub_sector} - {self.industry} - {self.sector}"


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Community(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    is_anonymous = models.BooleanField(default=False)
    parent_answer = models.ForeignKey('self', null=True, blank=True, related_name='child_answers',
                                      on_delete=models.CASCADE)

    def __str__(self):
        return f'Answer to {self.question}'

    def get_display_name(self):
        if self.user:
            return self.user.username


class Poll(models.Model):
    title = models.CharField(max_length=255)
    community = models.CharField(max_length=255)
    view_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to="poll_images", null=True, blank=True)
    caption = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    companies = models.ManyToManyField('Company', blank=True, related_name='polls')
    sectors = models.ManyToManyField('Sector', blank=True, related_name='polls')
    tags = models.ManyToManyField('Tag', blank=True, related_name='polls')
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255, null=True, blank=True)
    choice3 = models.CharField(max_length=255, null=True, blank=True)
    choice1_votes = models.IntegerField(default=0)
    choice2_votes = models.IntegerField(default=0)
    choice3_votes = models.IntegerField(default=0)

    def __str__(self):
        if self.is_anonymous:
            return f'{self.author.username}\'s Poll' if self.author else f'Anonymous Poll {self.id}'

    def increment_view_count(self):
        self.view_count += 1
        self.save()

    def update_poll_choice(self, choice):
        if choice == 'choice1':
            self.choice1_votes += 1
        elif choice == 'choice2':
            self.choice2_votes += 1
        elif choice == 'choice3':
            self.choice3_votes += 1
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and self.image.path:
            try:
                img = Image.open(self.image.path)
                if img.height > 400 or img.width > 400:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
            except FileNotFoundError:
                pass


#for notification testing
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - {self.message}"
