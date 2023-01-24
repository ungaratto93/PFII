import datetime

# Create your models here.
from django.utils import timezone
from django.db import models


class Category(models.Model):
	code = models.IntegerField(null=False)
	name = models.CharField(null=False, max_length=55)
	description = models.CharField(null=False, max_length=255)
	registered_at = models.DateTimeField()
	registered_by = models.CharField(null=False, max_length=55)

	def __str__(self):
		return self.name


class Inflow(models.Model):
	name = models.CharField(null=False, max_length=255)
	value = models.DecimalField(null=False, max_digits=10, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.PROTECT)
	registered_at = models.DateTimeField()
	registered_by = models.CharField(null=False, max_length=55)

	def __str__(self):
		return self.name

	def was_registered_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1) <= self.registered_at <= now


class Outflow(models.Model):
	name = models.CharField(null=False, max_length=255)
	value = models.DecimalField(null=False, max_digits=10, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.PROTECT)
	registered_at = models.DateTimeField()
	registered_by = models.CharField(null=False, max_length=55)
	billet_code = models.IntegerField(null=True, blank=True)
	payment_code = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.name

	def was_registered_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1) <= self.registered_at <= now


class Report(models.Model):
	month = models.IntegerField(null=True, blank=True)
	year = models.IntegerField(null=True, blank=True)
	inflow_sum_values = models.DecimalField(null=False, max_digits=10, decimal_places=2, default=0.00)
	outflow_sum_values = models.DecimalField(null=False, max_digits=10, decimal_places=2, default=0.00)
	inflow_outflow_dif_values = models.DecimalField(null=False, max_digits=10, decimal_places=2, default=0.00)
	registered_at = models.DateTimeField()
	registered_by = models.CharField(null=False, max_length=55, default='')

	def calc_dif_values(self):
		try:
			dif = self.inflow_sum_values - self.outflow_sum_values
		except Exception as e:
			raise e
		return dif