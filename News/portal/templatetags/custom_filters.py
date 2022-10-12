from django import template

register = template.Library()


@register.filter(name='censor')
def censor(values):
    values_list = values.lower().split()
    values = values.split()
    bad_words = ['хуй', 'пизда', 'ебать', 'блять', 'пиздец', 'нахуй']
    for i in range(len(values_list) - 1):
        if values_list[i] in bad_words:
            values[i] = '*' * len(values[i])
    return ' '.join(values)
