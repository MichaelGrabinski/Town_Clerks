from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.fields import Field
from django.urls import reverse
from .models import VetRecord, TransmitelReport, Vet, Marriagelicense, Transactions, Deaths, ActivityLog
import pandas as pd
import json
from django.utils import timezone


def _model_field_names(model_cls):
    """Return concrete (db-backed) field names for a model, excluding reverse/M2M."""
    names = []
    for f in model_cls._meta.get_fields():
        if not isinstance(f, Field):
            continue
        if getattr(f, 'many_to_many', False):
            continue
        if getattr(f, 'one_to_many', False):
            continue
        if getattr(f, 'auto_created', False) and not f.concrete:
            continue
        if not getattr(f, 'concrete', False):
            continue
        names.append(f.name)
    return names


def _apply_generic_search(qs, q, field_names):
    if not q:
        return qs
    # Avoid giant ORs; keep it reasonable.
    max_fields = 12
    fields = field_names[:max_fields]
    cond = Q()
    for name in fields:
        cond |= Q(**{f"{name}__icontains": q})
    return qs.filter(cond)


def _raw_list(request, *, title, model_cls, db_alias, default_order, back_url=None, fields=None, page_size=100):
    q = (request.GET.get('q') or '').strip()
    sort = (request.GET.get('sort') or '').strip()
    page_num = request.GET.get('page')

    if fields is None:
        fields = _model_field_names(model_cls)

    # Sorting: only allow known fields.
    allowed = set(fields)
    order_by = default_order
    if sort:
        key = sort[1:] if sort.startswith('-') else sort
        if key in allowed:
            order_by = sort

    qs = model_cls.objects.all().using(db_alias)
    qs = _apply_generic_search(qs, q, fields)
    qs = qs.order_by(order_by)

    paginator = Paginator(qs.values(*fields), page_size)
    page = paginator.get_page(page_num)

    # Build clerk-friendly labels.
    label_map = {}
    for f in model_cls._meta.get_fields():
        if hasattr(f, 'name'):
            try:
                label_map[f.name] = str(getattr(f, 'verbose_name', f.name)).replace('_', ' ').title()
            except Exception:
                label_map[f.name] = f.name.replace('_', ' ').title()

    columns = [{'key': f, 'label': label_map.get(f, f.replace('_', ' ').title()), 'sort_key': f} for f in fields]

    return render(request, 'raw_list.html', {
        'title': title,
        'columns': columns,
        'page': page,
        'q': q,
        'sort': sort,
        'back_url': back_url,
    })


def _record_detail(request, *, title, model_cls, db_alias, pk, back_url=None, fields=None):
    if fields is None:
        fields = _model_field_names(model_cls)

    allowed = set(fields)
    if not model_cls._meta.pk.name in allowed:
        fields = [model_cls._meta.pk.name] + fields

    row = (
        model_cls.objects.using(db_alias)
        .filter(pk=pk)
        .values(*fields)
        .first()
    )
    if not row:
        return HttpResponseBadRequest('Not found')

    # Labels
    label_map = {}
    for f in model_cls._meta.get_fields():
        if hasattr(f, 'name'):
            try:
                label_map[f.name] = str(getattr(f, 'verbose_name', f.name)).replace('_', ' ').title()
            except Exception:
                label_map[f.name] = f.name.replace('_', ' ').title()

    columns = [{'key': f, 'label': label_map.get(f, f.replace('_', ' ').title())} for f in fields]

    return render(request, 'record_detail.html', {
        'title': title,
        'columns': columns,
        'row': row,
        'back_url': back_url,
    'now': timezone.now(),
    })


def hub(request):
    # We will build links for all main sections
    options = [
    {'name': 'Transmitel / Financials', 'url': 'clerks:transmitel_list', 'raw_url': 'clerks:transmitel_raw', 'icon': '💰'},
    {'name': 'Veterans Data', 'url': 'clerks:vet_list', 'raw_url': 'clerks:vets_raw', 'icon': '🎖️'},
    {'name': 'Marriage Licenses', 'url': 'clerks:marriage_list', 'raw_url': 'clerks:marriages_raw', 'icon': '💍'},
    {'name': 'Death / Vitals', 'url': 'clerks:vitals_list', 'raw_url': 'clerks:vitals_raw', 'icon': '🕊️'},
        {'name': 'Ingest New Data', 'url': 'clerks:ingest', 'icon': '📥'},
    ]
    return render(request, 'hub.html', {'options': options})


def ingest(request):
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        try:
            if f.name.endswith('.xlsx') or f.name.endswith('.xls'):
                df = pd.read_excel(f)
            else:
                df = pd.read_csv(f)
        except Exception as e:
            return HttpResponseBadRequest(str(e))
        # basic header read
        headers = list(df.columns)
        # store as transmitel for now
        report = TransmitelReport.objects.create(filename=f.name, data=json.loads(df.to_json(orient='records')))
        return redirect('clerks:transmitel_detail', pk=report.id)
    return render(request, 'ingest.html')


