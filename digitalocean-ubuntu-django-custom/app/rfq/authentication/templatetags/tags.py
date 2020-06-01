from django.template import Library

register = Library()

def sub(value, arg):
	return value-arg

def multiply(value, arg):
	return value*arg

def divide(value, arg):
	return value/arg

def friendly(value):
	value = str(value)
	ret=''
	ret=' '.join([s[0].upper() + s[1:] for s in value.split('_')]);
	return ret

register.filter(sub)
register.filter(multiply)
register.filter(divide)
register.filter(friendly)