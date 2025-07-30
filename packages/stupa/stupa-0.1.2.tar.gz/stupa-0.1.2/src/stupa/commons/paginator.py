import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from typing import TypedDict


class PaginationData(TypedDict):
    count: int
    has_previous: bool
    has_next: bool


def paginator(model_queryset_object, response, page, limit) -> PaginationData:
    # Pagination
    paginator = Paginator(model_queryset_object,
                          limit)

    try:
        model_queryset_object = paginator.page(page)
    except PageNotAnInteger as error:
        logging.exception("Page is not an integer, received %s", error)
        model_queryset_object = paginator.page(1)
    except EmptyPage as error:
        logging.exception("Page not found, %s", error)
        model_queryset_object = paginator.page(paginator.num_pages)

    count = paginator.count
    has_previous = None if not model_queryset_object.has_previous(
    ) else model_queryset_object.previous_page_number()
    has_next = None if not model_queryset_object.has_next(
    ) else model_queryset_object.next_page_number()

    # Add details to response
    response["count"] = count
    response["has_previous"] = has_previous
    response["has_next"] = has_next

    response: PaginationData = response

    return response
