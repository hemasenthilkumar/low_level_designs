

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

    def _has_params(self, path):
        return '{' in path and '}' in path

    def add_route(self, path, method, handler):
        # /api/v1/users/{id}
        # /api/v1/users/{id}/posts/{pid}
        if method not in self.routes.keys():
            return f"{method} not allowed. Only allowed methods are {','.join(list(self.routes.keys()))}"

        if self._has_params(path):
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


    def resolve_route(self, path: str, method: str):
        if method not in self.routes.keys():
            return f"{method} not allowed. Only allowed methods are {','.join(list(self.routes.keys()))}"
        exact_match =  self.routes[method].get(path)
        if exact_match:
            # /api/v1/users/
            return exact_match
        # check if it matches the pattern
        # /api/v1/users/{id} --> it will store as that
        for route in self.param_routes[method]:
            pattern = route['pattern']
            handler = route['handler']
            params = self._get_match_params(path, pattern)
            if params:
                return {'handler': handler, 'params': params} 
        return '404 - Not Found'




if __name__ == "__main__":
    r = Router()
    
    # Static routes
    r.add_route('/api/v1/users', 'GET', lambda: "List all users")
    
    # Parameter routes
    r.add_route('/api/v1/users/{id}', 'GET', lambda: "Get specific user")
    r.add_route('/api/v1/users/{user_id}/posts/{post_id}', 'GET', lambda: "Get user's specific post")
    
    print("\n=== Testing Route Resolution ===")
    
    # Test static route
    result1 = r.resolve_route('/api/v1/users', 'GET')
    print(f"Static route: {result1}")
    
    # Test single parameter
    result2 = r.resolve_route('/api/v1/users/123', 'GET')
    print(f"Single param: {result2}")
    if isinstance(result2, dict):
        print(f"Handler result: {result2['handler']()}")
        print(f"Extracted params: {result2['params']}")
    
    # Test multiple parameters
    result3 = r.resolve_route('/api/v1/users/456/posts/789', 'GET')
    print(f"Multiple params: {result3}")
    if isinstance(result3, dict):
        print(f"Handler result: {result3['handler']()}")
        print(f"Extracted params: {result3['params']}")
    
    # Test no match
    result4 = r.resolve_route('/api/v1/nonexistent', 'GET')
    print(f"No match: {result4}")