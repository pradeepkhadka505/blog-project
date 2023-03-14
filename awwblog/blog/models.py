from django.db import models
from django.utils import timezone 
from django.contrib.auth.models import User 
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField 
from taggit.managers import TaggableManager

# Create your models manager
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')

#post Model 
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length = 250)
    slug = models.SlugField(max_length =250, unique_for_date = 'publish')
    image = models.ImageField(upload_to='featured_image/%y/%m/%d/')  #this
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'blog_posts')
    body = RichTextUploadingField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length= 10, choices= STATUS_CHOICES,default='draft')
    tags = TaggableManager()

    class Meta:
        ordering = ('-publish',)
        def __str__(self):
            return self.title
        
    objects = models.Manager() # The default manager
    published = PublishedManager() # Our custom Manger 

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    #to get the comment with parents is none and ativeis true, we ccan use this 
    def get_comments(self):
        return self.comments.filter(parent=None).filter(active=True)


#model class comments
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=50)
    email = models.EmailField()
    parent = models.ForeignKey("self", null = True, blank=True, on_delete= models.CASCADE)
    body = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now = True)
    active = models.BooleanField(default = True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.body
    
    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)

    
