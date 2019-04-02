from django.db import models

from oi_sud.core.utils import nullable

CODEX_CHOICES = (
    ('uk', 'УК'),
    ('koap', 'КОАП'),
)


class CodexArticle(models.Model):
    article_number = models.CharField(max_length=10)
    part = models.CharField(max_length=10, **nullable)
    short_title = models.TextField(**nullable)
    parent_title = models.TextField(**nullable)
    full_text = models.TextField(**nullable)
    codex = models.CharField(max_length=4, choices=CODEX_CHOICES)

    def __str__(self):
        if self.part:
            return f'{self.article_number} ч.{self.part} {self.get_codex_display()}'
        else:
            return f'{self.article_number} {self.get_codex_display()}'
