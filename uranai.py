import re


def safe_int(c):
    if '0' <= c <= '9':
        return int(c)
    return 0


def soul_number(s):
    n = sum(safe_int(c) for c in str(s))
    if n % 11 == 0 and n < 10:
        return n
    return soul_number(str(n))


def ask_birthday(msg='生年月日は？'):
    date = input(msg)
    matched = re.findall(r'(\d\d\d\d)年|/|-(\d?\d)月|/|-(\d?\d)日?', date)
    if len(matched) > 0:
        year, month, day = matched[0]
        return year+month+day
    matched = re.findall(r'(\d?\d)月|/|-(\d?\d)日?', date)
    if len(matched) > 0:
        month, day = matched[0]
        return ask_birthyear()+month+day
    if not date.isdigit():
        raise RuntimeError('wrong format')
    return date


def ask_birthyear(msg='何年生まれ？'):
    year = input(msg)
    if not year.isdigit():
        raise RuntimeError('wrong format')
    return year


# ask_birthday()
