from django.db import models


class Muster(models.Model):
    data = models.TextField()
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'muster'  # तुमचं table name override करत आहे
