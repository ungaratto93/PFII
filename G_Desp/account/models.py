
import uuid

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class MagicKey(models.Model):

    """ The purpose of this model is for generate random keys """

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    key = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
