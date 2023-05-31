## Frappe ReST API Wrapper


### Installation
``` sh
$ bench get-app https://github.com/pinely-international/restipie.git
```
### Prerequisite
You should have frappe installed.
Edit apps/frappe/frappe/app.py, and add elif block as shown in lines 16 to 17

``` python
1  import frappe
2  from restipie.core import handle
3  from werkzeug.wrappers import Request
4  # import yours api routes here
5
6
7  @Request.application
8  def application(request):
9     response = None
10
11    try:
12        ...
13        if frappe.local.form_dict.cmd:
14            response = frappe.handler.handle()
15
16        elif frappe.request.path.startswith("/v1/"):
17            response = handle()
18    
19        elif frappe.request.path.startswith("/api/"):
20            response = frappe.api.handle()
21    ...
```
The above code will direct incoming request to "/v1/api/" to our custom handler.

### Adding custom ReST 
Declare a function that accepts *args and **kwargs parameters and decorate it with the api function decorator as shown below.
```python
    from restipie.core import request
    from restipie.core.response import JSONResponse


    @request.api("POST", "/v1/api/test/users")
    def create_user(*args, **kwargs):
        try:
            data = kwargs.get("data")

            #don't bake the business logic here, put it in the service layer.

            return JSONResponse(
                data=data
            )
        except Exception as e:
            raise e

```
For uniformity, json responses are handled by response.JSONResponse class
### Using [JSON Schema](https://json-schema.org/specification.html) to describe our data format and [jsonschema](https://python-jsonschema.readthedocs.io/en/v3.2.0/) to validate.
An example of json schema declaration for an imaginary user.
```python
    user_schema = {
        "$schema":"http://json-schema.org/draft-07/schema#",
        "title":"Test User",
        "type" : "object",
        "properties" : {
            "email" : {
                "type" : "string",
                "format": "email",
                "description": "Email of the user"
                },
            "fullname" : {"type" : "string"},
            "age": {"type" : "integer", "minimum": 18}
        },
        "required": ["email", "fullname"]
    }
```
### Using middlewares
The request.api decorator accepts a middleware key argument which is a tuple of functions.
Here we use request.validate_schema to validate kwargs.get("data")(which contains the request body) againts our defined schema.
```python
    ...
    from .schema import user_schema
    from restipie.core import request, middleware
    from restipie.core.response import JSONResponse

    @request.api("POST", "/v1/api/test/users", middlewares=(middleware.validate_schema(user_schema)))
    def create_user(*args, **kwargs):
        try:
            data = kwargs.get("data")

            #don't bake the business logic here, put it in the service layer.

            return JSONResponse(
                data=data
            )
        except Exception as e:
            raise e
```
Middlewares are executed in order they are declared in the tuple.

### Middleware declaration
This is an example of a middleware that validates user token and session id.
You can can add values to args and kwargs here. Just keep in mind that these arguments are not immutable so make sure that you know the side effects if you add, update or delete values from them. 
One thing to note here is that we want to return the args and kwargs as a tuple (for convenience) as it will be passed to the next middleware.

```python
    def authenticate(*args, **kwargs):
        token = frappe.get_request_header("Authorization")

        decoded = validate_token(token)                 #this raises an 'Unauthorized' exception if token is invalid
        validate_session(decoded.get("sid"))            #this raises an 'Unauthorized' exception if session id is invalid

        # set user only after token and session validation
        user = frappe.get_doc("User", { "email": decoded.get("user") })
        frappe.set_user(user.name)

        kwargs["decoded"] = decoded
        return args, kwargs

```
### Error handling
Exceptions raised inside of the handler and middleware will propagate to the main handler and will be sent to the client as json.

```python
    @request.api("GET", "/v1/api/test/users/<id>", middlewares=(authenticate))
    def get_one_user(*args, **kwargs):
        try:
            user_id = kwargs.get("params").get("id")

            #don't bake the business logic here, put it in the service layer.

            response = JSONResponse(data={})
            return 
        except Exception as e:
            raise e
```
