# -*- coding: utf-8 -*-
"""
Simple jsonrpc base implementation using decorators. The basic service code
is based on: http://trac.pyworks.org/pyjamas/wiki/DjangoWithPyJamas
"""

# Use simplejson over json if available
try: 
    import simplejson as json
except ImportError: 
    import json

import inspect
    
version = '2.0'

class JSONRPCService:
    """
    Simple JSON RPC service
    """
    def __init__(self, method_map={}, api_version=0):
        self.method_map = method_map
    
    def add_method(self, name, method):
        self.method_map[name] = method
    
    def handle_rpc(self, data, request):
        try:
            json_version, method_id, method, params = data["jsonrpc"], data["id"], data["method"], [request,] + data["params"]
            if json_version != "2.0":
                return {'jsonrpc':version, 'id': None, "error": {"code": -32600, "message": "Invalid Request"},}
            if method in self.method_map:
                # TODO Make sue we can map this to an error using the result someday :D
                result = self.method_map[method](*params)
                return {'jsonrpc':version, 'id': method_id, 'result': result}
            else:
                return {'jsonrpc':version, 'id': method_id, "error": {"code": -32601, "message": "Method not found"},}
        except KeyError:
            return {'jsonrpc':version, 'id': None, "error": {"code": -32700, "message": "Parse error"},}
        except TypeError as e:
            return {'jsonrpc':version, 'id': None, "error": {"code": -32600, "message": "Invalid Request"},}
        
    def __call__(self, request):
        try:
            data = json.loads(request)
            if isinstance(data, dict):
                return json.dumps(self.handle_rpc(data, request))
            result_list = []
            for batch_rpc in data:
                result_list.append(self.handle_rpc(batch_rpc, request))
            return json.dumps(result_list)
        except ValueError:
            return json.dumps({'jsonrpc':version, 'id': None, "error": {"code": -32700, "message": "Parse error"},})
        
    
    def api(self):
        api_description = {}
        if api_version > 0:
            api_description['api_version']=api_version
        api_description['methods']={}
        for k, v in self.method_map.iteritems():
            api_description['methods'][k] = inspect.getargspec(v)
        return api_description

def jsonremote(service):
    """
    makes JSONRPCService a decorator so that you can write :
    
    from jsonrpc import *

    service = JSONRPCService()

    @jsonremote(service)
    def method(request, arg1, arg2):
        (...)
    
    """
    
    def remotify(func):
        if isinstance(service, JSONRPCService):
            service.add_method(func.__name__, func)
        else:
            raise NotImplementedError, 'Service "%s" not found' % str(service.__name__)
        return func

    return remotify