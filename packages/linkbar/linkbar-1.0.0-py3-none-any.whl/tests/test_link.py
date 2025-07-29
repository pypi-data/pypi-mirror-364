"""
Tests for the Link class
"""

import pytest
from unittest.mock import patch, Mock
import linkbar
from linkbar.link import Link


class TestLink:
    
    def setup_method(self):
        """Reset module state before each test"""
        linkbar.api_key = "test_api_key"
        linkbar.base_url = "https://api.linkbar.co/"
    
    def test_link_initialization(self):
        """Test Link object initialization with API data"""
        data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': {'name': 'linkb.ar'},
            'tags': ['test', 'example'],
            'created_at': '2024-01-01T00:00:00Z',
            'click_count': 42
        }
        
        link = Link(data)
        
        assert link.id == 'abc123'
        assert link.long_url == 'https://example.com'
        assert link.keyword == 'test-link'
        assert link.domain_name == 'linkb.ar'
        assert link.tags == ['test', 'example']
        assert link.created_at == '2024-01-01T00:00:00Z'
        assert link.click_count == 42
        assert link.short_url == 'https://linkb.ar/test-link'
        assert link.pretty_url == 'linkb.ar/test-link'
    
    def test_link_initialization_with_string_domain(self):
        """Test Link initialization when domain is a string"""
        data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        
        assert link.domain_name == 'linkb.ar'
        assert link.short_url == 'https://linkb.ar/test-link'
        assert link.pretty_url == 'linkb.ar/test-link'
    
    def test_link_initialization_no_domain(self):
        """Test Link initialization when domain is None"""
        data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': None,
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        
        assert link.domain_name is None
        assert link.short_url is None
        assert link.pretty_url is None
    
    def test_link_str_representation(self):
        """Test Link string representation"""
        data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        assert str(link) == "Link(https://linkb.ar/test-link -> https://example.com)"
    
    def test_link_repr_representation(self):
        """Test Link repr representation"""
        data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        assert repr(link) == "Link(id=abc123, short_url=https://linkb.ar/test-link, long_url=https://example.com)"
    
    @patch('linkbar._request')
    def test_create_basic_link(self, mock_request):
        """Test creating a basic link"""
        mock_request.return_value = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'xyz789',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link.create(long_url='https://example.com')
        
        mock_request.assert_called_once_with('POST', 'links/', {'long_url': 'https://example.com'})
        assert isinstance(link, Link)
        assert link.long_url == 'https://example.com'
        assert link.id == 'abc123'
    
    @patch('linkbar._request')
    def test_create_link_with_all_parameters(self, mock_request):
        """Test creating a link with all parameters"""
        mock_request.return_value = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'custom-link',
            'domain': 'linkb.ar',
            'tags': ['marketing', 'campaign'],
            'click_count': 0
        }
        
        link = Link.create(
            long_url='https://example.com',
            domain='linkb.ar',
            keyword='custom-link',
            tags=['marketing', 'campaign']
        )
        
        expected_data = {
            'long_url': 'https://example.com',
            'domain': 'linkb.ar',
            'keyword': 'custom-link',
            'tags': ['marketing', 'campaign']
        }
        mock_request.assert_called_once_with('POST', 'links/', expected_data)
        assert link.keyword == 'custom-link'
        assert link.tags == ['marketing', 'campaign']
    
    @patch('linkbar._request')
    def test_list_links(self, mock_request):
        """Test listing links"""
        mock_request.return_value = {
            'results': [
                {
                    'id': 'abc123',
                    'long_url': 'https://example.com',
                    'keyword': 'link1',
                    'domain': 'linkb.ar',
                    'tags': [],
                    'click_count': 5
                },
                {
                    'id': 'def456',
                    'long_url': 'https://test.com',
                    'keyword': 'link2',
                    'domain': 'linkb.ar',
                    'tags': ['test'],
                    'click_count': 10
                }
            ]
        }
        
        links = Link.list()
        
        mock_request.assert_called_once_with('GET', 'links/', {})
        assert len(links) == 2
        assert all(isinstance(link, Link) for link in links)
        assert links[0].id == 'abc123'
        assert links[1].id == 'def456'
    
    @patch('linkbar._request')
    def test_list_links_with_search(self, mock_request):
        """Test listing links with search parameter"""
        mock_request.return_value = {'results': []}
        
        Link.list(search='marketing')
        
        mock_request.assert_called_once_with('GET', 'links/', {'q': 'marketing'})
    
    @patch('linkbar._request')
    def test_list_links_non_paginated_response(self, mock_request):
        """Test listing links with non-paginated response"""
        mock_request.return_value = [
            {
                'id': 'abc123',
                'long_url': 'https://example.com',
                'keyword': 'link1',
                'domain': 'linkb.ar',
                'tags': [],
                'click_count': 5
            }
        ]
        
        links = Link.list()
        
        assert len(links) == 1
        assert links[0].id == 'abc123'
    
    @patch('linkbar._request')
    def test_get_link(self, mock_request):
        """Test getting a specific link"""
        mock_request.return_value = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 42
        }
        
        link = Link.get('abc123')
        
        mock_request.assert_called_once_with('GET', 'links/abc123/')
        assert isinstance(link, Link)
        assert link.id == 'abc123'
    
    @patch('linkbar._request')
    def test_update_link(self, mock_request):
        """Test updating a link"""
        # Initial link data
        initial_data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 42
        }
        
        # Updated link data
        updated_data = {
            'id': 'abc123',
            'long_url': 'https://newexample.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': ['updated'],
            'click_count': 42
        }
        
        mock_request.return_value = updated_data
        
        link = Link(initial_data)
        updated_link = link.update(long_url='https://newexample.com', tags=['updated'])
        
        mock_request.assert_called_once_with('PATCH', 'links/abc123/', {
            'long_url': 'https://newexample.com',
            'tags': ['updated']
        })
        assert updated_link is link  # Should return the same instance
        assert link.long_url == 'https://newexample.com'
        assert link.tags == ['updated']
    
    def test_update_link_without_id(self):
        """Test updating a link without ID raises error"""
        data = {
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        
        with pytest.raises(ValueError, match="Cannot update link without ID"):
            link.update(long_url='https://newexample.com')
    
    @patch('linkbar._request')
    def test_delete_link(self, mock_request):
        """Test deleting a link"""
        data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        link.delete()
        
        mock_request.assert_called_once_with('DELETE', 'links/abc123/')
    
    def test_delete_link_without_id(self):
        """Test deleting a link without ID raises error"""
        data = {
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        
        with pytest.raises(ValueError, match="Cannot delete link without ID"):
            link.delete()
    
    @patch('linkbar._request')
    def test_refresh_link(self, mock_request):
        """Test refreshing a link's data"""
        initial_data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 42
        }
        
        refreshed_data = {
            'id': 'abc123',
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 100  # Updated click count
        }
        
        mock_request.return_value = refreshed_data
        
        link = Link(initial_data)
        refreshed_link = link.refresh()
        
        mock_request.assert_called_once_with('GET', 'links/abc123/')
        assert refreshed_link is link  # Should return the same instance
        assert link.click_count == 100
    
    def test_refresh_link_without_id(self):
        """Test refreshing a link without ID raises error"""
        data = {
            'long_url': 'https://example.com',
            'keyword': 'test-link',
            'domain': 'linkb.ar',
            'tags': [],
            'click_count': 0
        }
        
        link = Link(data)
        
        with pytest.raises(ValueError, match="Cannot refresh link without ID"):
            link.refresh()