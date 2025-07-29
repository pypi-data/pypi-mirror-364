"""
Linkbar Link API
"""

from typing import Optional, List, Dict, Any


class Link:
    """
    Represents a Linkbar short link with all its properties and methods.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a Link instance from API response data.
        
        Args:
            data: Dictionary containing link data from API
        """
        self._data = data
        
        # Set properties from data
        self.id = data.get('id')
        self.long_url = data.get('long_url')
        self.keyword = data.get('keyword')
        self.domain = data.get('domain')
        self.tags = data.get('tags', [])
        self.created_at = data.get('created_at')
        self.click_count = data.get('click_count', 0)
        
        # Computed properties
        if isinstance(self.domain, dict):
            self.domain_name = self.domain.get('name')
            self.short_url = f"https://{self.domain_name}/{self.keyword}"
            self.pretty_url = f"{self.domain_name}/{self.keyword}"
        elif isinstance(self.domain, str):
            self.domain_name = self.domain
            self.short_url = f"https://{self.domain}/{self.keyword}"
            self.pretty_url = f"{self.domain}/{self.keyword}"
        else:
            self.domain_name = None
            self.short_url = None
            self.pretty_url = None
    
    def __str__(self) -> str:
        return f"Link({self.short_url} -> {self.long_url})"
    
    def __repr__(self) -> str:
        return f"Link(id={self.id}, short_url={self.short_url}, long_url={self.long_url})"
    
    @classmethod
    def create(cls, long_url: str, domain: Optional[str] = None, keyword: Optional[str] = None, 
               tags: Optional[List[str]] = None) -> 'Link':
        """
        Create a new short link.
        
        Args:
            long_url: The URL to be shortened
            domain: Domain to use for the short link (optional)
            keyword: Custom keyword for the short link (optional)
            tags: List of tags to associate with the link (optional)
            
        Returns:
            Link instance representing the created link
            
        Raises:
            ValueError: If API key is not configured
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        data = {'long_url': long_url}
        
        if domain:
            data['domain'] = domain
        if keyword:
            data['keyword'] = keyword
        if tags:
            data['tags'] = tags
            
        response_data = _request('POST', 'links/', data)
        return cls(response_data)
    
    @classmethod
    def list(cls, search: Optional[str] = None) -> List['Link']:
        """
        List existing links.
        
        Args:
            search: Search query to filter links (optional)
            
        Returns:
            List of Link instances
            
        Raises:
            ValueError: If API key is not configured
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        params = {}
        if search:
            params['q'] = search
            
        response_data = _request('GET', 'links/', params)
        
        # Handle both paginated and non-paginated responses
        if 'results' in response_data:
            links_data = response_data['results']
        else:
            links_data = response_data if isinstance(response_data, list) else [response_data]
            
        return [cls(link_data) for link_data in links_data]
    
    @classmethod
    def get(cls, link_id: str) -> 'Link':
        """
        Get a specific link by ID.
        
        Args:
            link_id: The ID of the link to retrieve
            
        Returns:
            Link instance representing the retrieved link
            
        Raises:
            ValueError: If API key is not configured
            requests.HTTPError: If the API request fails
        """
        from . import _request
            
        response_data = _request('GET', f'links/{link_id}/')
        return cls(response_data)
    
    def update(self, long_url: Optional[str] = None, domain: Optional[str] = None,
               keyword: Optional[str] = None, tags: Optional[List[str]] = None) -> 'Link':
        """
        Update this link.
        
        Args:
            long_url: The URL to be shortened (optional)
            domain: Domain to use for the short link (optional)
            keyword: Custom keyword for the short link (optional)
            tags: List of tags to associate with the link (optional)
            
        Returns:
            Updated Link instance
            
        Raises:
            ValueError: If API key is not configured or link has no ID
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        if not self.id:
            raise ValueError("Cannot update link without ID.")
        
        data = {}
        if long_url is not None:
            data['long_url'] = long_url
        if domain is not None:
            data['domain'] = domain
        if keyword is not None:
            data['keyword'] = keyword
        if tags is not None:
            data['tags'] = tags
            
        response_data = _request('PATCH', f'links/{self.id}/', data)
        
        # Update this instance with new data
        self.__init__(response_data)
        return self
    
    def delete(self) -> None:
        """
        Delete this link.
        
        Raises:
            ValueError: If API key is not configured or link has no ID
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        if not self.id:
            raise ValueError("Cannot delete link without ID.")
            
        _request('DELETE', f'links/{self.id}/')
    
    def refresh(self) -> 'Link':
        """
        Refresh this link's data from the API.
        
        Returns:
            This Link instance with updated data
            
        Raises:
            ValueError: If API key is not configured or link has no ID
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        if not self.id:
            raise ValueError("Cannot refresh link without ID.")
            
        response_data = _request('GET', f'links/{self.id}/')
        self.__init__(response_data)
        return self