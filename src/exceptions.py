class OilSyntaxError(Exception):
    def __init__(self, message, line_num=None, source_line=None):
        self.message = message
        self.line_num = line_num
        self.source_line = source_line
        super().__init__(self.format_error())

    def format_error(self):
        if self.line_num is not None and self.source_line is not None:
            return f"SyntaxError at line {self.line_num}:\n {self.source_line}\n {self.message}"
        else:
            return f"SyntaxError: {self.message}"
