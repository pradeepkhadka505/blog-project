from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post,Comment 
from blog.forms import CommentForm 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
from django.db.models import Count
from django.db.models import Q 



# Create your views here.
#views of functions for listing all post 
def post_list(request, tag_slug=None):
    posts = Post.published.all()

    paginator = Paginator(posts, 10)  # 10 posts in each page
    page = request.GET.get('page')
     #tags 
    tag = None 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
        
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an interfer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        #if page is out of the range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    #search 
    query = request.GET.get("q")
    if query:
        posts = Post.published.filter(Q(title__icontains = query) | Q(tags__name__icontains=query)).distinct()

    return render(request, 'post_list.html', {'posts':posts, page:'pages', 'tag':tag})

#functions to show individual page details
def post_detail(request, post):
    post = get_object_or_404(Post, slug=post, status='published')
        #list of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    comment_form = CommentForm()

    if request.method == 'POST':
            #A comments was posted 
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
                #Create comments objects but dont dave to database yet
            new_comment = comment_form.save(commit=False)
                #assign the current post to the comment 
            new_comment.post = post 
                #save the comment to the database 
            new_comment.save()
                #redirect to same page and focus on that comment
            return redirect(post.get_absolute_url()+'#'+str(new_comment.id))
        else:
            comment_form = CommentForm()

        # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:6]

    return render(request, 'post_detail.html',{'post':post,'comments':comments, 'comment_form':comment_form, 'similar_posts':similar_posts})

#functions for comment Reply
def reply_page(request):
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            post_id = request.POST.get('post_id')
            parent_id = request.POST.get('parent')
            post_url = request.POST.get('post_url')

            reply = form.save(commit=False)

            reply.post = Post(id=post_id)
            reply.parent = Comment(id=parent_id)
            reply.save()

            return redirect(post_url+'#'+str(reply.id))

    return redirect("/")