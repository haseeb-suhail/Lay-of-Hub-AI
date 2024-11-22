from django.contrib import admin
from django.utils.html import format_html

from .models import User_Model, Referral, Badge, Group, Post, Comment, Company, Sector, Tag, Community, Question, Answer, Poll, Upvote

@admin.register(User_Model)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_total_points_awarded', 'get_referral_points', 'get_upvotes', 'badge')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_total_points_awarded(self, obj):
        return obj.total_points_awarded
    get_total_points_awarded.short_description = 'Total Points Awarded'

    def get_referral_points(self, obj):
        return obj.referral_points
    get_referral_points.short_description = 'Referral Points'

    def get_upvotes(self, obj):
        return obj.upvotes
    get_upvotes.short_description = 'Upvotes'

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referred_by', 'referred_to', 'points_awarded', 'created_at')
    search_fields = ('referred_by__username', 'referred_to__username')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_by')
    search_fields = ('name', 'created_by__username')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'heading', 'content', 'created_at', 'approved', 'upvotes')
    search_fields = ('author__username', 'heading')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    search_fields = ('author__username', 'post__heading')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'public_or_private', 'industry', 'sector', 'display_picture')
    search_fields = ('name', 'symbol', 'industry', 'sector')
    fields = ('name', 'symbol', 'name_on_website', 'public_or_private', 'industry', 'sector', 'clean_name', 'website_url', 'picture')  # Include picture in fields

    def display_picture(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.picture.url)
        return "No Image"
    display_picture.short_description = 'Picture'

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('sub_sector', 'industry', 'sector')
    search_fields = ('sub_sector', 'industry', 'sector')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'view_count', 'date_posted', 'author', 'is_anonymous', 'votes')
    search_fields = ('title', 'community', 'author__username')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_display_name', 'content', 'date_posted')
    search_fields = ('question__title', 'user__username', 'pseudonym')

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'view_count', 'date_posted', 'author', 'is_anonymous', 'choice1', 'choice2', 'choice3', 'choice1_votes', 'choice2_votes', 'choice3_votes')
    search_fields = ('title', 'community', 'author__username')

@admin.register(Upvote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'post_author', 'created_at')
    search_fields = ('post__heading', 'user__username', 'post_author__username')
