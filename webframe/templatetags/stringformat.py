from django import template
register=template.Library()

@register.filter
def format(value, fmt='{}'):
   '''
   @Deprecated Use format instead
   Format the string according to [Python String Formatting](https://docs.python.org/3/library/string.html#string-formatting) syntax.

   USAGE
   =====

   Given variable pi=3.141516:
      pi|stringformat:'{0:0.2f}'     => 3.14
      pi|stringformat:'{:0.3f}'      => 3.142
      pi|stringformat:'{:06.2f}'     => 003.14

   Giving variable val={'key': 'name', 'value': 'Hello world!'}
      val|stringformat:'{key}=={value}'         => name==Hello world!
      val|stringformat:'{key:10s}=={value}'     => name      ==Hello world!
      val|stringformat:'{key:>10s}=={value}'    =>       name==Hello world!

   Giving variable dt=new DateTime(year=2019, month=5, day=12, hour=11, minute=46)
      val|stringformat:'{%Y-%m-%d %H:%M}'       => 2019-05-12 11:46
   '''
   try:
      if isinstance(value, dict):
         return fmt.format(**value)
      return fmt.format(value)
   except:
      return 'Value[%s]::%s cannot format by pattern: %s'%(value, type(value).__name__, fmt)

@register.filter
def stringformat(value, fmt='{}'):
   '''
   @Deprecated Use format instead
   '''
   return format(value, fmt)
