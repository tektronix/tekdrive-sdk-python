from urllib.parse import quote as _uriquote


class Route:

    def __init__(self, method, path_template, **params):
        self.method = method
        self.path_template = path_template
        if params:
            self.path = path_template.format(**{k: _uriquote(v) if isinstance(v, str) else v for k, v in params.items()})
        else:
            self.path = path_template

        # major params:
        self.file_id = params.get('file_id')


ENDPOINTS = {
    "file_create": "/file",
    "file_details": "/file/{file_id}",
    "file_members": "/file/{file_id}/members",
    "file_overwrite": "/file/{file_id}/uploadUrl",
}