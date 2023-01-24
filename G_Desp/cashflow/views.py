
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Min, ProtectedError, Sum, CharField, Value

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Category, Inflow, Outflow
from .utils import get_first_day_month, get_my_current_balance, get_my_report

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# Create your views here.


@login_required(login_url='/account/login')
def category_delete(request, pk):
    try:
        category = Category.objects.filter(
            pk=pk,
            registered_by=request.user.get_username()
        )
        if len(category) > 0:
            was_deleted = Category.objects.filter(
                pk=pk,
                registered_by=request.user.get_username()
            ).delete()
            if was_deleted:
                messages.success(request, 'Category was deleted!')
                return render(request, 'cashflow/category_list.html')
            else:
                messages.error(request, 'An error was ocurred!')
                return render(request, 'cashflow/category_list.html')
        else:
            return HttpResponse('Category not found.')
    except ProtectedError as exc:
        messages.error(
            request,
            "Cannot delete some instances of model, because they are referenced through protected foreign keys."
        )
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect("/cashflow/category_list")


@login_required(login_url='/account/login')
def category_update(request, pk):
    try:
        code = request.POST['code']
        name = request.POST['name']
        description = request.POST['description']
        registered_at = request.POST['reg_date']
        registered_by = request.user.get_username()

        category = Category.objects.filter(
            pk=pk,
            registered_by=request.user.get_username()
        ).update(
            code=code,
            name=name,
            description=description,
            registered_at=registered_at,
            registered_by=registered_by
        )

        messages.success(request, "Category was updated!")
    except Exception as exc:
        messages.error(request, 'An error was ocurred.')
    return redirect("/cashflow/category_detail/" + str(pk))


@login_required(login_url='/account/login')
def category_edit(request, pk):
    try:
        category = get_object_or_404(
            Category,
            pk=pk,
            registered_by=request.user.get_username()
        )
    except Category.DoesNotExist as e:
        raise Http404('Category does not exist')
    except Http404 as e:
        return HttpResponse('404')
    return render(
        request,
        'cashflow/category_edit.html',
        {
            'category': category,
        }
    )


@login_required(login_url='/account/login')
def category_detail(request, pk):
    try:
        category = get_object_or_404(
            Category,
            pk=pk,
            registered_by=request.user.get_username()
        )
    except Category.DoesNotExist as exc:
        raise Http404('Category does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'cashflow/category_detail.html', {'category': category})


@login_required(login_url='/account/login')
def category_list(request):
    try:
        categories_inflow_count = 0
        categories_outflow_count = 0

        categories = Category.objects.filter(
            registered_by=request.user.get_username()
        )
        for category in categories:
            categories_inflow = Inflow.objects.filter(
                registered_by=request.user.get_username(),
                category=category
            )
            categories_outflow = Outflow.objects.filter(
                registered_by=request.user.get_username(),
                category=category
            )

            if categories_inflow:
                categories_inflow_count += categories_inflow.count()

            if categories_outflow:
                categories_outflow_count += categories_outflow.count()

    except Category.DoesNotExist as e:
        raise Http404('Category does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(
        request,
        'cashflow/category_list.html',
        {
            'categories': categories,
            'categories_inflow': categories_inflow_count,
            'categories_outflow': categories_outflow_count,
        }
    )


@login_required(login_url='/account/sign_in')
def category_save(request):
    try:
        if request.POST:

            category = Category()
            category.code = request.POST['code']
            category.name = request.POST['name']
            category.description = request.POST['description']
            category.registered_at = request.POST['reg_date']
            category.registered_by = request.user.username
            category.save()


            messages.success(request, "A new category was created!")
    except Exception as exc:
        print(exc)
        messages.error(request, 'Ocorreu um erro' + str(exc))
        return redirect('/cashflow/category_list')
    return redirect('/cashflow/category_list')


@login_required(login_url='/account/sign_in')
def category_create(request):
    try:
        template_name = "category_create"
    except Exception as exc:
        messages.error(request, 'erro')
    return render(
        request, 'cashflow/category_create.html',
    )


@login_required(login_url='/account/login')
def inflow_delete(request, pk):
    try:
        registered_by = request.user.get_username()
        inflow = Inflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        )
        if len(inflow) > 0:
            was_deleted = Inflow.objects.filter(
                pk=pk,
                registered_by=registered_by
            ).delete()
            if was_deleted:
                messages.success(request, 'Inflow was deleted!')
                return render(request, 'cashflow/inflow_list.html')
            else:
                messages.error(request, 'An error was ocurred!')
                return render(request, 'cashflow/inflow_list.html')
        else:
            return HttpResponse('Inflow not found.')
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect("/cashflow/inflow_list")


