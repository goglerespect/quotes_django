from django.db import models

class Author(models.Model):
    fullname = models.CharField(max_length=255, unique=True)
    born_date = models.CharField(max_length=255, blank=True, null=True)
    born_location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fullname

class Quote(models.Model):
    quote = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="quotes")
    tags = models.CharField(max_length=255, blank=True, null=True)  # "life, inspirational"

    def tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",")]

    def __str__(self):
        return self.quote[:50]
