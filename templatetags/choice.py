from django import template
register=template.Library()

@register.filter
def choice(value, choices):
   '''
   Get the choice displayable value

   Example Given:

   class Model(models.model):
      STATUS_DRAFT            = 0
      STATUS_PENDDING         = 1
      STATUS_APPROVING        = 2
      STATUS_CONFIRMED        = 3
      STATUS_GOINGON          = 4
      STATUS_COMPELETED       = 5
      STATUS_EXPIRED          = 6
      STATUS_CANCELLED        = 7
      STATUS                  = (
         (STATUS_DRAFT,    'Draft'),
         (STATUS_PENDDING, 'Pendding'),
         (STATUS_APPROVING,'Approving'),
         (STATUS_CONFIRMED,'Confirmed'),
         (STATUS_GOINGON,  'Going On'),
         (STATUS_COMPELETED,'Completed'),
         (STATUS_EXPIRED,  'Expired'),
         (STATUS_CANCELLED,'Cancelled'),
      )

      status                  = models.IntegerField(choices=STATUS, default=STATUS_DRAFT, verbose_name='status field')


      {%load choice%}
      {{target.status|choice:STATUS}} == 'Draft'
   '''
   if type(value)!=int:
      return '"%d" is not a int'%value
   if type(choices)!=tuple:
      return 'no suitable choices provided'
   return choices[value][1]
