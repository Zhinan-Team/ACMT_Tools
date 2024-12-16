from django.urls import path
from rest_framework import routers


from dvadmin.system.views.clause import PrivacyView, TermsServiceView
from dvadmin.system.views.login_log import LoginLogViewSet
from dvadmin.system.views.menu import MenuViewSet
from dvadmin.system.views.menu_button import MenuButtonViewSet
from dvadmin.system.views.operation_log import OperationLogViewSet
from dvadmin.system.views.role import RoleViewSet
from dvadmin.system.views.role_menu import RoleMenuPermissionViewSet
from dvadmin.system.views.role_menu_button_permission import RoleMenuButtonPermissionViewSet
from dvadmin.system.views.system_config import SystemConfigViewSet
from dvadmin.system.views.user import UserViewSet
from dvadmin.system.views.menu_field import MenuFieldViewSet
from dvadmin.system.views.parameter import ParameterViewSet
from dvadmin.system.views.derived_parameter import DerivedParameterViewSet
from dvadmin.system.views.parameter_distinct import ParameterDistinctViewSet
from dvadmin.system.views.acars import AcarsViewSet
from dvadmin.system.views.rule import RuleViewSet
from dvadmin.system.views.task import TaskViewSet
from dvadmin.system.views.ruletotask import RuletoTaskViewSet

from dvadmin.system.views.project import ProjectViewSet

system_url = routers.SimpleRouter()
system_url.register(r'menu', MenuViewSet)
system_url.register(r'menu_button', MenuButtonViewSet)
system_url.register(r'role', RoleViewSet)
system_url.register(r'user', UserViewSet) 
system_url.register(r'operation_log', OperationLogViewSet)

system_url.register(r'system_config', SystemConfigViewSet)
system_url.register(r'role_menu_button_permission', RoleMenuButtonPermissionViewSet)
system_url.register(r'role_menu_permission', RoleMenuPermissionViewSet)
system_url.register(r'column', MenuFieldViewSet)
system_url.register(r'parameter', ParameterViewSet)
system_url.register(r'derived_parameter', DerivedParameterViewSet)
system_url.register(r'parameter_distinct', ParameterDistinctViewSet)
system_url.register(r'acars', AcarsViewSet)
system_url.register(r'rule', RuleViewSet)
system_url.register(r'task', TaskViewSet)
system_url.register(r'ruletotask', RuletoTaskViewSet)
system_url.register(r'project', ProjectViewSet)

urlpatterns = [
    path('user/export/', UserViewSet.as_view({'post': 'export_data', })),
    path('user/import/', UserViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('system_config/save_content/', SystemConfigViewSet.as_view({'put': 'save_content'})),
    path('system_config/get_association_table/', SystemConfigViewSet.as_view({'get': 'get_association_table'})),
    path('system_config/get_table_data/<int:pk>/', SystemConfigViewSet.as_view({'get': 'get_table_data'})),
    path('system_config/get_relation_info/', SystemConfigViewSet.as_view({'get': 'get_relation_info'})),
    path('login_log/', LoginLogViewSet.as_view({'get': 'list'})),
    path('login_log/<int:pk>/', LoginLogViewSet.as_view({'get': 'retrieve'})),
    path('clause/privacy.html', PrivacyView.as_view()),
    path('clause/terms_service.html', TermsServiceView.as_view()),
]
urlpatterns += system_url.urls
