from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Article, Newsletter, Publisher, CustomUser
from .forms import CustomUserCreationForm
from .serializers import ArticleSerializer, NewsletterSerializer


# -------------------- Web Views --------------------

def home(request):
    """Display home page with all approved articles."""
    articles = Article.objects.filter(approved=True)
    return render(request, 'news/home.html', {'articles': articles})


def article_detail(request, pk):
    """Display a single article."""
    article = get_object_or_404(Article, pk=pk, approved=True)
    return render(request, 'news/article_detail.html', {'article': article})


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'news/register.html', {'form': form})


def is_editor(user):
    """Check if user is an editor."""
    return user.role == 'editor'


@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    """Show pending articles for editors to review."""
    pending_articles = Article.objects.filter(approved=False)
    return render(request, 'news/editor_dashboard.html', {'pending_articles': pending_articles})


@login_required
@user_passes_test(is_editor)
def approve_article(request, pk):
    """Approve an article and send email notifications to subscribers."""
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()

    subscribers = []

    if article.publisher:
        publisher_subscribers = article.publisher.subscribers.all()
        subscribers.extend(publisher_subscribers)

    journalist_subscribers = article.author.subscribers.all()
    subscribers.extend(journalist_subscribers)

    subscriber_emails = list(set(
        user.email for user in subscribers if user.email
    ))

    if subscriber_emails:
        subject = f'New Article: {article.title}'
        message = f'''Hello,

A new article has been published!

Title: {article.title}
Author: {article.author.username}
Publisher: {article.publisher.name if article.publisher else 'Independent'}

{article.content[:200]}...

Read more at the News App.

Best regards,
News App Team'''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=subscriber_emails,
            fail_silently=True,
        )

    messages.success(request, f'Article "{article.title}" approved! {len(subscriber_emails)} subscriber(s) notified.')
    return redirect('editor_dashboard')

@login_required
@user_passes_test(is_editor)
def editor_preview_article(request, pk):
    """Allow editors to preview unapproved articles."""
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'news/editor_preview.html', {'article': article})
# -------------------- Journalist Views --------------------

def is_journalist(user):
    """Check if user is a journalist."""
    return user.role == 'journalist'


@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    """Show journalist's articles and newsletters."""
    my_articles = Article.objects.filter(author=request.user)
    my_newsletters = Newsletter.objects.filter(author=request.user)

    # Get publishers this journalist belongs to
    my_publishers = request.user.publisher_journalist_of.all()

    return render(request, 'news/journalist_dashboard.html', {
        'my_articles': my_articles,
        'my_newsletters': my_newsletters,
        'my_publishers': my_publishers,
    })


@login_required
@user_passes_test(is_journalist)
def create_article(request):
    """Create a new article."""
    # Get publishers this journalist belongs to
    my_publishers = request.user.publisher_journalist_of.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        publisher_id = request.POST.get('publisher')

        article = Article.objects.create(
            title=title,
            content=content,
            author=request.user,
            approved=False
        )

        if publisher_id:
            from .models import Publisher
            publisher = Publisher.objects.filter(id=publisher_id).first()
            if publisher:
                article.publisher = publisher
                article.save()

        messages.success(request, f'Article "{title}" created! Waiting for editor approval.')
        return redirect('journalist_dashboard')

    return render(request, 'news/create_article.html', {
        'my_publishers': my_publishers,
    })


@login_required
@user_passes_test(is_journalist)
def edit_article(request, pk):
    """Edit an existing article."""
    article = get_object_or_404(Article, pk=pk, author=request.user)
    my_publishers = request.user.publisher_journalist_of.all()

    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        publisher_id = request.POST.get('publisher')

        if publisher_id:
            from .models import Publisher
            publisher = Publisher.objects.filter(id=publisher_id).first()
            article.publisher = publisher
        else:
            article.publisher = None

        article.save()
        messages.success(request, f'Article "{article.title}" updated!')
        return redirect('journalist_dashboard')

    return render(request, 'news/edit_article.html', {
        'article': article,
        'my_publishers': my_publishers,
    })


@login_required
@user_passes_test(is_journalist)
def delete_article(request, pk):
    """Delete an article."""
    article = get_object_or_404(Article, pk=pk, author=request.user)
    title = article.title
    article.delete()
    messages.success(request, f'Article "{title}" deleted!')
    return redirect('journalist_dashboard')


@login_required
@user_passes_test(is_journalist)
def create_newsletter(request):
    """Create a new newsletter."""
    my_articles = Article.objects.filter(author=request.user, approved=True)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        article_ids = request.POST.getlist('articles')

        newsletter = Newsletter.objects.create(
            title=title,
            description=description,
            author=request.user
        )

        if article_ids:
            newsletter.articles.set(article_ids)

        messages.success(request, f'Newsletter "{title}" created!')
        return redirect('journalist_dashboard')

    return render(request, 'news/create_newsletter.html', {
        'my_articles': my_articles,
    })


