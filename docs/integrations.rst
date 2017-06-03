===========================
Raw integration with jinja2
===========================
To use jinja2-webpack in a project::

    from jinja2 import Environment
    from jinja2_webpack import Environment as WebpackEnvironment
    from jinja2_webpack.filter import WebpackFilter


    jinja2_env = Environment(loader=FileSystemLoader(['.']))
    webpack_env = WebpackEnvironment(manifest='webpack-manifest.json')
    jinja2_env.filters['webpack'] = WebpackFilter(webpack_env)


=======
Pyramid
=======

See: `pyramid-jinja2-webpack <http://pyramid-jinja2-webpack.readthedocs.io/en/latest/>`_.