@login_required(login_url='/account/login')
def inflow_update(request, pk):
    try:
        name = request.POST['name']
        category = Category.objects.filter(
            registered_by__iexact=request.user.username,
            id__iexact=request.POST['categories']
        )[0]
        registered_at = request.POST['reg_date']
        registered_by = request.user.username
        value = request.POST['value']

        inflow = Inflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        ).update(
            name=name,
            value=value,
            category=category,
            registered_at=registered_at,
            registered_by=registered_by
        )
        messages.success(request, "Inflow was updated!")
    except Exception as exc:
        messages.error(request, 'An error was ocurred.')
    return redirect("/cashflow/inflow_detail/" + str(pk))


@login_required(login_url='/account/login')
def inflow_edit(request, pk):
    try:
        categories = None
        registered_by = request.user.get_username()
        categories = Category.objects.filter(
            registered_by__iexact=request.user.get_username()
        )
        inflow = get_object_or_404(
            Inflow,
            pk=pk,
            registered_by=registered_by
        )
    except Inflow.DoesNotExist as e:
        raise Http404('Inflow does not exist')
    except Http404 as e:
        return HttpResponse('404')
    return render(
        request,
        'cashflow/inflow_edit.html',
        {
            'inflow': inflow,
            'categories': categories,
        }
    )


@login_required(login_url='/account/login')
def inflow_detail(request, pk):
    try:
        registered_by = request.user.get_username()
        inflow = get_object_or_404(
            Inflow,
            pk=pk,
            registered_by=registered_by
        )
    except Inflow.DoesNotExist as exc:
        raise Http404('Inflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'cashflow/inflow_detail.html', {'inflow': inflow})


@login_required(login_url='/account/login')
def inflow_list(request):
    try:

        template_name = 'cashflow/inflow_list.html'
        str_date = get_first_day_month()
        registered_by = request.user.get_username()
        print(str_date)
        inflows = Inflow.objects.filter(
            registered_at__gte=str_date,
            registered_by=registered_by
        )
    except Inflow.DoesNotExist as e:
        raise Http404('Inflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(
        request,
        'cashflow/inflow_list.html',
        {
            'inflows': inflows
        }
    )


@login_required(login_url='/account/sign_in')
def inflow_save(request):
    try:
        if request.POST:
            category = Category.objects.filter(
                registered_by__iexact=request.user.username,
                id__iexact=request.POST['categories']
            )[0]

            inflow = Inflow()
            inflow.name = request.POST['name']
            inflow.category = category
            inflow.registered_at = request.POST['reg_date']
            inflow.registered_by = request.user.username
            inflow.value = request.POST['value']
            inflow.save()

            messages.success(request, "A new inflow was created!")
    except Exception as exc:
        messages.error(request, 'Ocorreu um erro' + str(exc))
        return redirect('/cashflow/inflow_list')
    return redirect('/cashflow/inflow_list')


@login_required(login_url='/account/sign_in')
def inflow_create(request):
    categories = None
    no_categories = False
    try:
        categories = Category.objects.filter(
            registered_by__iexact=request.user.username
        )
        if categories.count() == 0:
            no_categories = True
    except Exception as exc:
        messages.error(request, 'erro')
    return render(
        request,
        'cashflow/inflow_create.html',
        {
            'messages': messages,
            'categories': categories,
            'no_categories': no_categories,
        }
    )


@login_required(login_url='/account/login')
def outflow_delete(request, pk):
    try:
        registered_by = request.user.get_username()
        outflow = Outflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        )
        if (len(outflow) > 0):
            was_deleted = Outflow.objects.filter(
                pk=pk,
                registered_by=registered_by
            ).delete()
            if was_deleted:
                messages.success(request, 'Outflow was deleted!')
                return render(request, 'cashflow/outflow_list.html')
            else:
                messages.error(request, 'An error was ocurred!')
                return render(request, 'cashflow/outflow_list.html')
        else:
            return HttpResponse('Outflow not found.')
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect("/cashflow/outflow_list")


