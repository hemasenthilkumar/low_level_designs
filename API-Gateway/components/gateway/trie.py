# gateway/core/router.py

from typing import Dict, List, Optional, Callable, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RouteMatch:
    """Result of a successful route match."""
    handler: Callable
    path_params: Dict[str, str]
    route_pattern: str


class TrieNode:
    """
    A node in the HTTP route Trie.

    Key differences from a word Trie:
    1. Stores path segments, not individual characters
    2. Has different types of children (static, param, wildcard)
    3. Stores handlers per HTTP method
    """

    def __init__(self):
        # Static children: exact string matches like "api", "users"
        # Fast O(1) lookup using dictionary
        self.static_children: Dict[str, 'TrieNode'] = {}

        # Parameter child: matches segments like {id}, {user_id}
        # Only ONE parameter child per node (avoids ambiguity)
        self.param_child: Optional['TrieNode'] = None
        self.param_name: Optional[str] = None  # Store the parameter name

        # Wildcard child: matches {*path} - captures all remaining segments
        # Only ONE wildcard per node, always at the end
        self.wildcard_child: Optional['TrieNode'] = None
        self.wildcard_name: Optional[str] = None

        # Handlers: different HTTP methods can have different handlers
        # GET /users might list users, POST /users might create a user
        self.handlers: Dict[HTTPMethod, Callable] = {}

        # Metadata for debugging and metrics
        self.route_pattern: str = ""  # Original pattern like "/api/users/{id}"
        self.is_endpoint: bool = False  # True if this node has any handlers


class RouteTrie:
    """
    HTTP Route Trie for efficient path matching.

    Handles three types of path segments:
    1. Static: /api/users - exact match
    2. Parameter: /api/users/{id} - match any value, extract as parameter
    3. Wildcard: /files/{*path} - match all remaining segments
    """

    def __init__(self):
        self.root = TrieNode()

    def add_route(self, method: HTTPMethod, pattern: str, handler: Callable) -> None:
        """
        Register a new route pattern with its handler.

        Examples:
        - add_route(HTTPMethod.GET, "/api/users", list_users)
        - add_route(HTTPMethod.GET, "/api/users/{id}", get_user)
        - add_route(HTTPMethod.POST, "/api/users", create_user)
        """
        # Parse the pattern into segments
        segments = self._parse_pattern(pattern)

        # Navigate/create the trie path
        current = self.root
        for segment in segments:
            current = self._get_or_create_child(current, segment)

        # Store the handler at the final node
        current.handlers[method] = handler
        current.route_pattern = pattern
        current.is_endpoint = True

        print(f"Registered: {method.value} {pattern}")

    def match(self, method: HTTPMethod, path: str) -> Optional[RouteMatch]:
        """
        Find a matching route for the given method and path.

        Returns RouteMatch with handler and extracted parameters,
        or None if no match found.
        """
        # Parse the path into segments (similar to pattern parsing)
        segments = self._parse_path(path)

        # Try to match using recursive traversal
        params = {}
        handler = self._match_recursive(self.root, segments, 0, params)

        if handler and method in handler.handlers:
            return RouteMatch(
                handler=handler.handlers[method],
                path_params=params.copy(),
                route_pattern=handler.route_pattern
            )

        return None

    def _parse_pattern(self, pattern: str) -> List[str]:
        """
        Parse a route pattern into segments.

        "/api/users/{id}" -> ["api", "users", "{id}"]
        """
        # Remove leading/trailing slashes and split
        clean_pattern = pattern.strip('/')
        if not clean_pattern:
            return []
        return clean_pattern.split('/')

    def _parse_path(self, path: str) -> List[str]:
        """
        Parse a request path into segments.

        "/api/users/123" -> ["api", "users", "123"]
        """
        # Same logic as pattern parsing
        clean_path = path.strip('/')
        if not clean_path:
            return []
        return clean_path.split('/')

    def _get_or_create_child(self, node: TrieNode, segment: str) -> TrieNode:
        """
        Get or create the appropriate child node for a pattern segment.

        Determines if segment is static, parameter, or wildcard.
        """
        if segment.startswith('{') and segment.endswith('}'):
            # This is a parameter or wildcard segment
            param_name = segment[1:-1]  # Remove { and }

            if param_name.startswith('*'):
                # Wildcard segment like {*path}
                wildcard_name = param_name[1:]  # Remove the *
                if node.wildcard_child is None:
                    node.wildcard_child = TrieNode()
                    node.wildcard_name = wildcard_name
                return node.wildcard_child
            else:
                # Parameter segment like {id}
                if node.param_child is None:
                    node.param_child = TrieNode()
                    node.param_name = param_name
                return node.param_child
        else:
            # Static segment like "api" or "users"
            if segment not in node.static_children:
                node.static_children[segment] = TrieNode()
            return node.static_children[segment]

    def _match_recursive(self, node: TrieNode, segments: List[str],
                        index: int, params: Dict[str, str]) -> Optional[TrieNode]:
        """
        Recursively match path segments against the trie.

        Uses backtracking to try different node types in priority order:
        1. Static children (highest priority - exact matches)
        2. Parameter children (medium priority - extract value)
        3. Wildcard children (lowest priority - catch remaining)
        """
        # Base case: we've consumed all path segments
        if index >= len(segments):
            return node if node.is_endpoint else None

        current_segment = segments[index]

        # Try 1: Static match (highest priority)
        if current_segment in node.static_children:
            result = self._match_recursive(
                node.static_children[current_segment],
                segments,
                index + 1,
                params
            )
            if result:
                return result

        # Try 2: Parameter match (medium priority)
        if node.param_child is not None:
            # Save current params state for backtracking
            old_params = params.copy()
            # Extract the parameter value
            params[node.param_name] = current_segment

            result = self._match_recursive(
                node.param_child,
                segments,
                index + 1,
                params
            )
            if result:
                return result

            # Backtrack: restore params if this path didn't work
            params.clear()
            params.update(old_params)

        # Try 3: Wildcard match (lowest priority, matches everything remaining)
        if node.wildcard_child is not None:
            # Wildcard captures all remaining segments
            remaining_path = '/'.join(segments[index:])
            params[node.wildcard_name] = remaining_path

            # Wildcard should lead to an endpoint (end of pattern)
            if node.wildcard_child.is_endpoint:
                return node.wildcard_child

        # No match found
        return None


