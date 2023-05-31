import json

from frappe.utils.response import json_handler, make_logs
from werkzeug.wrappers import Response


def handle_err(exception):
    context = exception.__class__.__name__

    if hasattr(exception, "http_status_code"):
        code = exception.http_status_code
        message = str(exception)

    else:
        code = exception.code if hasattr(exception, "code") else 500
        message = exception.description if hasattr(exception, "description") \
            else str(exception)

    data = {"data": {
        "success": False,
        "context": context,
        "message": message
    }
    }

    return JSONResponse(status_code=code, data=data)


class JSONResponse(Response):
    valid_fields = ["message", "data"]

    def __init__(self, data: dict, status_code: int = 200, status: bool = True, **kwargs):
        make_logs()
        super().__init__(**kwargs)
        self.status = status
        self.status_code = status_code
        self.mimetype = "application/json"
        self.charset = "utf-8"
        self.data = json.dumps(data,
                               default=json_handler,
                               separators=(',', ':')
                               )

# TODO Make html response
