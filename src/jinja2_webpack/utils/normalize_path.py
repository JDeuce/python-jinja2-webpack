import os


def normalize_path(path):
    """ normalizes a path to using /, even if you're on windows.
    jinja2 assumes all templates are referenced with /
    despite the underlying OS, see jinja2.loaders.split_template_path.
    """
    return '/'.join(os.path.normpath(path).split(os.sep))