def marriage_list(request):
    qs = Marriagelicense.objects.all().using('marriage')

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(groomlastname__icontains=q)
            | Q(groomfirstname__icontains=q)
            | Q(bridelastname__icontains=q)
            | Q(bridefirstname__icontains=q)
            | Q(marriage_id__icontains=q)
        )

    paginator = Paginator(qs.order_by('-dateofmarriage', '-date_issued', '-marriage_id'), 50)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'marriage_list.html', {
        'page': page,
        'q': q,
    })


def vitals_list(request):
    qs = Deaths.objects.all().using('vitals')

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(lastname__icontains=q)
            | Q(first_name__icontains=q)
            | Q(date_of_death__icontains=q)
            | Q(id__icontains=q)
        )

    paginator = Paginator(qs.order_by('-date_of_death', '-id'), 50)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'vitals_list.html', {
        'page': page,
        'q': q,
    })


def transmitel_list(request):
    qs = Transactions.objects.all().using('transmitel')

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(transaction_id__icontains=q)
            | Q(transactionnumber__icontains=q)
            | Q(entered_by__icontains=q)
            | Q(description__icontains=q)
        )

    paginator = Paginator(qs.order_by('-transactiondate', '-transaction_id'), 50)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'transmitel_list.html', {
        'page': page,
        'q': q,
    })


# Updated vet_list to use the REAL Vet model
def vet_list(request):
    qs = Vet.objects.all().using('vets')

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(lname__icontains=q)
            | Q(fname__icontains=q)
            | Q(vet_id__icontains=q)
            | Q(branch__icontains=q)
            | Q(town__icontains=q)
        )

    sort = (request.GET.get('sort') or '').strip()
    sort_map = {
        'lname': 'lname',
        '-lname': '-lname',
        'fname': 'fname',
        '-fname': '-fname',
        'branch': 'branch',
        '-branch': '-branch',
        'discharge_date': 'discharge_date',
        '-discharge_date': '-discharge_date',
        'vet_id': 'vet_id',
        '-vet_id': '-vet_id',
    }
    order_by = sort_map.get(sort, 'lname')

    paginator = Paginator(qs.order_by(order_by, 'fname', 'vet_id'), 100)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'vet_list.html', {
        'page': page,
        'q': q,
        'sort': sort,
    })


def transmitel_detail(request, pk):
    try:
        r = TransmitelReport.objects.get(pk=pk)
    except TransmitelReport.DoesNotExist:
        return HttpResponseBadRequest('Not found')
    return render(request, 'transmitel_detail.html', {'report': r})


def vet_detail(request, pk):
    return _record_detail(
        request,
        title='Vet Record Detail',
        model_cls=Vet,
        db_alias='vets',
        pk=pk,
        back_url=reverse('clerks:vet_list'),
    )


def marriage_detail(request, pk):
    return _record_detail(
        request,
        title='Marriage License Detail',
        model_cls=Marriagelicense,
        db_alias='marriage',
        pk=pk,
        back_url=reverse('clerks:marriage_list'),
    )


def vitals_detail(request, pk):
    return _record_detail(
        request,
        title='Vitals / Death Record Detail',
        model_cls=Deaths,
        db_alias='vitals',
        pk=pk,
        back_url=reverse('clerks:vitals_list'),
    )


def transmitel_tx_detail(request, pk):
    return _record_detail(
        request,
        title='Financial Transaction Detail',
        model_cls=Transactions,
        db_alias='transmitel',
        pk=pk,
        back_url=reverse('clerks:transmitel_list'),
    )


def vets_raw(request):
    return _raw_list(
        request,
        title='Vets (Raw)'
        , model_cls=Vet
        , db_alias='vets'
        , default_order='lname'
        , back_url=reverse('clerks:vet_list')
    )


def marriages_raw(request):
    return _raw_list(
        request,
        title='Marriage Licenses (Raw)'
        , model_cls=Marriagelicense
        , db_alias='marriage'
        , default_order='marriage_id'
        , back_url=reverse('clerks:marriage_list')
    )


def vitals_raw(request):
    return _raw_list(
        request,
        title='Vitals / Deaths (Raw)'
        , model_cls=Deaths
        , db_alias='vitals'
        , default_order='-date_of_death'
        , back_url=reverse('clerks:vitals_list')
    )


def transmitel_raw(request):
    return _raw_list(
        request,
        title='Clerk Transmittal Transactions (Raw)'
        , model_cls=Transactions
        , db_alias='transmitel'
        , default_order='-transactiondate'
        , back_url=reverse('clerks:transmitel_list')
    )


def activity_list(request):
    """Read-only activity log for non-admin users."""

    qs = ActivityLog.objects.all()

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(username__icontains=q)
            | Q(event_type__icontains=q)
            | Q(path__icontains=q)
            | Q(method__icontains=q)
            | Q(ip_address__icontains=q)
            | Q(action__icontains=q)
        )

    event_type = (request.GET.get('event_type') or '').strip()
    if event_type:
        qs = qs.filter(event_type=event_type)

    paginator = Paginator(qs, 100)
    page = paginator.get_page(request.GET.get('page'))

    event_types = ActivityLog.objects.order_by().values_list('event_type', flat=True).distinct()

    return render(request, 'activity_list.html', {
        'page': page,
        'q': q,
        'event_type': event_type,
        'event_types': event_types,
    })
