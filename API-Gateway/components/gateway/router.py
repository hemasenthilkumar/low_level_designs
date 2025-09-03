

class Router:

    def __init__(self):
        self.routes = {
            'GET': {},
            'POST': {}
        }

    def add_route(self, path, method, handler):
        if method not in self.routes.keys():
            return f"{method} not allowed. Only allowed methods are {','.join(list(self.routes.keys()))}"
        self.routes[method][path] = handler

    def resolve_route(self, path: str, method: str):
        if method not in self.routes.keys():
            return f"{method} not allowed. Only allowed methods are {','.join(list(self.routes.keys()))}"
        return self.routes[method].get(path)

if __name__ == "__main__":
    r = Router()
    r.add_route('/api/v1/users', 'GET', lambda : print("Hello User!"))
    r.add_route('/api/v1/login', 'GET', lambda : print("Logged In!"))
    r.add_route('/api/v1/logout', 'GET', lambda : print("Logged Out!"))
    r.resolve_route('/api/v1/users', 'GET')()
    r.resolve_route('/api/v1/login', 'GET')()
    r.resolve_route('/api/v1/logout', 'GET')()
    print(r.add_route('/api/v1/add', 'PUT', lambda : print("Logged Out!")))
    r.resolve_route('/api/v1/add', 'GET')