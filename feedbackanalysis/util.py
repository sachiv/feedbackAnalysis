from random import randint
import csv
from django.http import HttpResponse
from django import template
import random, string
from django.utils.http import urlquote  as django_urlquote
from django.utils.http import urlencode as django_urlencode
from django.utils.datastructures import MultiValueDict
from datetime import timedelta
import calendar
import json
from rest_framework.authtoken.models import Token
from django.contrib.admin import site
import adminactions.actions as actions
from django.core.exceptions import PermissionDenied
from django.contrib.admin.utils import label_for_field


def generate_pin():
    range_start = 10**(4-1)
    range_end = (10**4)-1
    return randint(range_start, range_end)

register = template.Library()


@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    value = unicode(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Break into words and remove the last
    words = value.split(' ')[:-1]

    # Join the words and return
    return ' '.join(words) + '...'


def export_as_csv_action(description="Download selected rows as CSV file",header=True):
    """
    This function returns an export csv action
    This function ONLY downloads the columns shown in the list_display of the admin
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/ and /2020/
        """
        # TODO Also create export_as_csv for exporting all columns including list_display
        if not request.user.is_staff:
            raise PermissionDenied
        opts = modeladmin.model._meta
        field_names = modeladmin.list_display
        if 'action_checkbox' in field_names:
            field_names.remove('action_checkbox')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            headers = []
            for field_name in list(field_names):
                label = label_for_field(field_name,modeladmin.model,modeladmin)
                label = str(label)
                if str.islower(label):
                   label = str.title(label)
                headers.append(label)
            writer.writerow(headers)
        for row in queryset:
            values = []
            for field in field_names:
                value = (getattr(row, field))
                if callable(value):
                    try:
                        value = value() or ''
                    except:
                        value = 'Error retrieving value'
                if value is None:
                    value = ''
                values.append(unicode(value).encode('utf-8'))
            writer.writerow(values)
        return response
    export_as_csv.short_description = description
    return export_as_csv


def generate_smart_id(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def urlquote(link=None, get={}):
    """
    This method does both: urlquote() and urlencode()

    urlqoute(): Quote special characters in 'link'

    urlencode(): Map dictionary to query string key=value&...

    HTML escaping is not done.

    Example:

      urlquote('/wiki/Python_(programming_language)')     --> '/wiki/Python_%28programming_language%29'
      urlquote('/mypath/', {'key': 'value'})              --> '/mypath/?key=value'
      urlquote('/mypath/', {'key': ['value1', 'value2']}) --> '/mypath/?key=value1&key=value2'
      urlquote({'key': ['value1', 'value2']})             --> 'key=value1&key=value2'
    """
    assert link or get
    if isinstance(link, dict):
        # urlqoute({'key': 'value', 'key2': 'value2'}) --> key=value&key2=value2
        assert not get, get
        get = link
        link = ''
    assert isinstance(get, dict), 'wrong type "%s", dict required' % type(get)
    assert not (link.startswith('http://') or link.startswith('https://')), \
        'This method should only quote the url path. It should not start with http(s)://  (%s)' % (
        link)
    if get:
        # http://code.djangoproject.com/ticket/9089
        if isinstance(get, MultiValueDict):
            get=get.lists()
        if link:
            link='%s?' % django_urlquote(link)
        return u'%s%s' % (link, django_urlencode(get, doseq=True))
    else:
        return django_urlquote(link)


def get_month_day_range(date):
    """
    For a date 'date' returns the start and end date for the month of 'date'.

    Month with 31 days:
    date = datetime.date(2011, 7, 27)
    get_month_day_range(date)
    (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))

    Month with 28 days:
    date = datetime.date(2011, 2, 15)
    get_month_day_range(date)
    (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
    """
    first_day = date.replace(day=1)
    last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day, last_day


def get_year_day_range(date):
    first_day = date.replace(day=1, month=1)
    last_day = date.replace(day=31, month=12)
    return first_day, last_day


def get_week_day_range(date):
    first_day = date - timedelta(days=date.weekday())
    last_day = first_day + timedelta(days=6)
    return first_day, last_day


# Auth token check
def json_response(response_dict, status=200):
    response = HttpResponse(json.dumps(response_dict), content_type="application/json", status=status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


def token_required(func):
    def inner(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return func(request, *args, **kwargs)
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header is not None:
            tokens = auth_header.split(' ')
            if len(tokens) == 2 and tokens[0] == 'Token':
                token = tokens[1]
                try:
                    request.token = Token.objects.get(key=token)
                    return func(request, *args, **kwargs)
                except Token.DoesNotExist:
                    return json_response({
                        'error': 'Token not found'
                    }, status=401)
        return json_response({
            'error': 'Invalid Header'
        }, status=401)

    return inner

# register all adminactions
actions.add_to_site(site)
