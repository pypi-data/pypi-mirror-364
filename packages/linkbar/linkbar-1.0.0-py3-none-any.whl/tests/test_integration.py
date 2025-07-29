"""
Integration tests for the Linkbar SDK

These tests require a real API key and will make actual API calls.
Set LINKBAR_TEST_API_KEY environment variable to run these tests.

Run with: pytest tests/test_integration.py -m integration
"""

import os
import pytest
import linkbar
from linkbar.link import Link
from linkbar.domain import Domain


# Skip all integration tests if API key is not provided
pytestmark = pytest.mark.skipif(
    not os.getenv('LINKBAR_TEST_API_KEY'),
    reason="LINKBAR_TEST_API_KEY environment variable not set"
)


class TestLinkbarIntegration:
    
    def setup_method(self):
        """Setup for each test"""
        linkbar.api_key = os.getenv('LINKBAR_TEST_API_KEY')
        # Clean up any test links/domains from previous runs
        self.cleanup_test_resources()
    
    def teardown_method(self):
        """Cleanup after each test"""
        self.cleanup_test_resources()
    
    def cleanup_test_resources(self):
        """Clean up test resources"""
        try:
            # Clean up test links
            links = Link.list(search='test-linkbar-sdk')
            for link in links:
                if 'test-linkbar-sdk' in (link.keyword or ''):
                    try:
                        link.delete()
                    except:
                        pass
            
            # Clean up test domains
            domains = Domain.list(search='test-linkbar-sdk')
            for domain in domains:
                if 'test-linkbar-sdk' in domain.name:
                    try:
                        domain.delete()
                    except:
                        pass
        except:
            # Ignore cleanup errors
            pass
    
    @pytest.mark.integration
    def test_create_and_manage_link_lifecycle(self):
        """Test complete link lifecycle: create, read, update, delete"""
        # Create a link
        link = Link.create(
            long_url='https://example.com',
            keyword='test-linkbar-sdk-lifecycle',
            tags=['test', 'sdk']
        )
        
        assert link.id is not None
        assert link.long_url == 'https://example.com'
        assert link.keyword == 'test-linkbar-sdk-lifecycle'
        assert 'test' in link.tags
        assert 'sdk' in link.tags
        assert link.short_url is not None
        
        # Read the link back
        retrieved_link = Link.get(link.id)
        assert retrieved_link.id == link.id
        assert retrieved_link.long_url == link.long_url
        assert retrieved_link.keyword == link.keyword
        
        # Update the link
        updated_link = link.update(
            long_url='https://updated-example.com',
            tags=['updated', 'test']
        )
        assert updated_link.long_url == 'https://updated-example.com'
        assert 'updated' in updated_link.tags
        
        # Refresh to get latest data
        refreshed_link = link.refresh()
        assert refreshed_link.long_url == 'https://updated-example.com'
        
        # Delete the link
        link.delete()
        
        # Verify it's deleted (should raise an error)
        with pytest.raises(Exception):  # Should be 404 or similar
            Link.get(link.id)
    
    @pytest.mark.integration
    def test_list_links_with_search(self):
        """Test listing and searching links"""
        # Create a few test links
        link1 = Link.create(
            long_url='https://example.com/page1',
            keyword='test-linkbar-sdk-list-1',
            tags=['list-test']
        )
        link2 = Link.create(
            long_url='https://example.com/page2',
            keyword='test-linkbar-sdk-list-2',
            tags=['list-test']
        )
        
        try:
            # List all links
            all_links = Link.list()
            assert len(all_links) >= 2
            assert any(l.id == link1.id for l in all_links)
            assert any(l.id == link2.id for l in all_links)
            
            # Search for specific links
            search_results = Link.list(search='test-linkbar-sdk-list')
            assert len(search_results) >= 2
            found_ids = [l.id for l in search_results]
            assert link1.id in found_ids
            assert link2.id in found_ids
            
        finally:
            # Cleanup
            link1.delete()
            link2.delete()
    
    @pytest.mark.integration
    def test_list_domains(self):
        """Test listing domains"""
        domains = Domain.list()
        assert len(domains) > 0
        
        # Should have at least the default linkbar domains
        domain_names = [d.name for d in domains]
        assert any('linkb.ar' in name or 'linkbar' in name for name in domain_names)
        
        # Test filtering custom domains only
        custom_domains = Domain.list(is_custom=True)
        # All returned domains should be custom
        for domain in custom_domains:
            assert domain.is_custom is True
    
    @pytest.mark.integration
    def test_error_handling(self):
        """Test error handling with invalid operations"""
        # Test with invalid API key
        original_key = linkbar.api_key
        linkbar.api_key = "invalid_key_123"
        
        try:
            with pytest.raises(Exception):  # Should be 401 Unauthorized
                Link.create(long_url='https://example.com')
        finally:
            linkbar.api_key = original_key
        
        # Test getting non-existent link
        with pytest.raises(Exception):  # Should be 404 Not Found
            Link.get('nonexistent_id_123')
        
        # Test creating link with invalid URL
        with pytest.raises(Exception):  # Should be 400 Bad Request
            Link.create(long_url='not_a_valid_url')
    
    @pytest.mark.integration
    def test_link_properties_and_computed_fields(self):
        """Test that link properties are correctly populated"""
        link = Link.create(
            long_url='https://example.com/test',
            keyword='test-linkbar-sdk-props'
        )
        
        try:
            assert link.id is not None
            assert link.long_url == 'https://example.com/test'
            assert link.keyword == 'test-linkbar-sdk-props'
            assert link.short_url is not None
            assert link.pretty_url is not None
            assert link.domain_name is not None
            assert link.created_at is not None
            assert isinstance(link.click_count, int)
            assert link.click_count >= 0
            
            # Test string representations
            str_repr = str(link)
            assert link.short_url in str_repr
            assert link.long_url in str_repr
            
            repr_repr = repr(link)
            assert link.id in repr_repr
            assert link.short_url in repr_repr
            
        finally:
            link.delete()