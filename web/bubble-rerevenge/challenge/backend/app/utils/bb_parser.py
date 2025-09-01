import html


class BBCodeParser:
    def parse(self, text):
        # bb bb fr fr
        return html.escape(text, quote=True)