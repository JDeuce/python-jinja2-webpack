=====
Usage
=====

You will configure webpack to write a JSON manifest of built files with webpack-manifest-plugin.

This project can then be configured to load the manifest, and allow you to reference the templates
from your jinja2 templates by using the filter syntax::

    {{ "entry_name" | webpack }}


So for a JS file reference you might use syntax like::

    <script src="{{ "test_js_bundle" | webpack }}"></script>


==================
Setting up webpack
==================

Add webpack-manifest-plugin as a dependency and configure it
into your webpack.config.js::

    var ManifestPlugin = require('webpack-manifest-plugin');

    module.exports = {
        ...
        plugins: [
            ...,
            new ManifestPlugin({
                fileName: './webpack-manifest.json',
            })
        ]
    }


==========================================
Auto-scanning jinja2 templates for entries
==========================================


It is also possible to scan your jinja2 templates to force
webpack to process assets that you reference from them.

This would enable you to reference static pngs from within your jinja2
templates.

The project comes with a command line tool called jinja2-webpack-scan
which can be used to generate a JS file that requires() all of the
assets you reference from your jinja2 templates. This will cause webpack
to process them and add them to the manifest.

Example running it on a template with::

    {{ "./image.png" | webpack }}

Would produce a JS reference file with a line like::

    require("./image.png");

And it takes the path of the entry into account, so you can
do relative imports within your templates such as::

    {{ "../pngs/image.png" | webpack }}


And it will resolve the path relative to where you store the
output file::

    require("project/pngs/image.png")


Example usage::

    jinja2-webpack-scan \
        -o webpack-asset-entries.js \
        -d 'templates/' \
        --root 'project/' \
        'templates/*.jinja2'



And then configure webpack so it will build those things::


    modules.exports = {
        ...,
        entries: {
            ...,
            assets: './project/webpack-asset-entries.js'
        }
    }


