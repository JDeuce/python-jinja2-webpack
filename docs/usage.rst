=====
Usage
=====

To use jinja2-webpack in a project::

	import jinja2_webpack


=============================
Referencing asset from jinja2
=============================
You can get an asset reference by using the filter syntax::

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


This project comes with the jinja2-webpack-scan command line
tool which can be used to generate a JS file that can be used
to force webpack to build entries you reference in your jinja2 templates.


Example running it on a template with::

    {{ "entry_name" | webpack }}

Would produce a JS reference file with a line like::

    require("entry_name")

And it takes the path of the entry into account, so you can
do relative imports such as::

    {{ "../pngs/image.png" | webpack }}


And it will resolve the path relative to where you store the
output file::

    require("project/pngs/image.png")


Example usage::

    jinja2-webpack-scan -o webpack-asset-entries.js \
        -d 'templates/' \
        --root 'project/' \
        'templates/\*.jinja2'



And then configure webpack so it will build those things::


    modules.exports = {
        ...,
        entries: {
            ...,
            assets: './project/webpack-asset-entries.js'
        }
    }


