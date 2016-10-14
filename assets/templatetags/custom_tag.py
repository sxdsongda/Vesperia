#!usr/bin/env python
# coding:utf-8

from django import template

register = template.Library()


@register.filter
def sum_size(query_set):
    total_val = sum([i.capacity if i.capacity else 0 for i in query_set])
    return total_val


def list_count(query_set):
    count = sum()