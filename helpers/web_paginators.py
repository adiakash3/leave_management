from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_fun_pagiantion(request, queryset, queryset_name='queryset'):
    """
    helper function to get the pagination
    """
    count = queryset.count
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
    
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    index = queryset.number - 1
    # This value is maximum index of pages, so the last page - 1
    max_index = len(paginator.page_range)
    # range of 7, calculate where to slice the list
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 4 if index <= max_index - 4 else max_index
    # new page range
    page_range = paginator.page_range[start_index:end_index]

    # showing first and last links in pagination
    if index >= 4:
        start_index = 4
    if end_index - index >= 1 and end_index != max_index:
        end_index = max_index
    else:
        end_index = max_index
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    
    context = {}
    context['count'] = count
    context[queryset_name] = queryset
    context['page_range'] = page_range
    context['start_index'] = start_index
    context['end_index'] = end_index
    context['parameters'] = parameters
    return context