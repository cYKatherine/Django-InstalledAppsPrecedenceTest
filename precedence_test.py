import os
import re
import glob

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.conf import settings

######################################################################
# Monkeypatches to the Loader class.
from django.template.loaders.base import Loader
from django.template import Template, TemplateDoesNotExist
from django.utils.inspect import func_supports_parameter


def patched_Loader_get_template(self, template_name, template_dirs=None, skip=None):
    tried = []

    args = [template_name]
    # RemovedInDjango20Warning: Add template_dirs for compatibility with
    # old loaders
    if func_supports_parameter(self.get_template_sources, 'template_dirs'):
        args.append(template_dirs)

    return_value = None
    return_value_origin = None
    for origin in self.get_template_sources(*args):
        if skip is not None and origin in skip:
            tried.append((origin, 'Skipped'))
            continue

        try:
            contents = self.get_contents(origin)
        except TemplateDoesNotExist:
            tried.append((origin, 'Source does not exist'))
            continue
        else:
            if return_value is None:
                return_value = Template(
                    contents, origin, origin.template_name, self.engine,
                )
                return_value_origin = origin
            else:
                print((
                    "CONFLICT[%s]: %s is used instead of %s"
                    % (return_value_origin.template_name, return_value_origin, origin)
                ))

    if return_value:
        return return_value

    raise TemplateDoesNotExist(template_name, tried=tried)


Loader.get_template = patched_Loader_get_template

######################################################################

from django.template.exceptions import TemplateSyntaxError
from django.template.loader import get_template


class Command(BaseCommand):
    help = "Rebuild the forms cache."

    def handle(self, **options):
        # Clear the cache.
        cache.clear()
        print("Cleared the cache.")

        for app in settings.INSTALLED_APPS:
            is_local_app = app.split('.')[0] == "your local directory root"
            app_path_without_templates = app.replace('.', '/')
            if not is_local_app:
                app_path_without_templates = (
                    os.environ.get("VIRTUAL_ENV", None) +
                    "/lib/*/site-packages/" +
                    app_path_without_templates
                )
            app_path = app_path_without_templates + '/templates/**/*.*'
            for filename in glob.iglob(app_path, recursive=True):
                template_name = re.sub(r'^.*/templates/', '', filename)
                try:
                    get_template(template_name)
                except TemplateSyntaxError:
                    pass