class HTTPRouter:
    """
    Main HTTP Router that provides a clean public API.

    This is what your gateway middleware will interact with.
    """

    def __init__(self):
        self.trie = RouteTrie()
        self.routes_count = 0

    def add_route(self, method: str, pattern: str, handler: Callable) -> None:
        """
        Public API to add a route.

        Args:
            method: HTTP method as string ("GET", "POST", etc.)
            pattern: Route pattern like "/api/users/{id}"
            handler: Function to handle matching requests
        """
        try:
            http_method = HTTPMethod(method.upper())
            self.trie.add_route(http_method, pattern, handler)
            self.routes_count += 1
        except ValueError:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def match(self, method: str, path: str) -> Optional[RouteMatch]:
        """
        Public API to match a request.

        Args:
            method: HTTP method as string ("GET", "POST", etc.)
            path: Request path like "/api/users/123"

        Returns:
            RouteMatch with handler and extracted parameters, or None
        """
        try:
            http_method = HTTPMethod(method.upper())
            return self.trie.match(http_method, path)
        except ValueError:
            return None  # Invalid HTTP method

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics for monitoring."""
        return {
            "total_routes": self.routes_count,
            "supported_methods": [method.value for method in HTTPMethod]
        }


# Example usage and testing
if __name__ == "__main__":
    # Create router
    router = HTTPRouter()

    # Sample handlers
    def list_users(): return "List all users"
    def get_user(): return "Get specific user"
    def create_user(): return "Create new user"
    def get_user_posts(): return "Get user's posts"
    def serve_files(): return "Serve static files"

    # Register routes
    router.add_route("GET", "/api/users", list_users)
    router.add_route("POST", "/api/users", create_user)
    router.add_route("GET", "/api/users/{id}", get_user)
    router.add_route("GET", "/api/users/{id}/posts", get_user_posts)
    router.add_route("GET", "/files/{*path}", serve_files)

    # Test matching
    test_cases = [
        ("GET", "/api/users"),
        ("POST", "/api/users"),
        ("GET", "/api/users/123"),
        ("GET", "/api/users/123/posts"),
        ("GET", "/files/docs/readme.txt"),
        ("GET", "/api/nonexistent"),  # Should not match
        ("DELETE", "/api/users/123"),  # Method not registered
    ]

    print("\n--- Testing Route Matching ---")
    for method, path in test_cases:
        match = router.match(method, path)
        if match:
            print(f"✅ {method} {path}")
            print(f"   Handler: {match.handler.__name__}")
            print(f"   Params: {match.path_params}")
            print(f"   Pattern: {match.route_pattern}")
        else:
            print(f"❌ {method} {path} - No match")
        print()

    print(f"Router stats: {router.get_stats()}")