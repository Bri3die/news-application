from rest_framework import serializers
from .models import CustomUser, Publisher, Article, Newsletter


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher."""
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'description', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user public info."""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article with nested author and publisher."""
    
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'publisher', 'approved', 'created_at', 'updated_at']
        read_only_fields = ['approved', 'created_at', 'updated_at']


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter with nested articles."""
    
    author = UserSerializer(read_only=True)
    articles = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = Newsletter
        fields = ['id', 'title', 'description', 'author', 'articles', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
