import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from dvadmin.utils.models import CoreModel, table_prefix, get_custom_app_models


class Role(CoreModel):
    name = models.CharField(max_length=64, verbose_name="角色名称", help_text="角色名称")
    key = models.CharField(max_length=64, unique=True, verbose_name="权限字符", help_text="权限字符")
    sort = models.IntegerField(default=1, verbose_name="角色顺序", help_text="角色顺序")
    status = models.BooleanField(default=True, verbose_name="角色状态", help_text="角色状态")

    class Meta:
        db_table = table_prefix + "system_role"
        verbose_name = "角色表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class CustomUserManager(UserManager):

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = super(CustomUserManager, self).create_superuser(username, email, password, **extra_fields)
        user.set_password(password)
        try:
            user.role.add(Role.objects.get(name="管理员"))
            user.save(using=self._db)
            return user
        except ObjectDoesNotExist:
            user.delete()
            raise ValidationError("角色`管理员`不存在, 创建失败, 请先执行python manage.py init")


from django.db import models
from django.contrib.auth.models import AbstractUser
import hashlib

class Users(CoreModel, AbstractUser):
    username = models.CharField(max_length=150, unique=True, db_index=True, verbose_name="用户账号",
                                help_text="用户账号")
    email = models.EmailField(max_length=255, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.CharField(max_length=255, verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    
    GENDER_CHOICES = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )
    gender = models.IntegerField(
        choices=GENDER_CHOICES, default=0, verbose_name="性别", null=True, blank=True, help_text="性别"
    )
    
    USER_TYPE = (
        (0, "后台用户"),
        (1, "前台用户"),
    )
    user_type = models.IntegerField(
        choices=USER_TYPE, default=0, verbose_name="用户类型", null=True, blank=True, help_text="用户类型"
    )
    
    role = models.ManyToManyField(to="Role", blank=True, verbose_name="关联角色", db_constraint=False,
                                   help_text="关联角色")
    # # 修改 project 字段为 ForeignKey 类型
    # project = models.ForeignKey(to="Project", blank=True, null=True, on_delete=models.SET_NULL, 
    #                              related_name='users', verbose_name="关联项目", help_text="关联项目")
    
    login_error_count = models.IntegerField(default=0, verbose_name="登录错误次数", help_text="登录错误次数")
    objects = CustomUserManager()

    def set_password(self, raw_password):
        super().set_password(hashlib.md5(raw_password.encode(encoding="UTF-8")).hexdigest())

    class Meta:
        db_table = table_prefix + "system_users"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

class Menu(CoreModel):
    parent = models.ForeignKey(
        to="Menu",
        on_delete=models.CASCADE,
        verbose_name="上级菜单",
        null=True,
        blank=True,
        db_constraint=False,
        help_text="上级菜单",
    )
    icon = models.CharField(max_length=64, verbose_name="菜单图标", null=True, blank=True, help_text="菜单图标")
    name = models.CharField(max_length=64, verbose_name="菜单名称", help_text="菜单名称")
    sort = models.IntegerField(default=1, verbose_name="显示排序", null=True, blank=True, help_text="显示排序")
    ISLINK_CHOICES = (
        (0, "否"),
        (1, "是"),
    )
    is_link = models.BooleanField(default=False, verbose_name="是否外链", help_text="是否外链")
    link_url = models.CharField(max_length=255, verbose_name="链接地址", null=True, blank=True, help_text="链接地址")
    is_catalog = models.BooleanField(default=False, verbose_name="是否目录", help_text="是否目录")
    web_path = models.CharField(max_length=128, verbose_name="路由地址", null=True, blank=True, help_text="路由地址")
    component = models.CharField(max_length=128, verbose_name="组件地址", null=True, blank=True, help_text="组件地址")
    component_name = models.CharField(max_length=50, verbose_name="组件名称", null=True, blank=True,
                                      help_text="组件名称")
    status = models.BooleanField(default=True, blank=True, verbose_name="菜单状态", help_text="菜单状态")
    cache = models.BooleanField(default=False, blank=True, verbose_name="是否页面缓存", help_text="是否页面缓存")
    visible = models.BooleanField(default=True, blank=True, verbose_name="侧边栏中是否显示",
                                  help_text="侧边栏中是否显示")
    is_iframe = models.BooleanField(default=False, blank=True, verbose_name="框架外显示", help_text="框架外显示")
    is_affix = models.BooleanField(default=False, blank=True, verbose_name="是否固定", help_text="是否固定")

    @classmethod
    def get_all_parent(cls, id: int, all_list=None, nodes=None):
        """
        递归获取给定ID的所有层级
        :param id: 参数ID
        :param all_list: 所有列表
        :param nodes: 递归列表
        :return: nodes
        """
        if not all_list:
            all_list = Menu.objects.values("id", "name", "parent")
        if nodes is None:
            nodes = []
        for ele in all_list:
            if ele.get("id") == id:
                parent_id = ele.get("parent")
                if parent_id is not None:
                    cls.get_all_parent(parent_id, all_list, nodes)
                nodes.append(ele)
        return nodes
    class Meta:
        db_table = table_prefix + "system_menu"
        verbose_name = "菜单表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)

class MenuField(CoreModel):
    model = models.CharField(max_length=64, verbose_name='表名')
    menu = models.ForeignKey(to='Menu', on_delete=models.CASCADE, verbose_name='菜单', db_constraint=False)
    field_name = models.CharField(max_length=64, verbose_name='模型表字段名')
    title = models.CharField(max_length=64, verbose_name='字段显示名')
    class Meta:
        db_table = table_prefix + "system_menu_field"
        verbose_name = "菜单字段表"
        verbose_name_plural = verbose_name
        ordering = ("id",)

class FieldPermission(CoreModel):
    role = models.ForeignKey(to='Role', on_delete=models.CASCADE, verbose_name='角色', db_constraint=False)
    field = models.ForeignKey(to='MenuField', on_delete=models.CASCADE,related_name='menu_field', verbose_name='字段', db_constraint=False)
    is_query = models.BooleanField(default=1, verbose_name='是否可查询')
    is_create = models.BooleanField(default=1, verbose_name='是否可创建')
    is_update = models.BooleanField(default=1, verbose_name='是否可更新')

    class Meta:
        db_table = table_prefix + "system_field_permission"
        verbose_name = "字段权限表"
        verbose_name_plural = verbose_name
        ordering = ("id",)


class MenuButton(CoreModel):
    menu = models.ForeignKey(
        to="Menu",
        db_constraint=False,
        related_name="menuPermission",
        on_delete=models.CASCADE,
        verbose_name="关联菜单",
        help_text="关联菜单",
    )
    name = models.CharField(max_length=64, verbose_name="名称", help_text="名称")
    value = models.CharField(unique=True, max_length=64, verbose_name="权限值", help_text="权限值")
    api = models.CharField(max_length=200, verbose_name="接口地址", help_text="接口地址")
    METHOD_CHOICES = (
        (0, "GET"),
        (1, "POST"),
        (2, "PUT"),
        (3, "DELETE"),
    )
    method = models.IntegerField(default=0, verbose_name="接口请求方法", null=True, blank=True,
                                 help_text="接口请求方法")

    class Meta:
        db_table = table_prefix + "system_menu_button"
        verbose_name = "菜单权限表"
        verbose_name_plural = verbose_name
        ordering = ("-name",)


class RoleMenuPermission(CoreModel):
    role = models.ForeignKey(
        to="Role",
        db_constraint=False,
        related_name="role_menu",
        on_delete=models.CASCADE,
        verbose_name="关联角色",
        help_text="关联角色",
    )
    menu = models.ForeignKey(
        to="Menu",
        db_constraint=False,
        related_name="role_menu",
        on_delete=models.CASCADE,
        verbose_name="关联菜单",
        help_text="关联菜单",
    )

    class Meta:
        db_table = table_prefix + "role_menu_permission"
        verbose_name = "角色菜单权限表"
        verbose_name_plural = verbose_name
        # ordering = ("-create_datetime",)


class RoleMenuButtonPermission(CoreModel):
    role = models.ForeignKey(
        to="Role",
        db_constraint=False,
        related_name="role_menu_button",
        on_delete=models.CASCADE,
        verbose_name="关联角色",
        help_text="关联角色",
    )
    menu_button = models.ForeignKey(
        to="MenuButton",
        db_constraint=False,
        related_name="menu_button_permission",
        on_delete=models.CASCADE,
        verbose_name="关联菜单按钮",
        help_text="关联菜单按钮",
        null=True,
        blank=True
    )
    DATASCOPE_CHOICES = (
        (0, "仅本人数据权限"),
        (1, "本部门及以下数据权限"),
        (2, "本部门数据权限"),
        (3, "全部数据权限"),
        (4, "自定数据权限"),
    )
    data_range = models.IntegerField(default=0, choices=DATASCOPE_CHOICES, verbose_name="数据权限范围",
                                     help_text="数据权限范围")

    class Meta:
        db_table = table_prefix + "role_menu_button_permission"
        verbose_name = "角色按钮权限表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)



class OperationLog(CoreModel):
    request_modular = models.CharField(max_length=64, verbose_name="请求模块", null=True, blank=True,
                                       help_text="请求模块")
    request_path = models.CharField(max_length=400, verbose_name="请求地址", null=True, blank=True,
                                    help_text="请求地址")
    request_body = models.TextField(verbose_name="请求参数", null=True, blank=True, help_text="请求参数")
    request_method = models.CharField(max_length=8, verbose_name="请求方式", null=True, blank=True,
                                      help_text="请求方式")
    request_msg = models.TextField(verbose_name="操作说明", null=True, blank=True, help_text="操作说明")
    request_ip = models.CharField(max_length=32, verbose_name="请求ip地址", null=True, blank=True,
                                  help_text="请求ip地址")
    request_browser = models.CharField(max_length=64, verbose_name="请求浏览器", null=True, blank=True,
                                       help_text="请求浏览器")
    response_code = models.CharField(max_length=32, verbose_name="响应状态码", null=True, blank=True,
                                     help_text="响应状态码")
    request_os = models.CharField(max_length=64, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    json_result = models.TextField(verbose_name="返回信息", null=True, blank=True, help_text="返回信息")
    status = models.BooleanField(default=False, verbose_name="响应状态", help_text="响应状态")

    class Meta:
        db_table = table_prefix + "system_operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


def media_file_name(instance, filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    return os.path.join("files", h[:1], h[1:2], h + ext.lower())


class SystemConfig(CoreModel):
    parent = models.ForeignKey(
        to="self",
        verbose_name="父级",
        on_delete=models.CASCADE,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="父级",
    )
    title = models.CharField(max_length=50, verbose_name="标题", help_text="标题")
    key = models.CharField(max_length=100, verbose_name="键", help_text="键", db_index=True)
    value = models.JSONField(max_length=100, verbose_name="值", help_text="值", null=True, blank=True)
    sort = models.IntegerField(default=0, verbose_name="排序", help_text="排序", blank=True)
    status = models.BooleanField(default=True, verbose_name="启用状态", help_text="启用状态")
    data_options = models.JSONField(verbose_name="数据options", help_text="数据options", null=True, blank=True)
    FORM_ITEM_TYPE_LIST = (
        (0, "text"),
        (1, "datetime"),
        (2, "date"),
        (3, "textarea"),
        (4, "select"),
        (5, "checkbox"),
        (6, "radio"),
        (7, "img"),
        (8, "file"),
        (9, "switch"),
        (10, "number"),
        (11, "array"),
        (12, "imgs"),
        (13, "foreignkey"),
        (14, "manytomany"),
        (15, "time"),
    )
    form_item_type = models.IntegerField(
        choices=FORM_ITEM_TYPE_LIST, verbose_name="表单类型", help_text="表单类型", default=0, blank=True
    )
    rule = models.JSONField(null=True, blank=True, verbose_name="校验规则", help_text="校验规则")
    placeholder = models.CharField(max_length=50, null=True, blank=True, verbose_name="提示信息", help_text="提示信息")
    setting = models.JSONField(null=True, blank=True, verbose_name="配置", help_text="配置")

    class Meta:
        db_table = table_prefix + "system_config"
        verbose_name = "系统配置表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)
        unique_together = (("key", "parent_id"),)

    def __str__(self):
        return f"{self.title}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        dispatch.refresh_system_config()  # 有更新则刷新系统配置

    def delete(self, using=None, keep_parents=False):
        res = super().delete(using, keep_parents)
        dispatch.refresh_system_config()
        return res


class LoginLog(CoreModel):
    LOGIN_TYPE_CHOICES = ((1, "普通登录"), (2, "微信扫码登录"),)
    username = models.CharField(max_length=32, verbose_name="登录用户名", null=True, blank=True, help_text="登录用户名")
    ip = models.CharField(max_length=32, verbose_name="登录ip", null=True, blank=True, help_text="登录ip")
    agent = models.TextField(verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名")
    os = models.CharField(max_length=200, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    continent = models.CharField(max_length=50, verbose_name="州", null=True, blank=True, help_text="州")
    country = models.CharField(max_length=50, verbose_name="国家", null=True, blank=True, help_text="国家")
    province = models.CharField(max_length=50, verbose_name="省份", null=True, blank=True, help_text="省份")
    city = models.CharField(max_length=50, verbose_name="城市", null=True, blank=True, help_text="城市")
    district = models.CharField(max_length=50, verbose_name="县区", null=True, blank=True, help_text="县区")
    isp = models.CharField(max_length=50, verbose_name="运营商", null=True, blank=True, help_text="运营商")
    area_code = models.CharField(max_length=50, verbose_name="区域代码", null=True, blank=True, help_text="区域代码")
    country_english = models.CharField(max_length=50, verbose_name="英文全称", null=True, blank=True,
                                       help_text="英文全称")
    country_code = models.CharField(max_length=50, verbose_name="简称", null=True, blank=True, help_text="简称")
    longitude = models.CharField(max_length=50, verbose_name="经度", null=True, blank=True, help_text="经度")
    latitude = models.CharField(max_length=50, verbose_name="纬度", null=True, blank=True, help_text="纬度")
    login_type = models.IntegerField(default=1, choices=LOGIN_TYPE_CHOICES, verbose_name="登录类型",
                                     help_text="登录类型")

    class Meta:
        db_table = table_prefix + "system_login_log"
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Parameter(models.Model):
    #id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=255, blank=True, null=True)
    guid = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    acquired = models.IntegerField(blank=True, null=True)
    sample_frame = models.CharField(max_length=255, blank=True, null=True)
    sample_rate = models.CharField(max_length=255, blank=True, null=True)
    updated_timeout = models.IntegerField(blank=True, null=True)
    record_rate = models.CharField(max_length=255, blank=True, null=True)
    recording_data_group = models.CharField(max_length=255, blank=True, null=True)
    global_guid = models.CharField(max_length=255, blank=True, null=True)
    scale_factor = models.IntegerField(blank=True, null=True)
    one_state = models.CharField(max_length=255, blank=True, null=True)
    full_scale_rng_min = models.IntegerField(blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    transmission_interval_minimum = models.IntegerField(blank=True, null=True)
    zero_state = models.CharField(max_length=255, blank=True, null=True)
    min = models.IntegerField(blank=True, null=True)
    number_of_bits = models.IntegerField(blank=True, null=True)
    max = models.IntegerField(blank=True, null=True)
    encoding = models.CharField(max_length=255, blank=True, null=True)
    lsb_res = models.IntegerField(blank=True, null=True)
    word_in_message = models.IntegerField(blank=True, null=True)
    full_scale_rng_max = models.IntegerField(blank=True, null=True)
    units = models.CharField(max_length=255, blank=True, null=True)
    coded_set = models.TextField(blank=True, null=True)
    published_latency = models.IntegerField(blank=True, null=True)
    ATA = models.CharField(max_length=255, blank=True, null=True)
    
    project = models.ForeignKey(
        to="Project",
        verbose_name="所属项目",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属项目",
    )
    class Meta:
        db_table = table_prefix + "acmt_bus_parameter"
        verbose_name = "Parameter数据"  # 修改为您希望的名称
        verbose_name_plural = "Parameters数据"  # 修改为您希望的名称的复数形式
        managed = False


class ParameterDistinct(models.Model):
    #id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=255, blank=True, null=True)
    guid = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    acquired = models.IntegerField(blank=True, null=True)
    sample_frame = models.CharField(max_length=255, blank=True, null=True)
    sample_rate = models.CharField(max_length=255, blank=True, null=True)
    updated_timeout = models.IntegerField(blank=True, null=True)
    record_rate = models.CharField(max_length=255, blank=True, null=True)
    recording_data_group = models.CharField(max_length=255, blank=True, null=True)
    global_guid = models.CharField(max_length=255, blank=True, null=True)
    scale_factor = models.IntegerField(blank=True, null=True)
    one_state = models.CharField(max_length=255, blank=True, null=True)
    full_scale_rng_min = models.IntegerField(blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    transmission_interval_minimum = models.IntegerField(blank=True, null=True)
    zero_state = models.CharField(max_length=255, blank=True, null=True)
    min = models.IntegerField(blank=True, null=True)
    number_of_bits = models.IntegerField(blank=True, null=True)
    max = models.IntegerField(blank=True, null=True)
    encoding = models.CharField(max_length=255, blank=True, null=True)
    lsb_res = models.IntegerField(blank=True, null=True)
    word_in_message = models.IntegerField(blank=True, null=True)
    full_scale_rng_max = models.IntegerField(blank=True, null=True)
    units = models.CharField(max_length=255, blank=True, null=True)
    coded_set = models.TextField(blank=True, null=True)
    published_latency = models.IntegerField(blank=True, null=True)
    ATA = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = table_prefix + "acmt_bus_parameter_data"
        verbose_name = "Parameter数据唯一"  # 修改为您希望的名称
        verbose_name_plural = "Parameters数据唯一"  # 修改为您希望的名称的复数形式
        managed = False



class DerivedParameter(models.Model):
    parameter_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='参数名称')
    calculation_frame_offset = models.CharField(max_length=255, null=True, blank=True, verbose_name='计算框架偏移')
    calculation_rate = models.CharField(max_length=255, null=True, blank=True, verbose_name='计算率')
    units = models.CharField(max_length=255, null=True, blank=True, verbose_name='单位')
    encoding = models.CharField(max_length=255, null=True, blank=True, verbose_name='编码')
    max = models.CharField(max_length=255, null=True, blank=True, verbose_name='最大值')
    min = models.CharField(max_length=255, null=True, blank=True, verbose_name='最小值')
    number_of_bits = models.IntegerField(null=True, blank=True, verbose_name='位数')
    record_rate = models.CharField(max_length=255, null=True, blank=True, verbose_name='记录比率')
    steady_state_filter = models.CharField(max_length=255, null=True, blank=True, verbose_name='稳态滤波器')
    global_guid = models.CharField(max_length=255, null=True, blank=True, verbose_name='全局GUID')
    guid = models.CharField(max_length=255, null=True, blank=True, verbose_name='GUID')
    value_scaling = models.CharField(max_length=255, null=True, blank=True, verbose_name='值缩放')
    recording_data_group = models.CharField(max_length=255, null=True, blank=True, verbose_name='录制数据组')
    display_values = models.CharField(max_length=255, null=True, blank=True, verbose_name='显示值')
    translate_before = models.CharField(max_length=255, null=True, blank=True, verbose_name='翻译前')
    translate_after = models.CharField(max_length=255, null=True, blank=True, verbose_name='翻译后')

    calculation_standard = models.TextField(null=True, blank=True, verbose_name='standard条件')
    calculation_conditional = models.TextField(null=True, blank=True, verbose_name='conditional条件')

    calculation_reversion = models.TextField(null=True, blank=True, verbose_name='reversion条件')
    calculation_source_selection = models.TextField(null=True, blank=True, verbose_name='source条件')	

    calculation_rolling_average	= models.TextField(null=True, blank=True, verbose_name='rolling条件')
    calculation_valid_average = models.TextField(null=True, blank=True, verbose_name='valid条件')	

    project = models.ForeignKey(
        to="Project",
        verbose_name="所属项目",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属项目",
    )
    class Meta:
        db_table = table_prefix + "acmt_derived_parameter"
        verbose_name = "Parameter衍生数据"
        verbose_name_plural = "Parameter衍生数据"
        managed = False



class Rule(models.Model):
    # id = models.IntegerField(primary_key=True, null=False, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True, default='')
    group_info = models.CharField(max_length=255, null=True, blank=True, default='')
    rate = models.CharField(max_length=255, null=True, blank=True, default='')
    delay = models.IntegerField(null=True, blank=True, default=0)
    trigger = models.CharField(max_length=255, null=True, blank=True, default='')
    init_state = models.CharField(max_length=255, null=True, blank=True, default='')
    state_filter = models.IntegerField(null=True, blank=True, default=0)
    trigger_limit = models.IntegerField(null=True, blank=True, default=0)
    log_limit = models.IntegerField(null=True, blank=True, default=0)
    event_record = models.CharField(max_length=255, null=True, blank=True, default='')
    condition = models.TextField(null=True, blank=True, default='{}')
    task_id = models.TextField(null=True, blank=True, default='')
    guid = models.TextField(null=True, blank=True, default='')
    aircraft_part = models.CharField(max_length=255, null=True, blank=True, default='')

    class Meta:
        db_table = table_prefix + "rule"
        verbose_name = "Rule数据"  # 修改为您希望的名称
        verbose_name_plural = "Rule数据"  # 修改为您希望的名称的复数形式
        managed = False




class RuletoTask(models.Model):
    rulename = models.CharField(max_length=255, null=True, blank=True, default='')
    taskname = models.CharField(max_length=255, null=True, blank=True, default='')

    class Meta:
        db_table = table_prefix + "ruletotask"
        verbose_name = "RuleTask关系"  # 修改为您希望的名称
        verbose_name_plural = "RuleTask关系"  # 修改为您希望的名称的复数形式
        managed = False



class Task(models.Model):
    # id = models.IntegerField(primary_key=True, auto_created=True)
    task_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    task_type = models.CharField(max_length=255, null=True, blank=True, default=None)
    hmu_event_type = models.CharField(max_length=255, null=True,blank=True, default=None)
    execution_limit = models.IntegerField(null=True,blank=True, default=None)
    record_rate = models.CharField(max_length=255, null=True,blank=True, default=None)
    start_time = models.IntegerField(null=True,blank=True, default=None)
    stop_time = models.IntegerField(null=True, blank=True,default=None)
    parameter = models.TextField(null=True,blank=True, default=None)
    fault = models.TextField(null=True, blank=True,default=None)
    acars_report = models.TextField(null=True, default=None, blank=True)
    guid = models.TextField(null=True, blank=True, default=None)
    task_position = models.CharField(max_length=255, null=True,blank=True,  default=None)

    class Meta:
        db_table = table_prefix + "task"
        verbose_name = "Task数据"  # 修改为您希望的名称
        verbose_name_plural = "Task数据"  # 修改为您希望的名称的复数形式
        managed = False


class Project(models.Model):
    # project_id = models.CharField(max_length=255, primary_key=True)  # 主键，不可为null
    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='projects', verbose_name="关联用户")
    name = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    details = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    base_name = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    last_updater = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    last_updated = models.DateTimeField(auto_now=True, null=False)  # 自动更新为当前时间
    owner = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    created = models.DateTimeField(auto_now_add=True, null=False)  # 新建时自动设置
    status = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    LSAP_part_number = models.CharField(max_length=255, null=True, blank=True)  # 允许为空
    aircraft_model_number = models.CharField(max_length=255, null=True, blank=True)  # 允许为空

    class Meta:
        db_table = table_prefix + "project"
        verbose_name = "Project数据"  # 修改为您希望的名称
        verbose_name_plural = "Project数据"  # 修改为您希望的名称的复数形式
        managed = False


class Acars(models.Model):
    name = models.TextField(null=True, blank=True)  # 对应 MySQL 的 text 类型
    enable_report = models.CharField(max_length=255, null=True, blank=True) 
    prefix = models.CharField(max_length=255, null=True, blank=True)  # int 类型
    report_id = models.CharField(max_length=255, null=True, blank=True)   # int 类型
    exceedance_report = models.CharField(max_length=255, null=True, blank=True)   # tinytext 类型
    exceedance_parameter = models.CharField(max_length=255, null=True, blank=True)   # text 类型
    engine_location = models.CharField(max_length=255, null=True, blank=True)  # varchar(255)
    trigger_id = models.CharField(max_length=255, null=True, blank=True)   # int 类型
    header_task = models.CharField(max_length=255, null=True, blank=True)   # text 类型
    record_task = models.CharField(max_length=20000, null=True, blank=True)   # text 类型
    global_guid = models.CharField(max_length=255, null=True, blank=True)   # text 类型

    project = models.ForeignKey(
        to="Project",
        verbose_name="所属项目",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属项目",
    )

    class Meta:
        db_table = table_prefix + "acars"
        verbose_name = "Acars数据"
        verbose_name_plural = "Acars数据"
        managed = False

