"""
Tests for the Domain class
"""

import pytest
from unittest.mock import patch, Mock
import linkbar
from linkbar.domain import Domain


class TestDomain:
    
    def setup_method(self):
        """Reset module state before each test"""
        linkbar.api_key = "test_api_key"
        linkbar.base_url = "https://api.linkbar.co/"
    
    def test_domain_initialization(self):
        """Test Domain object initialization with API data"""
        data = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'connected',
            'organization': 'org456',
            'homepage_redirect_url': 'https://example.com',
            'nonexistent_link_redirect_url': 'https://example.com/404'
        }
        
        domain = Domain(data)
        
        assert domain.id == 'dom123'
        assert domain.name == 'example.com'
        assert domain.is_custom is True
        assert domain.status == 'connected'
        assert domain.organization == 'org456'
        assert domain.homepage_redirect_url == 'https://example.com'
        assert domain.nonexistent_link_redirect_url == 'https://example.com/404'
    
    def test_domain_initialization_minimal_data(self):
        """Test Domain initialization with minimal data"""
        data = {
            'name': 'linkb.ar'
        }
        
        domain = Domain(data)
        
        assert domain.id is None
        assert domain.name == 'linkb.ar'
        assert domain.is_custom is False  # Default value
        assert domain.status is None
        assert domain.organization is None
        assert domain.homepage_redirect_url is None
        assert domain.nonexistent_link_redirect_url is None
    
    def test_domain_str_representation(self):
        """Test Domain string representation"""
        data = {'name': 'example.com'}
        domain = Domain(data)
        assert str(domain) == "Domain(example.com)"
    
    def test_domain_repr_representation(self):
        """Test Domain repr representation"""
        data = {
            'id': 'dom123',
            'name': 'example.com',
            'status': 'connected'
        }
        domain = Domain(data)
        assert repr(domain) == "Domain(id=dom123, name=example.com, status=connected)"
    
    @patch('linkbar._request')
    def test_create_basic_domain(self, mock_request):
        """Test creating a basic custom domain"""
        mock_request.return_value = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'pending',
            'organization': 'org456'
        }
        
        domain = Domain.create(name='example.com')
        
        mock_request.assert_called_once_with('POST', 'domains/', {'name': 'example.com'})
        assert isinstance(domain, Domain)
        assert domain.name == 'example.com'
        assert domain.id == 'dom123'
        assert domain.is_custom is True
    
    @patch('linkbar._request')
    def test_create_domain_with_redirects(self, mock_request):
        """Test creating a domain with redirect URLs"""
        mock_request.return_value = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'pending',
            'organization': 'org456',
            'homepage_redirect_url': 'https://example.com',
            'nonexistent_link_redirect_url': 'https://example.com/404'
        }
        
        domain = Domain.create(
            name='example.com',
            homepage_redirect_url='https://example.com',
            nonexistent_link_redirect_url='https://example.com/404'
        )
        
        expected_data = {
            'name': 'example.com',
            'homepage_redirect_url': 'https://example.com',
            'nonexistent_link_redirect_url': 'https://example.com/404'
        }
        mock_request.assert_called_once_with('POST', 'domains/', expected_data)
        assert domain.homepage_redirect_url == 'https://example.com'
        assert domain.nonexistent_link_redirect_url == 'https://example.com/404'
    
    @patch('linkbar._request')
    def test_list_domains(self, mock_request):
        """Test listing domains"""
        mock_request.return_value = {
            'results': [
                {
                    'id': 'dom123',
                    'name': 'example.com',
                    'is_custom': True,
                    'status': 'connected'
                },
                {
                    'id': 'dom456',
                    'name': 'linkb.ar',
                    'is_custom': False,
                    'status': 'connected'
                }
            ]
        }
        
        domains = Domain.list()
        
        mock_request.assert_called_once_with('GET', 'domains/', {})
        assert len(domains) == 2
        assert all(isinstance(domain, Domain) for domain in domains)
        assert domains[0].id == 'dom123'
        assert domains[1].id == 'dom456'
    
    @patch('linkbar._request')
    def test_list_domains_with_search(self, mock_request):
        """Test listing domains with search parameter"""
        mock_request.return_value = {'results': []}
        
        Domain.list(search='example')
        
        mock_request.assert_called_once_with('GET', 'domains/', {'q': 'example'})
    
    @patch('linkbar._request')
    def test_list_domains_custom_only(self, mock_request):
        """Test listing only custom domains"""
        mock_request.return_value = {'results': []}
        
        Domain.list(is_custom=True)
        
        mock_request.assert_called_once_with('GET', 'domains/', {'is_custom': 'true'})
    
    @patch('linkbar._request')
    def test_list_domains_all_parameters(self, mock_request):
        """Test listing domains with all parameters"""
        mock_request.return_value = {'results': []}
        
        Domain.list(search='example', is_custom=False)
        
        expected_params = {'q': 'example', 'is_custom': 'false'}
        mock_request.assert_called_once_with('GET', 'domains/', expected_params)
    
    @patch('linkbar._request')
    def test_list_domains_non_paginated_response(self, mock_request):
        """Test listing domains with non-paginated response"""
        mock_request.return_value = [
            {
                'id': 'dom123',
                'name': 'example.com',
                'is_custom': True,
                'status': 'connected'
            }
        ]
        
        domains = Domain.list()
        
        assert len(domains) == 1
        assert domains[0].id == 'dom123'
    
    @patch('linkbar._request')
    def test_get_domain(self, mock_request):
        """Test getting a specific domain"""
        mock_request.return_value = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'connected'
        }
        
        domain = Domain.get('dom123')
        
        mock_request.assert_called_once_with('GET', 'domains/dom123/')
        assert isinstance(domain, Domain)
        assert domain.id == 'dom123'
    
    @patch('linkbar._request')
    def test_update_domain(self, mock_request):
        """Test updating a domain"""
        # Initial domain data
        initial_data = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'connected',
            'homepage_redirect_url': 'https://example.com'
        }
        
        # Updated domain data
        updated_data = {
            'id': 'dom123',
            'name': 'newexample.com',
            'is_custom': True,
            'status': 'connected',
            'homepage_redirect_url': 'https://newexample.com',
            'nonexistent_link_redirect_url': 'https://newexample.com/404'
        }
        
        mock_request.return_value = updated_data
        
        domain = Domain(initial_data)
        updated_domain = domain.update(
            name='newexample.com',
            homepage_redirect_url='https://newexample.com',
            nonexistent_link_redirect_url='https://newexample.com/404'
        )
        
        expected_data = {
            'name': 'newexample.com',
            'homepage_redirect_url': 'https://newexample.com',
            'nonexistent_link_redirect_url': 'https://newexample.com/404'
        }
        mock_request.assert_called_once_with('PATCH', 'domains/dom123/', expected_data)
        assert updated_domain is domain  # Should return the same instance
        assert domain.name == 'newexample.com'
        assert domain.nonexistent_link_redirect_url == 'https://newexample.com/404'
    
    def test_update_domain_without_id(self):
        """Test updating a domain without ID raises error"""
        data = {
            'name': 'example.com',
            'is_custom': True
        }
        
        domain = Domain(data)
        
        with pytest.raises(ValueError, match="Cannot update domain without ID"):
            domain.update(name='newexample.com')
    
    @patch('linkbar._request')
    def test_delete_domain(self, mock_request):
        """Test deleting a domain"""
        data = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'connected'
        }
        
        domain = Domain(data)
        domain.delete()
        
        mock_request.assert_called_once_with('DELETE', 'domains/dom123/')
    
    def test_delete_domain_without_id(self):
        """Test deleting a domain without ID raises error"""
        data = {
            'name': 'example.com',
            'is_custom': True
        }
        
        domain = Domain(data)
        
        with pytest.raises(ValueError, match="Cannot delete domain without ID"):
            domain.delete()
    
    @patch('linkbar._request')
    def test_refresh_domain(self, mock_request):
        """Test refreshing a domain's data"""
        initial_data = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'pending'
        }
        
        refreshed_data = {
            'id': 'dom123',
            'name': 'example.com',
            'is_custom': True,
            'status': 'connected'  # Status changed
        }
        
        mock_request.return_value = refreshed_data
        
        domain = Domain(initial_data)
        refreshed_domain = domain.refresh()
        
        mock_request.assert_called_once_with('GET', 'domains/dom123/')
        assert refreshed_domain is domain  # Should return the same instance
        assert domain.status == 'connected'
    
    def test_refresh_domain_without_id(self):
        """Test refreshing a domain without ID raises error"""
        data = {
            'name': 'example.com',
            'is_custom': True
        }
        
        domain = Domain(data)
        
        with pytest.raises(ValueError, match="Cannot refresh domain without ID"):
            domain.refresh()