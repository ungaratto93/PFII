import calendar
from datetime import datetime

from django.db.models import Avg, Count, Min, ProtectedError, Sum, CharField, Value
from django.utils import timezone

from cashflow.models import Inflow, Outflow, Report, Category

from django.db.models.functions import (Extract, ExtractDay, ExtractHour,
	ExtractMinute, ExtractMonth, ExtractQuarter, ExtractSecond, ExtractWeek, 
	ExtractWeekDay, ExtractYear
	)

def get_first_day_month():

	date = None

	try:

		month = timezone.now().month
		if len(str(month)) == 1:
			month = int('0' + str(month))

		year = timezone.now().year
		month_range = calendar.monthrange(year, int(month))
		day = month_range[1] - (month_range[1] - 1)
		date = datetime(year, month, day)

	except ValueError as exc:
		print(exc, "ValueError")
	except TypeError as exc:
		print(exc, "TypeError")
	return date


def get_my_current_balance():

	balance = 0.00
	inflow_amount = 0.00
	outflow_amount = 0.00

	try:

		first_day = get_first_day_month()

		inflow_amount_on_this_month = Inflow.objects.filter(
			registered_at__gt=first_day
		).aggregate(
			amount=Sum('value')
		)

		outflow_amount_on_this_month = Outflow.objects.filter(
			registered_at__gt=first_day
		).aggregate(
			amount=Sum('value')
		)

		inflow_amount = inflow_amount_on_this_month['amount']
		outflow_amount = outflow_amount_on_this_month['amount']
		balance = inflow_amount - outflow_amount

	except ValueError as exc:
		print(exc, "Wow, An ValueError was occurred")
	except TypeError as exc:
		print(exc, "Wow, An TypeError was occurred")
	return balance, inflow_amount, outflow_amount


def get_my_categories():
	""" all categories of current user """
	try:
		data = Category.objects.filter(
			registered_by=request.user.username
		)
	except Category.DoesNotExist:
		data = None
	return data


def get_last_inflow_outflow():
	""" get last inflow and last outflow """
	print(".")

def get_my_reports_exists(request):
	exists = Report.objects.filter(
		registered_by__iexact=request.user.username
	).exists()
	return exists

def get_outflow(m, y, total_outflow):
	''' Persists outflows values '''
	try:
		report = Report.objects.filter(
			month=m,
			year=y
		)
		if report:
			report[0].outflow_sum_values = total_outflow
			report[0].save()
	except Report.DoesNotExist as e:
		raise e
	except TypeError as e:
		raise e

def get_my_report(request):
	""" get my report by month interval """
	# TODO FILTER BY MONTH INTERVAL
	try:
		labels = []
		data_in = []
		data_out = []
		diff = []
		data = []
		dataset = None

		exists = get_my_reports_exists(
			request=request
		)
		if exists:
			Report.objects.filter(
				registered_by__iexact=request.user.username
			).delete()

		inflow_dataset = Inflow.objects.filter(
			registered_by=request.user.username
		).\
		annotate(
			month=ExtractMonth('registered_at'), 
			year=ExtractYear('registered_at'),
		).\
		order_by().values(
			'year', 'month', 'registered_by'
		).\
		annotate(
			totali=Sum('value')
		).\
		annotate(
			type=Value('Inflow', output_field=CharField())
		).\
		values(
			'month','year','totali', 
			'registered_by','type'
		)

		outflow_dataset = Outflow.objects.filter(
			registered_by=request.user.username
		).\
		annotate(
			month=ExtractMonth('registered_at'), 
			year=ExtractYear('registered_at'),
		).\
		order_by().values(
			'year', 'month','registered_by'
		).\
		annotate(
			totalo=Sum('value')).\
		annotate(
			type=Value('Outflow', output_field=CharField())
		).\
		values(
			'month','year','totalo', 
			'registered_by', 'type'
		)

		sizes_in = len(inflow_dataset)

		# Create report object
		size = 0			
		if not exists:
			while (size < sizes_in):
				r = Report()
				r.month = inflow_dataset[size]['month']
				r.year = inflow_dataset[size]['year']
				r.inflow_sum_values = inflow_dataset[size]['totali']
				r.registered_at='2020-01-01 00:00:00' # fix it
				r.registered_by = inflow_dataset[size]['registered_by']
				r.save()
				size = size+1

		# Get reports created
		reports = Report.objects.filter(
			registered_by__iexact=request.user.username
		)

		# Get outflows values
		for outfl in outflow_dataset:
			get_outflow(
				outfl['month'],
				outfl['year'],
				outfl['totalo']
			)

		# Get reports updated
		dataset = Report.objects.filter(
			registered_by__iexact=request.user.username
		)

		# Calc difference 
		for report in dataset:
			difference = report.calc_dif_values()
			report.inflow_outflow_dif_values = difference
			report.save()

		# Get reports updated
		dataset = Report.objects.filter(
			registered_by__iexact=request.user.username
		)

		queryset = Report.objects.filter(
			registered_by__iexact=request.user.username
		)
		for row in queryset:
			labels.append([row.year, row.month])
			data_in.append(float(row.inflow_sum_values))
			data_out.append(float(row.outflow_sum_values))
			diff.append(float(row.inflow_outflow_dif_values))

		print("json response for build chart js report")
		data_in = '{"data_in" : ' + str(data_in)  + '}'
		data_out = '{"data_out" : ' + str(data_out)  + '}'
		diff = '{"diff" : ' + str(diff)  + '}'
		print(data_in)
		print(data_out)
	except (
		Inflow.DoesNotExist,
		Outflow.DoesNotExist,
		Report.DoesNotExist
	) as e:
		raise e
	except TypeError as e:
		raise e
	return dataset, labels, data_in, data_out, diff

