

class Router:

    def __init__(self):
        self.routes = {
            'GET': {},
            'POST': {}
        }

        self.param_routes = {
            'GET': [],
            'POST' : []
        }

        self.wildcard_routes = {
            'GET': [],
            'POST': []
        }

    def _has_params(self, path):
        return '{' in path and '}' in path

    def _has_wildcards(self, path):
        return '*' in path

    def add_route(self, path, method, handler):
        # /api/v1/users/{id}
        # /api/v1/users/{id}/posts/{pid}
        if method not in self.routes.keys():
            return f"{method} not allowed. Only allowed methods are {','.join(list(self.routes.keys()))}"
        
        if self._has_wildcards(path):
            self.wildcard_routes[method].append({
                'pattern': path, 
                'handler': handler
            })
        elif self._has_params(path):
            self.param_routes[method].append({
                'pattern': path, 
                'handler': handler
            })

        else:
            self.routes[method][path] = handler

    def _get_match_params(self, path, pattern):

        s1 = path.strip('/').split('/')
        s2 = pattern.strip('/').split('/')
        
        if len(s1) != len(s2):
            return None

        params = {}
        for path_seg, pattern_seg in zip(s1, s2):
            if self._has_params(pattern_seg):
                key = pattern_seg.replace('{','')
                key = key.replace('}','')
                value = path_seg
                params[key] = value
                continue
            if path_seg != pattern_seg:
                return None
        return params

    def _get_wildcard_params(self, path, pattern):
        # wildcard pattern
        # /api/v1/files/{*path}
        s1 = path.strip('/').split('/')
        s2 = pattern.strip('/').split('/')

        for i, seg in enumerate(s2):
            if self._has_wildcards(seg):
                # we have reached the point where its the end
                key = seg.replace('{*','').replace('}','')
                value = s1[i:]
                value = "/".join(value)
                break
            else:
                # we are till the same path
                if i > len(s1) or seg != s1[i]:
                    return None 
       
        return {key: value}

    def resolve_route(self, path: str, method: str):
        if method not in self.routes.keys():
            return f"{method} not allowed. Only allowed methods are {','.join(list(self.routes.keys()))}"
        exact_match =  self.routes[method].get(path)
        if exact_match:
            # /api/v1/users/
            return {'handler':exact_match, 'params': None}
        # check if it matches the pattern
        # /api/v1/users/{id} --> it will store as that
        for route in self.param_routes[method]:
            pattern = route['pattern']
            handler = route['handler']
            params = self._get_match_params(path, pattern)
            if params:
                return {'handler': handler, 'params': params} 

        for route in self.wildcard_routes[method]:
            pattern = route['pattern']
            handler = route['handler']
            params = self._get_wildcard_params(path, pattern)
            if params != None:
                return {'handler': handler, 'params': params} 
        
        
        return '404 - Not Found'



if __name__ == "__main__":
    r = Router()
    r.add_route('/api/v1/files/{*path}', 'GET', lambda: print("fetching file path"))
    x = r.resolve_route('/api/v1/files/docs/folders/word1.txt', 'GET')
    print(x)
    x = r.resolve_route('/api/v1/files/', 'GET')
    print(x)

"""
# Comprehensive test suite for your router
if __name__ == "__main__":
    print("🚀 Testing Your Router Implementation\n")
    
    router = Router()
    
    # Sample handlers
    def list_users():
        return "📋 Listing all users"
    
    def get_user():
        return "👤 Getting specific user"
    
    def create_user():
        return "✨ Creating new user"
    
    def get_user_posts():
        return "📝 Getting user's posts"
    
    def get_specific_post():
        return "📖 Getting specific post"
    
    # Register routes
    print("📝 Registering routes...")
    router.add_route('/api/v1/users', 'GET', list_users)
    router.add_route('/api/v1/users', 'POST', create_user)
    router.add_route('/api/v1/users/{id}', 'GET', get_user)
    router.add_route('/api/v1/users/{user_id}/posts', 'GET', get_user_posts)
    router.add_route('/api/v1/users/{user_id}/posts/{post_id}', 'GET', get_specific_post)
    
    print("\n" + "="*50)
    print("🧪 TESTING ROUTE RESOLUTION")
    print("="*50)
    
    # Test cases
    test_cases = [
        # Static routes
        ('GET', '/api/v1/users', "Static route - list users"),
        ('POST', '/api/v1/users', "Static route - create user"),
        
        # Single parameter
        ('GET', '/api/v1/users/123', "Single parameter - get user 123"),
        ('GET', '/api/v1/users/alice', "Single parameter - get user alice"),
        
        # Multiple parameters
        ('GET', '/api/v1/users/123/posts', "Multiple params - user 123's posts"),
        ('GET', '/api/v1/users/456/posts/789', "Multiple params - user 456's post 789"),
        
        # Edge cases
        ('GET', '/api/v1/nonexistent', "No matching route"),
        ('PUT', '/api/v1/users', "Unsupported method"),
        ('GET', '/api/v1/users/123/posts/456/comments', "Too many segments"),
        ('GET', '/api/v1', "Too few segments"),
    ]
    
    for method, path, description in test_cases:
        print(f"\n🎯 Test: {description}")
        print(f"   Request: {method} {path}")
        
        result = router.resolve_route(path, method)
        
        if isinstance(result, dict):
            # Successful match
            print(f"   ✅ Match found!")
            print(f"   📄 Handler: {result['handler'].__name__}")
            print(f"   📋 Params: {result['params']}")
            print(f"   🎬 Result: {result['handler']()}")
        elif isinstance(result, str) and "not allowed" in result:
            # Method not supported
            print(f"   ⚠️  Method issue: {result}")
        elif result == '404 - Not Found':
            # No route match
            print(f"   ❌ No match: {result}")
        else:
            # Static route (direct handler)
            print(f"   ✅ Static match!")
            print(f"   📄 Handler: {result.__name__}")
            print(f"   🎬 Result: {result()}")
    
    print("\n" + "="*50)
    print("📊 ROUTER STATISTICS")
    print("="*50)
    print(f"Static routes (GET): {len(router.routes['GET'])}")
    print(f"Static routes (POST): {len(router.routes['POST'])}")
    print(f"Parameter routes (GET): {len(router.param_routes['GET'])}")
    print(f"Parameter routes (POST): {len(router.param_routes['POST'])}")
    
    print(f"\n📋 Registered static routes:")
    for method, routes in router.routes.items():
        for path in routes.keys():
            print(f"   {method} {path}")
    
    print(f"\n📋 Registered parameter routes:")
    for method, routes in router.param_routes.items():
        for route in routes:
            print(f"   {method} {route['pattern']}")
    
    print("\n🎉 All tests completed!")

"""