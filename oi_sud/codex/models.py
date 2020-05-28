import logging
from django.db import models

from oi_sud.core.utils import nullable

logger = logging.getLogger(__name__)

CODEX_CHOICES = (
    ('uk', 'УК'),
    ('koap', 'КОАП'),  # TODO: КАС и ГПК
    )


class ArticlesManager(models.Manager):
    def get_from_list(self, articles_list, codex=None):
        articles = []
        for item in articles_list:  # ['19.3 ч.1',] -- для тестирования
            item_list = item.split(' ч.')

            article = item_list[0]
            if len(item_list) > 1:

                part = item_list[1]
            else:
                part = None

            params = {'article_number': article}
            if part:
                params['part'] = part
            if codex:
                params['codex'] = codex
            filtered_articles = super().get_queryset().filter(**params)
            logging.debug(f'filtered_articles{filtered_articles}')
            for a in filtered_articles:
                articles.append(a)
        return articles


class CodexArticle(models.Model):
    article_number = models.CharField(max_length=10, verbose_name='Номер cтатьи')
    part = models.CharField(max_length=10, verbose_name='Часть статьи', **nullable)
    short_title = models.TextField(verbose_name='Короткое описание', **nullable)
    parent_title = models.TextField(verbose_name='Родительская статья', **nullable)
    full_text = models.TextField(verbose_name='Текст статьи', **nullable)
    codex = models.CharField(max_length=4, verbose_name='Кодекс', choices=CODEX_CHOICES)
    active = models.BooleanField(default=True, verbose_name='Дела по статье собираются')
    objects = ArticlesManager()

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        if self.part:
            return f'{self.article_number} ч.{self.part} {self.get_codex_display()}'
        else:
            return f'{self.article_number} {self.get_codex_display()}'

    def get_number_and_part(self):
        if self.part:
            return f'{self.article_number} ч.{self.part}'
        else:
            return f'{self.article_number}'

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
