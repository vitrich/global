from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from .models import Task, News

@plugin_pool.register_plugin
class TaskPlugin(CMSPluginBase):
    model = Task  # используем вашу модель Task
    render_template = "grade5/task_plugin.html"
    name = _("Задача по биологии")

@plugin_pool.register_plugin
class NewsPlugin(CMSPluginBase):
    model = News
    render_template = "grade5/news_plugin.html"
    name = _("Новость класса")
