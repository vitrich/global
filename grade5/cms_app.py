# grade5/cms_app.py
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

@apphook_pool.register
class Grade5Apphook(CMSApp):
    app_name = "grade5"
    name = "5 класс"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["grade5.urls"]
