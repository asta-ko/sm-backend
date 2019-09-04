from django.db import models

from oi_sud.core.utils import nullable

CODEX_CHOICES = (
    ('uk', 'УК'),
    ('koap', 'КОАП'), #TODO: КАС и ГПК
)


class ArticlesManager(models.Manager):
    def get_from_list(self, articles_list):
        articles = []
        for item in articles_list:  # ['19.3 ч.1',] -- для тестирования
            item_list = item.split(' ч.')
            article = item_list[0]
            if len(item_list) > 0:
                part = item_list[1]
            else:
                part = None
            a = super().get_queryset().filter(article_number=article, part=part).first()
            if a:
                articles.append(a)
        return articles

class CodexArticle(models.Model):
    article_number = models.CharField(max_length=10, verbose_name='Номер cтатьи')
    part = models.CharField(max_length=10, verbose_name='Часть статьи', **nullable)
    short_title = models.TextField(verbose_name='Короткое описание', **nullable)
    parent_title = models.TextField(verbose_name='Родительская статья', **nullable)
    full_text = models.TextField(verbose_name='Текст статьи', **nullable)
    codex = models.CharField(max_length=4, verbose_name='Кодекс', choices=CODEX_CHOICES)
    objects = ArticlesManager()

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'


    def __str__(self):
        if self.part:
            return f'{self.article_number} ч.{self.part} {self.get_codex_display()}'
        else:
            return f'{self.article_number} {self.get_codex_display()}'


    @staticmethod
    def autocomplete_search_fields():
        return 'article_number', 'short_title'




class KoapManager(ArticlesManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            codex='koap')


class UKManager(ArticlesManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            codex='uk')


class UKCodexArticle(CodexArticle):
    objects = UKManager()
    class Meta:
        proxy = True
        verbose_name = 'Статья УК'
        verbose_name_plural = 'Статьи УК'


class KoapCodexArticle(CodexArticle):
    objects = KoapManager()
    class Meta:
        proxy = True
        verbose_name = 'Статья КОАП'
        verbose_name_plural = 'Статьи КОАП'