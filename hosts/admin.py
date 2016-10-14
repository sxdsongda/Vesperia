from django.contrib import admin
from .models import Host, HostUser, HostGroup, BindHostToHostUser, IDC, TaskLog, TaskLogDetail
# Register your models here.


class HostAdmin(admin.ModelAdmin):
    search_fields = ('hostname', 'ip_addr')
    list_display = ('hostname', 'ip_addr', 'idc', 'port', 'system_type', 'enabled')
    list_filter = ('idc', 'system_type')


class HostGroupAdmin(admin.ModelAdmin):
    # inlines = [
    #     HostMembershipInline,
    # ]
    # exclude = ('hosts',)
    filter_horizontal = ('bound_hosts', 'staffs')


admin.site.register(Host, HostAdmin)
admin.site.register(IDC)
admin.site.register(TaskLog)
admin.site.register(TaskLogDetail)
admin.site.register(HostGroup, HostGroupAdmin)
admin.site.register(HostUser)
admin.site.register(BindHostToHostUser)