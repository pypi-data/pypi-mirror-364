"""
WAF Client SDK - Enhanced Version with Custom Protection Settings
Python implementation equivalent to the Node.js version
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict
import re

import aiohttp
import requests
from flask import Flask, request, jsonify, Response
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse


class WAFClient:
    def __init__(self, options: Dict[str, Any] = None):
        if not options:
            options = {}
            
        if not options.get('apiKey'):
            raise ValueError('WAF API Key is required')
            
        self.config = {
            'apiKey': options['apiKey'],
            'wafEndpoint': options.get('wafEndpoint', 'https://graphnet.emailsbit.com/waf/v1/validate'),
            'timeout': options.get('timeout', 5000) / 1000,  # Convert to seconds
            'enabled': options.get('enabled', True),
            'blockOnError': options.get('blockOnError', True),
            'logRequests': options.get('logRequests', False),
            
            # Response type - 'rest' or 'graphql'
            'responseType': options.get('responseType', 'rest'),
            
            # Custom protection settings (sent to server)
            'protections': {
                'xss': {'enabled': options.get('protections', {}).get('xss', {}).get('enabled', True)},
                'sqlInjection': {'enabled': options.get('protections', {}).get('sqlInjection', {}).get('enabled', True)},
                'rce': {'enabled': options.get('protections', {}).get('rce', {}).get('enabled', True)},
                'pathTraversal': {'enabled': options.get('protections', {}).get('pathTraversal', {}).get('enabled', True)},
                'maliciousHeaders': {'enabled': options.get('protections', {}).get('maliciousHeaders', {}).get('enabled', True)},
                'fileUpload': {'enabled': options.get('protections', {}).get('fileUpload', {}).get('enabled', True)},
                'ipCheck': {'enabled': options.get('protections', {}).get('ipCheck', {}).get('enabled', True)},
            },
            
            'onWafError': options.get('onWafError', 'allow'),  # 'allow' or 'block'
            'ignoredPaths': options.get('ignoredPaths', ['/health']),
            'validatedMethods': options.get('validatedMethods', ['POST', 'PUT', 'PATCH', 'DELETE']),
            'customHeaders': options.get('customHeaders', {}),
            
            # Cache settings
            'enableCache': options.get('enableCache', True),
            'cacheTimeout': options.get('cacheTimeout', 60000) / 1000,  # Convert to seconds
            
            # Rate limiting (client-side)
            'rateLimitRequests': options.get('rateLimitRequests', 100),
            'rateLimitWindow': options.get('rateLimitWindow', 60000) / 1000,  # Convert to seconds
        }
        
        self.cache = {}
        self.rate_limit_map = defaultdict(list)
        
        # Setup logging
        self.logger = logging.getLogger('WAFClient')
        if self.config['logRequests']:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s [%(name)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.validate_protection_settings()
        
    def validate_protection_settings(self):
        valid_protections = ['xss', 'sqlInjection', 'rce', 'pathTraversal', 'maliciousHeaders', 'fileUpload', 'ipCheck']
        
        for key, value in self.config['protections'].items():
            if key not in valid_protections:
                self.logger.warning(f"⚠️  Unknown protection type: {key}. Valid types: {', '.join(valid_protections)}")
            
            if not isinstance(value.get('enabled'), bool):
                self.logger.warning(f"⚠️  Protection {key}.enabled must be boolean, got {type(value.get('enabled'))}")
                self.config['protections'][key]['enabled'] = True
                
    def should_ignore_path(self, path: str) -> bool:
        return any(ignored_path.lower() in path.lower() for ignored_path in self.config['ignoredPaths'])
        
    def should_validate_method(self, method: str) -> bool:
        return method.upper() in self.config['validatedMethods']
        
    def check_rate_limit(self, client_ip: str) -> bool:
        if not self.config['rateLimitRequests']:
            return True
            
        now = time.time()
        window_start = now - self.config['rateLimitWindow']
        
        # Remove old requests
        self.rate_limit_map[client_ip] = [
            timestamp for timestamp in self.rate_limit_map[client_ip]
            if timestamp > window_start
        ]
        
        if len(self.rate_limit_map[client_ip]) >= self.config['rateLimitRequests']:
            return False
            
        self.rate_limit_map[client_ip].append(now)
        return True
        
    def create_request_hash(self, method: str, path: str, body: Any, headers: Dict[str, str]) -> Optional[str]:
        if not self.config['enableCache']:
            return None
            
        data = {
            'method': method,
            'path': path,
            'body': body,
            'headers': {
                'user-agent': headers.get('user-agent', ''),
                'content-type': headers.get('content-type', '')
            },
            'protections': self.config['protections']
        }
        
        hash_string = json.dumps(data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
        
    def check_cache(self, hash_key: str) -> Optional[Dict]:
        if not hash_key or not self.config['enableCache'] or hash_key not in self.cache:
            return None
            
        cached = self.cache[hash_key]
        if time.time() - cached['timestamp'] > self.config['cacheTimeout']:
            del self.cache[hash_key]
            return None
            
        return cached['result']
        
    def save_to_cache(self, hash_key: str, result: Dict):
        if not hash_key or not self.config['enableCache']:
            return
            
        self.cache[hash_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
    def clean_cache(self):
        """Clean expired cache entries and rate limit data"""
        now = time.time()
        
        # Clean cache
        expired_keys = [
            key for key, data in self.cache.items()
            if now - data['timestamp'] > self.config['cacheTimeout']
        ]
        for key in expired_keys:
            del self.cache[key]
            
        # Clean rate limit map
        rate_limit_window = self.config['rateLimitWindow']
        for ip in list(self.rate_limit_map.keys()):
            valid_requests = [
                timestamp for timestamp in self.rate_limit_map[ip]
                if now - timestamp < rate_limit_window
            ]
            if not valid_requests:
                del self.rate_limit_map[ip]
            else:
                self.rate_limit_map[ip] = valid_requests
                
    async def validate_request_async(self, method: str, path: str, headers: Dict[str, str], 
                                   body: Any = None, query: Dict = None, params: Dict = None,
                                   client_ip: str = 'unknown') -> Dict:
        """Async version of request validation"""
        try:
            # Check rate limit
            if not self.check_rate_limit(client_ip):
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'RATE_LIMIT_EXCEEDED',
                    'message': f'Rate limit exceeded: {self.config["rateLimitRequests"]} requests per {int(self.config["rateLimitWindow"])} seconds'
                }
                
            payload = {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body,
                'query': query or {},
                'params': params or {},
                'timestamp': datetime.now().isoformat(),
                'clientIp': client_ip,
                'userAgent': headers.get('user-agent', ''),
                'protections': self.config['protections'],
                'clientInfo': {
                    'apiKey': self.config['apiKey'],
                    'version': '2.0.0',
                    'responseType': self.config['responseType']
                }
            }
            
            if self.config['logRequests']:
                enabled_protections = [
                    name for name, config in self.config['protections'].items()
                    if config['enabled']
                ]
                self.logger.info(f"🔍 Sending for validation: {method} {path}, "
                               f"protections: {enabled_protections}, ip: {client_ip}")
                
            request_headers = {
                'Content-Type': 'application/json',
                'Authorization': self.config['apiKey'],
                'X-WAF-Client': 'python',
                'X-WAF-Response-Type': self.config['responseType'],
                **self.config['customHeaders']
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.config['wafEndpoint'],
                    json=payload,
                    headers=request_headers
                ) as response:
                    response_data = await response.json()
                    
                    if self.config['logRequests']:
                        applied_protections = []
                        if 'appliedProtections' in response_data:
                            applied_protections = [
                                name for name, config in response_data['appliedProtections'].items()
                                if config.get('enabled', False)
                            ]
                            
                        self.logger.info(f"📨 Server response: status={response.status}, "
                                       f"blocked={response_data.get('blocked', False)}, "
                                       f"violations={response_data.get('validationResults', {}).get('totalViolations', 0)}, "
                                       f"applied_protections={applied_protections}")
                    
                    return response_data
                    
        except asyncio.TimeoutError:
            if self.config['logRequests']:
                self.logger.error("❌ Timeout error connecting to WAF service")
                
            if self.config['onWafError'] == 'block' or self.config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_NETWORK_ERROR',
                    'message': 'Unable to connect to security service',
                    'error': {'type': 'TIMEOUT', 'timeout': True}
                }
            
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_NETWORK_ERROR',
                'message': 'Security validation unavailable, request allowed',
                'warning': True
            }
            
        except Exception as error:
            if self.config['logRequests']:
                self.logger.error(f"❌ Network/timeout error: {str(error)}")
                
            if self.config['onWafError'] == 'block' or self.config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_UNEXPECTED_ERROR',
                    'message': 'Unexpected error during security validation',
                    'error': {'type': 'UNKNOWN'}
                }
                
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_UNEXPECTED_ERROR',
                'message': 'Security validation error, request allowed',
                'warning': True
            }
            
    def validate_request_sync(self, method: str, path: str, headers: Dict[str, str],
                            body: Any = None, query: Dict = None, params: Dict = None,
                            client_ip: str = 'unknown') -> Dict:
        """Sync version of request validation"""
        try:
            # Check rate limit
            if not self.check_rate_limit(client_ip):
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'RATE_LIMIT_EXCEEDED',
                    'message': f'Rate limit exceeded: {self.config["rateLimitRequests"]} requests per {int(self.config["rateLimitWindow"])} seconds'
                }
                
            payload = {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body,
                'query': query or {},
                'params': params or {},
                'timestamp': datetime.now().isoformat(),
                'clientIp': client_ip,
                'userAgent': headers.get('user-agent', ''),
                'protections': self.config['protections'],
                'clientInfo': {
                    'apiKey': self.config['apiKey'],
                    'version': '2.0.0',
                    'responseType': self.config['responseType']
                }
            }
            
            if self.config['logRequests']:
                enabled_protections = [
                    name for name, config in self.config['protections'].items()
                    if config['enabled']
                ]
                self.logger.info(f"🔍 Sending for validation: {method} {path}, "
                               f"protections: {enabled_protections}, ip: {client_ip}")
                
            request_headers = {
                'Content-Type': 'application/json',
                'Authorization': self.config['apiKey'],
                'X-WAF-Client': 'python',
                'X-WAF-Response-Type': self.config['responseType'],
                **self.config['customHeaders']
            }
            
            response = requests.post(
                self.config['wafEndpoint'],
                json=payload,
                headers=request_headers,
                timeout=self.config['timeout']
            )
            
            response_data = response.json()
            
            if self.config['logRequests']:
                applied_protections = []
                if 'appliedProtections' in response_data:
                    applied_protections = [
                        name for name, config in response_data['appliedProtections'].items()
                        if config.get('enabled', False)
                    ]
                    
                self.logger.info(f"📨 Server response: status={response.status_code}, "
                               f"blocked={response_data.get('blocked', False)}, "
                               f"violations={response_data.get('validationResults', {}).get('totalViolations', 0)}, "
                               f"applied_protections={applied_protections}")
            
            return response_data
            
        except requests.exceptions.Timeout:
            if self.config['logRequests']:
                self.logger.error("❌ Timeout error connecting to WAF service")
                
            if self.config['onWafError'] == 'block' or self.config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_NETWORK_ERROR',
                    'message': 'Unable to connect to security service',
                    'error': {'type': 'TIMEOUT', 'timeout': True}
                }
            
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_NETWORK_ERROR',
                'message': 'Security validation unavailable, request allowed',
                'warning': True
            }
            
        except Exception as error:
            if self.config['logRequests']:
                self.logger.error(f"❌ Network/timeout error: {str(error)}")
                
            if self.config['onWafError'] == 'block' or self.config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_UNEXPECTED_ERROR',
                    'message': 'Unexpected error during security validation',
                    'error': {'type': 'UNKNOWN'}
                }
                
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_UNEXPECTED_ERROR',
                'message': 'Security validation error, request allowed',
                'warning': True
            }
            
    def create_graphql_error_response(self, operation_info: Optional[Dict], validation: Dict) -> Dict:
        """Create GraphQL response with detailed violation information"""
        def to_camel_case(s: str) -> str:
            if not s:
                return s
            return s[0].lower() + s[1:]
            
        # Include detailed violation information in GraphQL response
        violation_details = validation.get('validationResults', {}).get('violations', [])
        violation_summary = []
        
        for v in violation_details:
            violation_summary.append({
                'type': v.get('type', ''),
                'severity': v.get('severity', ''),
                'count': len(v.get('details', [])) if isinstance(v.get('details'), list) else 1,
                'readableType': v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
            })
            
        # Create human-readable violation list
        violation_list = ', '.join([
            v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
            for v in violation_details
        ])
        
        enhanced_message = f"{validation.get('message', 'Request blocked by security policy')} ({violation_list})" if violation_list else validation.get('message', 'Request blocked by security policy')
        
        if not operation_info:
            return {
                'data': None,
                'errors': [{
                    'message': enhanced_message,
                    'extensions': {
                        'code': validation.get('reason', 'SECURITY_VIOLATION'),
                        'blocked': True,
                        'waf': True,
                        'violations': violation_summary,
                        'violationTypes': violation_list,
                        'totalViolations': validation.get('validationResults', {}).get('totalViolations', 0),
                        'highSeverityViolations': validation.get('validationResults', {}).get('highSeverityViolations', 0)
                    }
                }]
            }
            
        operation_name = to_camel_case(operation_info.get('name', ''))
        response = {
            'data': {},
            'errors': [{
                'message': enhanced_message,
                'extensions': {
                    'code': validation.get('reason', 'SECURITY_VIOLATION'),
                    'operation': operation_name,
                    'blocked': True,
                    'waf': True,
                    'violations': violation_summary,
                    'violationTypes': violation_list,
                    'totalViolations': validation.get('validationResults', {}).get('totalViolations', 0),
                    'highSeverityViolations': validation.get('validationResults', {}).get('highSeverityViolations', 0)
                }
            }]
        }
        
        response['data'][operation_name] = {
            'success': False,
            'message': enhanced_message,
            'blocked': True,
            'reason': validation.get('reason'),
            'violations': violation_list,
            'violationDetails': violation_summary
        }
        
        return response
        
    def parse_graphql_operation(self, body: Any) -> Optional[Dict]:
        """Extract GraphQL operation info"""
        try:
            if not body or not isinstance(body, dict) or 'query' not in body:
                return None
                
            operation_name = body.get('operationName') or self.extract_operation_name_from_query(body['query'])
            return {'name': operation_name} if operation_name else None
            
        except Exception:
            return None
            
    def extract_operation_name_from_query(self, query: str) -> Optional[str]:
        """Extract operation name from GraphQL query"""
        try:
            match = re.search(r'(query|mutation|subscription)\s+(\w+)', query, re.IGNORECASE)
            return match.group(2) if match else None
        except Exception:
            return None
            
    def get_config_summary(self) -> Dict:
        """Get current configuration summary"""
        enabled_protections = [
            name for name, config in self.config['protections'].items()
            if config['enabled']
        ]
        
        return {
            'enabled': self.config['enabled'],
            'responseType': self.config['responseType'],
            'enabledProtections': enabled_protections,
            'disabledProtections': [p for p in self.config['protections'].keys() if p not in enabled_protections],
            'cacheEnabled': self.config['enableCache'],
            'rateLimitEnabled': bool(self.config['rateLimitRequests']),
            'validatedMethods': self.config['validatedMethods'],
            'ignoredPaths': self.config['ignoredPaths']
        }
        
    # Flask middleware
    def flask_middleware(self):
        """Flask middleware implementation"""
        if self.config['logRequests']:
            self.logger.info(f"🛡️  WAF Client initialized with config: {self.get_config_summary()}")
            
        def middleware():
            if not self.config['enabled']:
                return None
                
            path = request.path
            method = request.method
            
            if self.should_ignore_path(path):
                if self.config['logRequests']:
                    self.logger.info(f"⏭️  Ignoring path: {path}")
                return None
                
            if not self.should_validate_method(method):
                if self.config['logRequests']:
                    self.logger.info(f"⏭️  Ignoring method: {method}")
                return None
                
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                          request.environ.get('HTTP_X_REAL_IP', 
                                                            request.environ.get('REMOTE_ADDR', 'unknown')))
            if ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
                
            # Create request hash for caching
            body = None
            try:
                if request.is_json:
                    body = request.get_json()
                elif request.form:
                    body = dict(request.form)
            except Exception:
                pass
                
            request_hash = self.create_request_hash(method, path, body, dict(request.headers))
            cached_result = self.check_cache(request_hash)
            
            if cached_result:
                if self.config['logRequests']:
                    self.logger.info('📋 Using cached result')
                    
                if not cached_result.get('allowed', True) or cached_result.get('blocked', False):
                    if self.config['responseType'] == 'graphql':
                        operation_info = self.parse_graphql_operation(body)
                        graphql_response = self.create_graphql_error_response(operation_info, cached_result)
                        return jsonify(graphql_response), 200
                    else:
                        # Enhanced cached response with violation details
                        violation_details = cached_result.get('validationResults', {}).get('violations', [])
                        violation_summary = ', '.join([
                            v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                            for v in violation_details
                        ])
                        
                        enhanced_message = f"{cached_result.get('message', '')} ({violation_summary})" if violation_summary else cached_result.get('message', '')
                        
                        return jsonify({
                            'success': False,
                            'blocked': True,
                            'reason': cached_result.get('reason'),
                            'message': enhanced_message,
                            'violations': violation_summary,
                            'details': cached_result.get('validationResults'),
                            'cached': True
                        }), 403
                        
                return None
                
            # Validate request
            validation = self.validate_request_sync(
                method, path, dict(request.headers), body,
                dict(request.args), {}, client_ip
            )
            
            self.save_to_cache(request_hash, validation)
            
            if not validation.get('allowed', True) or validation.get('blocked', False):
                # Enhanced logging with detailed violation information
                if self.config['logRequests']:
                    violation_details = validation.get('validationResults', {}).get('violations', [])
                    violation_summary = ', '.join([
                        f"{v.get('type', '').replace('_DETECTED', '').replace('_', ' ')} ({len(v.get('details', [])) if isinstance(v.get('details'), list) else 1})"
                        for v in violation_details
                    ])
                    
                    high_severity = len([v for v in violation_details if v.get('severity') in ['CRITICAL', 'HIGH']])
                    
                    self.logger.info(f"🚫 Request blocked: reason={validation.get('reason')}, "
                                   f"violations={validation.get('validationResults', {}).get('totalViolations', 0)}, "
                                   f"types={violation_summary or 'Unknown'}, "
                                   f"severity={high_severity} high/critical")
                    
                if self.config['responseType'] == 'graphql':
                    operation_info = self.parse_graphql_operation(body)
                    graphql_response = self.create_graphql_error_response(operation_info, validation)
                    return jsonify(graphql_response), 200
                else:
                    # Enhanced REST response with human-readable violation summary
                    violation_details = validation.get('validationResults', {}).get('violations', [])
                    violation_summary = ', '.join([
                        v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                        for v in violation_details
                    ])
                    
                    enhanced_message = f"{validation.get('message', '')} ({violation_summary})" if violation_summary else validation.get('message', '')
                    
                    return jsonify({
                        'success': False,
                        'blocked': True,
                        'reason': validation.get('reason'),
                        'message': enhanced_message,
                        'violations': violation_summary,
                        'details': validation.get('validationResults')
                    }), 403
                    
            if self.config['logRequests']:
                self.logger.info('✅ Request approved')
                
            return None
            
        return middleware
        
    # FastAPI middleware
    async def fastapi_middleware(self, request: Request, call_next):
        """FastAPI middleware implementation"""
        if not self.config['enabled']:
            response = await call_next(request)
            return response
            
        path = request.url.path
        method = request.method
        
        if self.should_ignore_path(path):
            if self.config['logRequests']:
                self.logger.info(f"⏭️  Ignoring path: {path}")
            response = await call_next(request)
            return response
            
        if not self.should_validate_method(method):
            if self.config['logRequests']:
                self.logger.info(f"⏭️  Ignoring method: {method}")
            response = await call_next(request)
            return response
            
        # Get client IP
        client_ip = request.client.host if request.client else 'unknown'
        if 'x-forwarded-for' in request.headers:
            forwarded_ips = request.headers['x-forwarded-for'].split(',')
            client_ip = forwarded_ips[0].strip()
        elif 'x-real-ip' in request.headers:
            client_ip = request.headers['x-real-ip']
            
        # Get request body
        body = None
        try:
            if request.headers.get('content-type', '').startswith('application/json'):
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes.decode())
        except Exception:
            pass
            
        # Create request hash for caching
        request_hash = self.create_request_hash(method, path, body, dict(request.headers))
        cached_result = self.check_cache(request_hash)
        
        if cached_result:
            if self.config['logRequests']:
                self.logger.info('📋 Using cached result')
                
            if not cached_result.get('allowed', True) or cached_result.get('blocked', False):
                if self.config['responseType'] == 'graphql':
                    operation_info = self.parse_graphql_operation(body)
                    graphql_response = self.create_graphql_error_response(operation_info, cached_result)
                    return JSONResponse(content=graphql_response, status_code=200)
                else:
                    # Enhanced cached response with violation details
                    violation_details = cached_result.get('validationResults', {}).get('violations', [])
                    violation_summary = ', '.join([
                        v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                        for v in violation_details
                    ])
                    
                    enhanced_message = f"{cached_result.get('message', '')} ({violation_summary})" if violation_summary else cached_result.get('message', '')
                    
                    return JSONResponse({
                        'success': False,
                        'blocked': True,
                        'reason': cached_result.get('reason'),
                        'message': enhanced_message,
                        'violations': violation_summary,
                        'details': cached_result.get('validationResults'),
                        'cached': True
                    }, status_code=403)
                    
        # Validate request
        validation = await self.validate_request_async(
            method, path, dict(request.headers), body,
            dict(request.query_params), {}, client_ip
        )
        
        self.save_to_cache(request_hash, validation)
        
        if not validation.get('allowed', True) or validation.get('blocked', False):
            # Enhanced logging with detailed violation information
            if self.config['logRequests']:
                violation_details = validation.get('validationResults', {}).get('violations', [])
                violation_summary = ', '.join([
                    f"{v.get('type', '').replace('_DETECTED', '').replace('_', ' ')} ({len(v.get('details', [])) if isinstance(v.get('details'), list) else 1})"
                    for v in violation_details
                ])
                
                high_severity = len([v for v in violation_details if v.get('severity') in ['CRITICAL', 'HIGH']])
                
                self.logger.info(f"🚫 Request blocked: reason={validation.get('reason')}, "
                               f"violations={validation.get('validationResults', {}).get('totalViolations', 0)}, "
                               f"types={violation_summary or 'Unknown'}, "
                               f"severity={high_severity} high/critical")
                
            if self.config['responseType'] == 'graphql':
                operation_info = self.parse_graphql_operation(body)
                graphql_response = self.create_graphql_error_response(operation_info, validation)
                return JSONResponse(content=graphql_response, status_code=200)
            else:
                # Enhanced REST response with human-readable violation summary
                violation_details = validation.get('validationResults', {}).get('violations', [])
                violation_summary = ', '.join([
                    v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                    for v in violation_details
                ])
                
                enhanced_message = f"{validation.get('message', '')} ({violation_summary})" if violation_summary else validation.get('message', '')
                
                return JSONResponse({
                    'success': False,
                    'blocked': True,
                    'reason': validation.get('reason'),
                    'message': enhanced_message,
                    'violations': violation_summary,
                    'details': validation.get('validationResults')
                }, status_code=403)
                
        if self.config['logRequests']:
            self.logger.info('✅ Request approved')
            
        response = await call_next(request)
        return response