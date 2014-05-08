# -*- coding: utf-8 -*-
"""
Simple jsonrpc base implementation using decorators.

    from simplejsonrpc import *

    loginservice = SimpleJSONRPCService(api_version=1)

    @jsonremote(loginservice, 'login')
    def login(request, user_name, user_pass):
        (...)
"""

# Use simplejson over json if available
try: 
    import simplejson as json
except ImportError: 
    import json

import inspect

version = '2.0'

class SimpleJSONRPCService:
    """
    Simple JSON RPC service
    """
    def __init__(self, method_map=None, api_version=0):
        if method_map is None:
            self.method_map = {}
        else:
            self.method_map = method_map
        self.api_version = api_version
    
    def add_method(self, name, method):
        self.method_map[name] = method
    
    def handle_rpc(self, data, request, node):
        try:
            json_version, method_id, method, params = data["jsonrpc"], data["id"], data["method"], [request, node,] + data["params"]
            if json_version != "2.0":
                return {'jsonrpc':version, 'id': None, "error": {"code": -32600, "message": "Invalid Request"},}
            if method in self.method_map:
                # TODO Make sure we can map this to an error using the result someday :D
                try:
                    result = self.method_map[method](*params)
                except TypeError:
                    return {'jsonrpc':version, 'id': None, "error": {"code": -32602, "message": "Invalid params"},}
                return {'jsonrpc':version, 'id': method_id, 'result': result}
            else:
                return {'jsonrpc':version, 'id': method_id, "error": {"code": -32601, "message": "Method not found"},}
        except KeyError:
            return {'jsonrpc':version, 'id': None, "error": {"code": -32700, "message": "Parse error"},}
        except TypeError:
            return {'jsonrpc':version, 'id': None, "error": {"code": -32600, "message": "Invalid Request"},}
        
    def __call__(self, request, node):
        try:
            data = json.loads(request)
            if isinstance(data, dict):
                return json.dumps(self.handle_rpc(data, request, node))
            result_list = []
            for batch_rpc in data:
                result_list.append(self.handle_rpc(batch_rpc, request, node))
            return json.dumps(result_list)
        except ValueError:
            return json.dumps({'jsonrpc':version, 'id': None, "error": {"code": -32700, "message": "Parse error"},})
        
    
    def api(self):
        api_description = {}
        if self.api_version > 0:
            api_description['api_version']=self.api_version
        api_description['methods']={}
        for k, v in self.method_map.iteritems():
            api_description['methods'][k] = inspect.getargspec(v)
        return api_description

def jsonremote(service, name=None):
    """
    makes SimpleJSONRPCService a decorator so that you can write :
    
    from simplejsonrpc import *

    loginservice = SimpleJSONRPCService(api_version=1)

    @jsonremote(loginservice, 'login')
    def login(request, user_name, user_pass):
        (...)
    
    """
    
    def remotify(func):
        if isinstance(service, SimpleJSONRPCService):
            func_name = name
            if func_name is None:
                func_name = func.__name__
            service.add_method(func_name, func)
        else:
            raise NotImplementedError, 'Service "%s" not found' % str(service.__name__)
        return func

    return remotify
