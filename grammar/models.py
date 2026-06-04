from django.db import models

class GrammarTopic(models.Model):
    LEVELS = [
        ('beginner', 'С нуля'),
        ('elementary', 'Начальный'),
        ('intermediate', 'Средний'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='📖')
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVELS, default='beginner')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class GrammarRule(models.Model):
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='rules')
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    formula = models.CharField(max_length=500, blank=True)
    examples = models.JSONField(default=list, blank=True)
    korean_examples = models.JSONField(default=list, blank=True)
    russian_examples = models.JSONField(default=list, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.topic.title} — {self.title}'

class GrammarExercise(models.Model):
    DIFFICULTY = [
        ('beginner', 'С нуля'),
        ('elementary', 'Начальный'),
        ('intermediate', 'Средний'),
    ]
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='exercises', null=True, blank=True)
    question = models.TextField()
    correct_answer = models.CharField(max_length=500)
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY, default='beginner')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question[:50]

    def options_list(self):
        opts = [('a', self.option_a), ('b', self.option_b)]
        if self.option_c: opts.append(('c', self.option_c))
        if self.option_d: opts.append(('d', self.option_d))
        return opts
