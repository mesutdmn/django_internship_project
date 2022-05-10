from django.contrib import admin
from .models import Article
from django.utils.html import format_html
# Register your models here.


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display_links=["title"] # linkle
    def git(self):
        return format_html("<a href='/etkinlik/%d'>İncele</a>" % self.id)
    git.allow_tags = True
    git.short_description = 'Etkinlik Sayfası'
    list_display=["id","title","author","created_date",git] #göster

    search_fields=["title","content"] #içerik ve başlıkta arama
    list_filter=["created_date"]
    class Meta:
        model=Article
