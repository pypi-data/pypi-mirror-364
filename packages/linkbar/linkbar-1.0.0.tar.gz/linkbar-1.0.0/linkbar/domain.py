"""
Linkbar Domain API
"""

from typing import Optional, List, Dict, Any


class Domain:
    """
    Represents a Linkbar domain with all its properties and methods.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a Domain instance from API response data.
        
        Args:
            data: Dictionary containing domain data from API
        """
        self._data = data
        
        # Set properties from data
        self.id = data.get('id')
        self.name = data.get('name')
        self.is_custom = data.get('is_custom', False)
        self.status = data.get('status')
        self.organization = data.get('organization')
        self.homepage_redirect_url = data.get('homepage_redirect_url')
        self.nonexistent_link_redirect_url = data.get('nonexistent_link_redirect_url')
    
    def __str__(self) -> str:
        return f"Domain({self.name})"
    
    def __repr__(self) -> str:
        return f"Domain(id={self.id}, name={self.name}, status={self.status})"
    
    @classmethod
    def create(cls, name: str, homepage_redirect_url: Optional[str] = None,
               nonexistent_link_redirect_url: Optional[str] = None) -> 'Domain':
        """
        Create a new custom domain.
        
        Args:
            name: Domain name (e.g., "example.com")
            homepage_redirect_url: URL to redirect to when accessing domain root (optional)
            nonexistent_link_redirect_url: URL to redirect to for non-existent links (optional)
            
        Returns:
            Domain instance representing the created domain
            
        Raises:
            ValueError: If API key is not configured
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        data = {'name': name}
        
        if homepage_redirect_url:
            data['homepage_redirect_url'] = homepage_redirect_url
        if nonexistent_link_redirect_url:
            data['nonexistent_link_redirect_url'] = nonexistent_link_redirect_url
            
        response_data = _request('POST', 'domains/', data)
        return cls(response_data)
    
    @classmethod
    def list(cls, search: Optional[str] = None, is_custom: Optional[bool] = None) -> List['Domain']:
        """
        List existing domains.
        
        Args:
            search: Search query to filter domains (optional)
            is_custom: Filter by custom domains only (optional)
            
        Returns:
            List of Domain instances
            
        Raises:
            ValueError: If API key is not configured
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        params = {}
        if search:
            params['q'] = search
        if is_custom is not None:
            params['is_custom'] = str(is_custom).lower()
            
        response_data = _request('GET', 'domains/', params)
        
        # Handle both paginated and non-paginated responses
        if 'results' in response_data:
            domains_data = response_data['results']
        else:
            domains_data = response_data if isinstance(response_data, list) else [response_data]
            
        return [cls(domain_data) for domain_data in domains_data]
    
    @classmethod
    def get(cls, domain_id: str) -> 'Domain':
        """
        Get a specific domain by ID.
        
        Args:
            domain_id: The ID of the domain to retrieve
            
        Returns:
            Domain instance representing the retrieved domain
            
        Raises:
            ValueError: If API key is not configured
            requests.HTTPError: If the API request fails
        """
        from . import _request
            
        response_data = _request('GET', f'domains/{domain_id}/')
        return cls(response_data)
    
    def update(self, name: Optional[str] = None, homepage_redirect_url: Optional[str] = None,
               nonexistent_link_redirect_url: Optional[str] = None) -> 'Domain':
        """
        Update this domain.
        
        Args:
            name: Domain name (optional)
            homepage_redirect_url: URL to redirect to when accessing domain root (optional)
            nonexistent_link_redirect_url: URL to redirect to for non-existent links (optional)
            
        Returns:
            Updated Domain instance
            
        Raises:
            ValueError: If API key is not configured or domain has no ID
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        if not self.id:
            raise ValueError("Cannot update domain without ID.")
        
        data = {}
        if name is not None:
            data['name'] = name
        if homepage_redirect_url is not None:
            data['homepage_redirect_url'] = homepage_redirect_url
        if nonexistent_link_redirect_url is not None:
            data['nonexistent_link_redirect_url'] = nonexistent_link_redirect_url
            
        response_data = _request('PATCH', f'domains/{self.id}/', data)
        
        # Update this instance with new data
        self.__init__(response_data)
        return self
    
    def delete(self) -> None:
        """
        Delete this domain.
        
        Raises:
            ValueError: If API key is not configured or domain has no ID
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        if not self.id:
            raise ValueError("Cannot delete domain without ID.")
            
        _request('DELETE', f'domains/{self.id}/')
    
    def refresh(self) -> 'Domain':
        """
        Refresh this domain's data from the API.
        
        Returns:
            This Domain instance with updated data
            
        Raises:
            ValueError: If API key is not configured or domain has no ID
            requests.HTTPError: If the API request fails
        """
        from . import _request
        
        if not self.id:
            raise ValueError("Cannot refresh domain without ID.")
            
        response_data = _request('GET', f'domains/{self.id}/')
        self.__init__(response_data)
        return self