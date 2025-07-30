import re

class RequestUtils:
    @staticmethod
    def resolve_path_param(url_path, **kwargs):
        placeholder_pattern = re.compile(r'<(.*?)>')
        placeholders = placeholder_pattern.findall(url_path)
        
        filled_path = url_path
        for placeholder in placeholders:
            if placeholder in kwargs:
                filled_path = filled_path.replace(f'<{placeholder}>', kwargs[placeholder])
            else:
                raise ValueError(f"Missing value for placeholder: {placeholder}")
        return filled_path