@login_required(login_url='/account/login')
def outflow_update(request, pk):
    try:
        name = request.POST['name']
        category = Category.objects.filter(
            registered_by__iexact=request.user.username,
            id__iexact=request.POST['categories']
        )[0]
        registered_at = request.POST['reg_date']
        registered_by = request.user.username
        value = request.POST['value']

        outflow = Outflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        ).update(
            name=name,
            value=value,
            category=category,
            registered_at=registered_at,
            registered_by=registered_by
        )
        messages.success(request, "Outflow was updated!")
    except Exception as exc:
        messages.error(request, 'An error was ocurred.')
    return redirect("/cashflow/outflow_detail/" + str(pk))


@login_required(login_url='/account/login')
def outflow_edit(request, pk):
    try:
        categories = None
        registered_by = request.user.get_username()
        categories = Category.objects.filter(
            registered_by__iexact=request.user.get_username()
        )
        outflow = get_object_or_404(
            Outflow, pk=pk,
            registered_by=registered_by
        )
    except Outflow.DoesNotExist as e:
        raise Http404('Outflow does not exist')
    except Http404 as e:
        return HttpResponse('404')
    return render(
        request,
        'cashflow/outflow_edit.html',
        {
            'outflow': outflow,
            'categories': categories,
        }
    )


@login_required(login_url='/account/login')
def outflow_detail(request, pk):
    try:
        registered_by = request.user.get_username()
        outflow = get_object_or_404(
            Outflow, pk=pk,
            registered_by=registered_by
        )
    except Outflow.DoesNotExist as exc:
        raise Http404('Outflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'cashflow/outflow_detail.html', {'outflow': outflow})


@login_required(login_url='/account/login')
def outflow_list(request):
    try:
        template_name = 'cashflow/outflow_list.html'
        str_date = get_first_day_month()
        registered_by = request.user.get_username()

        outflows = Outflow.objects.filter(
            registered_at__gte=str(str_date),
            registered_by=registered_by
        )
    except Outflow.DoesNotExist as e:
        raise Http404('Outflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'cashflow/outflow_list.html', {'outflows': outflows})


@login_required(login_url='/account/sign_in')
def outflow_save(request):
    try:
        if request.POST:
            category = Category.objects.filter(
                registered_by__iexact=request.user.username,
                id__iexact=request.POST['categories']
            )[0]

            outflow = Outflow()
            outflow.name = request.POST['name']
            outflow.category = category
            outflow.registered_at = request.POST['reg_date']
            outflow.registered_by = request.user.username
            outflow.value = request.POST['value']
            outflow.payment_code = request.POST['payment_code']
            outflow.billet_code = request.POST['billet_code']
            outflow.save()

            messages.success(request, "A new outflow was created!")
    except Exception as exc:
        messages.error(request, 'Ocorreu um erro' + str(exc))
        return redirect('/cashflow/outflow_list')
    return redirect('/cashflow/outflow_list')


@login_required(login_url='/account/sign_in')
def outflow_create(request):
    categories = None
    no_categories = False
    try:
        categories = Category.objects.filter(
            registered_by__iexact=request.user.username)
        if categories.count() == 0:
            no_categories = True
    except Exception as exc:
        messages.error(request, 'erro')
    return render(
        request,
        'cashflow/outflow_create.html',
        {
            'messages': messages,
            'categories': categories,
            'no_categories': no_categories,
        }
    )


@login_required(login_url='/account/sign_in')
def home(request):
    """ THis func is to show a overview about cashflow stats """
    try:
        template_name = 'cashflow/home.html'
        balance, inflow_amount, outflow_amount = get_my_current_balance()
    except Exception as exc:
        return HttpResponse(
            exc,
            'Wow, an error was occurred'
        )
    return render(
        request,
        'cashflow/home.html',
        {
            'balance': balance,
            'inflow_amount': inflow_amount,
            'outflow_amount': outflow_amount
        }
    )


@login_required(login_url='/account/sign_in')
def report(request):
    """Generate a report based on range selected by user"""
    try:
        dataset, labels, data_in, data_out, diff = get_my_report(request)
        page = request.GET.get('page', 1)
        paginator = Paginator(dataset, 5)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    return render(
        request,
        'cashflow/report.html',
        {
            'dataset': dataset,
            'labels': labels,
            'data_in': data_in,
            'data_out': data_out,
            'diff': diff
        }
    )
