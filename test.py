# -*- coding: utf-8 -*-
import unittest
import json
from simplejsonrpc import *

class TestJSONRPCService(unittest.TestCase):

    def testService(self):

        test_service = SimpleJSONRPCService(api_version=1)

        @jsonremote(test_service, name='test', doc='Test method')
        def test(request):
            return "ok"

        # test method should be registered by now
        self.assertTrue('test' in test_service.api()['methods'])

        # the call should complete successfully
        self.assertEqual(
            test_service(json.dumps({"jsonrpc": "2.0", "method": "test", "params": [], "id": 1})), 
            json.dumps({"jsonrpc": "2.0", "id": 1, "result": "ok"}))

        # Test a second api
        test_service_2 = SimpleJSONRPCService(api_version=2)
        @jsonremote(test_service_2, name='test', doc='Test method')
        def test_2(request):
            return "ok2"

        # test method should be registered by now
        self.assertTrue('test' in test_service_2.api()['methods'])

        # the call should complete successfully
        self.assertEqual(
            test_service_2(json.dumps({"jsonrpc": "2.0", "method": "test", "params": [], "id": 1})), 
            json.dumps({"jsonrpc": "2.0", "id": 1, "result": "ok2"}))

    def testExceptions(self):
        
        test_service = SimpleJSONRPCService()

        @jsonremote(test_service, name='test', doc='Test method')
        def test(request):
            raise JSONRPCException("Oh snap, this can happen.", 12345, {"data":"oh boy..."})

        # the cexception should match
        self.assertEqual(
            test_service(json.dumps({"jsonrpc": "2.0", "method": "test", "params": [], "id": 1})), 
            json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"message": "Oh snap, this can happen.", "code": 12345, "data": {"data": "oh boy..."}}}))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJSONRPCService)
    unittest.TextTestRunner(verbosity=2).run(suite)
