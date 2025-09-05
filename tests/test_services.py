"""Service layer tests"""
import pytest
from unittest.mock import Mock, patch


def test_import_service():
    """Test that we can import the service"""
    try:
        from src.media_picker.services.media_service import MediaItemService
        assert MediaItemService is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import MediaItemService: {e}")


class TestMediaItemService:
    """Test MediaItemService functionality"""
    
    def test_service_creation(self):
        """Test creating a service instance"""
        from unittest.mock import Mock
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        with patch('src.media_picker.services.media_service.MediaItemRepository'):
            service = MediaItemService(mock_db)
            assert service is not None
            assert hasattr(service, 'repository')
            assert service.db == mock_db

    def test_get_all_items_no_filter(self):
        """Test getting all items without filter"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_item = Mock()
        mock_item.id = "1"
        mock_item.title = "Test"
        mock_item.type = "game"
        mock_item.platform = None
        mock_item.cover_url = None
        mock_item.tags = []
        mock_item.status = "active"
        mock_item.added_at = None
        mock_item.created_at = None
        mock_item.updated_at = None
        
        mock_repo.get_all.return_value = [mock_item]
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            result = service.get_all_items()
            
            assert len(result) == 1
            assert result[0].id == "1"
            mock_repo.get_all.assert_called_once()

    def test_get_all_items_with_filter(self):
        """Test getting all items with filter"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_item = Mock()
        mock_item.id = "1"
        mock_item.title = "Test"
        mock_item.type = "game"
        mock_item.platform = None
        mock_item.cover_url = None
        mock_item.tags = []
        mock_item.status = "active"
        mock_item.added_at = None
        mock_item.created_at = None
        mock_item.updated_at = None
        
        mock_repo.get_filtered.return_value = [mock_item]
        mock_filter = Mock()
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            result = service.get_all_items(mock_filter)
            
            assert len(result) == 1
            assert result[0].id == "1"
            mock_repo.get_filtered.assert_called_once_with(mock_filter)

    def test_get_item_by_id_success(self):
        """Test getting item by ID successfully"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_item = Mock()
        mock_item.id = "1"
        mock_item.title = "Test"
        mock_item.type = "game"
        mock_item.platform = None
        mock_item.cover_url = None
        mock_item.tags = []
        mock_item.status = "active"
        mock_item.added_at = None
        mock_item.created_at = None
        mock_item.updated_at = None
        
        mock_repo.get_by_id.return_value = mock_item
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            result = service.get_item_by_id("1")
            
            assert result.id == "1"
            mock_repo.get_by_id.assert_called_once_with("1")

    def test_get_item_by_id_not_found(self):
        """Test getting item by ID when not found"""
        from src.media_picker.services.media_service import MediaItemService
        from src.media_picker.core.exceptions import ItemNotFoundError
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            
            with pytest.raises(ItemNotFoundError):
                service.get_item_by_id("nonexistent")

    def test_create_item_success(self):
        """Test creating item successfully"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_item = Mock()
        mock_item.id = "1"
        mock_item.title = "Test"
        mock_item.type = "game"
        mock_item.platform = None
        mock_item.cover_url = None
        mock_item.tags = []
        mock_item.status = "active"
        mock_item.added_at = None
        mock_item.created_at = None
        mock_item.updated_at = None
        
        mock_repo.create.return_value = mock_item
        mock_data = Mock()
        mock_data.model_dump.return_value = {"title": "Test", "type": "game"}
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            result = service.create_item(mock_data)
            
            assert result.id == "1"
            mock_repo.create.assert_called_once_with({"title": "Test", "type": "game"})

    def test_delete_item_success(self):
        """Test deleting item successfully"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_repo.delete.return_value = True
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            result = service.delete_item("1")
            
            assert result is True
            mock_repo.delete.assert_called_once_with("1")

    def test_spin_wheel_with_items(self):
        """Test spinning wheel with available items"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_item = Mock()
        mock_item.id = "1"
        mock_item.title = "Test"
        mock_item.type = "game"
        mock_item.platform = None
        mock_item.cover_url = None
        mock_item.tags = []
        mock_item.status = "active"
        mock_item.added_at = None
        mock_item.created_at = None
        mock_item.updated_at = None
        
        mock_repo.get_filtered.return_value = [mock_item]
        mock_request = Mock()
        mock_request.type = "game"
        mock_request.tags = None
        mock_request.include_archived = False
        mock_request.status = None
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class, \
             patch('src.media_picker.services.media_service.MediaItemFilter') as mock_filter_class, \
             patch('src.media_picker.services.media_service.random.choice') as mock_choice:
            
            mock_repo_class.return_value = mock_repo
            mock_choice.return_value = mock_item
            
            service = MediaItemService(mock_db)
            result = service.spin_wheel(mock_request)
            
            assert result.winner is not None
            assert result.total_pool_size == 1

    def test_get_statistics_success(self):
        """Test getting statistics successfully"""
        from src.media_picker.services.media_service import MediaItemService
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_repo.count_total.return_value = 10
        mock_repo.count_by_status.side_effect = [5, 3, 2]  # active, done, archived
        mock_repo.get_by_type.side_effect = [[1, 2, 3], [4, 5]]  # games, movies
        
        with patch('src.media_picker.services.media_service.MediaItemRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_repo
            service = MediaItemService(mock_db)
            result = service.get_statistics()
            
            assert result["total"] == 10
            assert result["active"] == 5
            assert result["done"] == 3
            assert result["archived"] == 2
            assert result["games"] == 3
            assert result["movies"] == 2
