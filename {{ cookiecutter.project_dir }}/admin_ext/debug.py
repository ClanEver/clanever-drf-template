from pathlib import Path

from django.template.library import import_library
from django.views import debug

debug.DEBUG_ENGINE.libraries['combine_url'] = 'admin_ext.templatetags.combine_url'
debug.DEBUG_ENGINE.template_libraries['combine_url'] = import_library('admin_ext.templatetags.combine_url')
builtin_template_path_ori = debug.builtin_template_path


def builtin_template_path(name):
    if (path := Path(__file__).parent / 'templates' / name).exists():
        return path
    return builtin_template_path_ori(name)


debug.builtin_template_path = builtin_template_path
