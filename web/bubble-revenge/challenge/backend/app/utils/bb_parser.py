import re

import bbcode


class BBCodeParser:
    def __init__(self):
        self._parser = bbcode.Parser()
        self._parser.add_formatter("youtube", self.render_youtube, standalone=True)
        self._parser.add_formatter("yt", self.render_youtube, standalone=True)
        self._parser.add_formatter("img", self.render_img, replace_links=False)
        self._parser.add_simple_formatter('h1', '<h1>%(value)s</h1>')
        self._parser.add_simple_formatter('sup', '<sup>%(value)s</sup>')
    
    def parse(self, text):
        return self._parser.format(text)

    @staticmethod
    def options_cleaner(options):
        p = bbcode.Parser()
        for key in options:
            options[key] = p._replace(options[key], p.REPLACE_ESCAPE)
            if re.sub(r"[^a-z0-9+]", "", options[key].lower().split(":", 1)[0]) in ("javascript", "data", "vbscript"):
                options[key] = "undefined"

    @staticmethod
    def render_youtube(name, value, options, parent, context):
        yt_options = {
            'youtube_id': options.get('id', 'undefined'),
            'width': options.get('width', '560'),
            'height': options.get('height', '315'),
        }
        BBCodeParser.options_cleaner(yt_options)
        return '<iframe width="{width}" height="{height}" ' \
               'src="https://www.youtube.com/embed/{youtube_id}" ' \
               'frameborder="0" allowfullscreen></iframe>'.format(**yt_options)

    @staticmethod
    def render_img(name, value, options, parent, context):
        img_options = {}
        if img_width := options.get('width'):
            img_options['width'] = img_width
        if img_height := options.get('height'):
            img_options['height'] = img_height
        BBCodeParser.options_cleaner(img_options)
        attrs = " ".join([
            f"{attr_key}={attr_value}" for attr_key, attr_value in img_options.items()
        ])
        return f'<img src="' + value.replace('"', "%22") +f'" {attrs} alt="User posted image" style="max-width:100%;">'
