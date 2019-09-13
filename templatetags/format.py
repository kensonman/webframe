from django import template
register=template.Library()

@register.filter
def format(value, fmt='{}'):
   '''
   Format the variable according to [Python3 String Formatting](https://docs.python.org/3/library/string.html#string-formatting) syntax.

   USAGE
   =====

   Given variable pi=3.141516:
      pi|format:'{0:0.2f}'     => 3.14
      pi|format:'{:0.3f}'      => 3.142
      pi|format:'{:06.2f}'     => 003.14

   Giving variable val={'key': 'name', 'value': 'Hello world!'}
      val|format:'{key}=={value}'         => name==Hello world!
      val|format:'{key:10s}=={value}'     => name      ==Hello world!
      val|format:'{key:>10s}=={value}'    =>       name==Hello world!

   Giving variable dt=new DateTime(year=2019, month=5, day=12, hour=11, minute=46)
      val|format:'{%Y-%m-%d %H:%M}'       => 2019-05-12 11:46
   '''
   try:
      if isinstance(value, dict):
         return fmt.format(**value)
      return fmt.format(value)
   except:
      return 'Value[{0}]::{1} cannot format by pattern: {2}'.format(value, type(value).__name__, fmt)
