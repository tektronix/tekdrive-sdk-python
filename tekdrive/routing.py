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
        self.folder_id = params.get('folder_id')


ENDPOINTS = {
    "file_create": "/file",
    "file_details": "/file/{file_id}",
    "file_download": "/file/{file_id}/contents",
    "file_members": "/file/{file_id}/members",
    "file_upload": "/file/{file_id}/uploadUrl",
    "folder_create": "/folder",
    "folder_details": "/folder/{folder_id}",
    "folder_members": "/folder/{folder_id}/members",
    "search": "/search",
}
