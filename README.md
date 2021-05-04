# Technical Exercise for first recruitment

I choose the Backend exercise.

You can test with the path `POST http://92.137.195.87/expand_validator`. 

Exemple using curl:

`curl -X POST 'http://92.137.195.87/expand_validator' --data '{"a.*.y.t": "integer",  "a.*.y.u": "integer",  "a.*.z": "object|keys:w,o",  "b": "array",   "b.c": "string",  "b.d": "object",   "b.d.e": "integer|min:5",   "b.d.f": "string"}'`

I use python with flask/flask_restfull and anytree libs.