@login_required
@user_passes_test(is_journalist)
def edit_newsletter(request, pk):
    """Edit an existing newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk, author=request.user)
    my_articles = Article.objects.filter(author=request.user, approved=True)

    if request.method == 'POST':
        newsletter.title = request.POST.get('title')
        newsletter.description = request.POST.get('description')
        article_ids = request.POST.getlist('articles')

        newsletter.articles.set(article_ids)
        newsletter.save()

        messages.success(request, f'Newsletter "{newsletter.title}" updated!')
        return redirect('journalist_dashboard')

    return render(request, 'news/edit_newsletter.html', {
        'newsletter': newsletter,
        'my_articles': my_articles,
    })


@login_required
@user_passes_test(is_journalist)
def delete_newsletter(request, pk):
    """Delete a newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk, author=request.user)
    title = newsletter.title
    newsletter.delete()
    messages.success(request, f'Newsletter "{title}" deleted!')
    return redirect('journalist_dashboard')


# -------------------- Reader Subscription Views --------------------

@login_required
def subscriptions(request):
    """Manage subscriptions for readers."""
    from .models import Publisher, CustomUser

    publishers = Publisher.objects.all()

    #Prevent journalist from subscribing to themselves
    journalists = CustomUser.objects.filter(role='journalist').exclude(pk=request.user.pk)

    return render(request, 'news/subscriptions.html', {
        'publishers': publishers,
        'journalists': journalists,
        'my_subscribed_publishers': request.user.subscribed_publishers.all(),
        'my_subscribed_journalists': request.user.subscribed_journalists.all(),
    })


@login_required
def toggle_publisher_subscription(request, pk):
    """Subscribe or unsubscribe from a publisher."""
    from .models import Publisher
    publisher = get_object_or_404(Publisher, pk=pk)

    if publisher in request.user.subscribed_publishers.all():
        request.user.subscribed_publishers.remove(publisher)
        messages.success(request, f'Unsubscribed from {publisher.name}')
    else:
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f'Subscribed to {publisher.name}')

    return redirect('subscriptions')


@login_required
def toggle_journalist_subscription(request, pk):
    """Subscribe or unsubscribe from a journalist."""
    from .models import CustomUser
    journalist = get_object_or_404(CustomUser, pk=pk, role='journalist')

    if journalist in request.user.subscribed_journalists.all():
        request.user.subscribed_journalists.remove(journalist)
        messages.success(request, f'Unsubscribed from {journalist.username}')
    else:
        request.user.subscribed_journalists.add(journalist)
        messages.success(request, f'Subscribed to {journalist.username}')

    return redirect('subscriptions')


def newsletter_list(request):
    """View all newsletters."""
    newsletters = Newsletter.objects.all()
    return render(request, 'news/newsletter_list.html', {'newsletters': newsletters})


def newsletter_detail(request, pk):
    """View a single newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(request, 'news/newsletter_detail.html', {'newsletter': newsletter})

# -------------------- API Views --------------------

@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def article_list_create(request):
    """List approved articles or create a new one."""
    if request.method == 'GET':
        articles = Article.objects.filter(approved=True)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != 'journalist':
            return Response({'detail': 'Only journalists can create articles.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscribed_articles(request):
    """List articles from subscribed publishers and journalists."""
    user = request.user
    subscribed_publishers = user.subscribed_publishers.all()
    subscribed_journalists = user.subscribed_journalists.all()

    articles = Article.objects.filter(approved=True).filter(
        models.Q(publisher__in=subscribed_publishers) |
        models.Q(author__in=subscribed_journalists)
    ).distinct()

    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.AllowAny])
def article_detail_api(request, pk):
    """Get, update, or delete an article."""
    if request.method == 'GET':
        article = get_object_or_404(Article, pk=pk, approved=True)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.user.role not in ['editor', 'journalist']:
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

    article = get_object_or_404(Article, pk=pk)

    if request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def newsletter_list_create(request):
    """List newsletters or create a new one."""
    if request.method == 'GET':
        newsletters = Newsletter.objects.all()
        serializer = NewsletterSerializer(newsletters, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != 'journalist':
            return Response({'detail': 'Only journalists can create newsletters.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = NewsletterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.AllowAny])
def newsletter_detail_api(request, pk):
    """Get, update, or delete a newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == 'GET':
        serializer = NewsletterSerializer(newsletter)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.user.role != 'journalist':
        return Response({'detail': 'Only journalists can modify newsletters.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = NewsletterSerializer(newsletter, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        newsletter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)