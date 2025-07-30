import unittest
import sys
from unittest.mock import patch, MagicMock
from gh_feed import app


class TestMultiSelect(unittest.TestCase):
    """Test cases for multi-select event type filtering"""

    def test_event_types_list(self):
        """Test that EVENT_TYPES contains expected event types"""
        event_names = [event[0] for event in app.EVENT_TYPES]
        expected_events = [
            "PushEvent", "IssuesEvent", "PullRequestEvent", "WatchEvent",
            "CreateEvent", "ForkEvent", "ReleaseEvent", "DeleteEvent",
            "PullRequestReviewCommentEvent"
        ]
        for event in expected_events:
            self.assertIn(event, event_names)
    
    def test_display_activity_multiple_filters(self):
        """Test display_activity with multiple filter types"""
        events = [
            {"type": "PushEvent", "repo": {"name": "test/repo1"}, 
             "created_at": "2024-06-27T12:00:00Z", "payload": {"commits": [1]}},
            {"type": "IssuesEvent", "repo": {"name": "test/repo2"}, 
             "created_at": "2024-06-27T12:01:00Z", "payload": {"action": "opened"}},
            {"type": "WatchEvent", "repo": {"name": "test/repo3"}, 
             "created_at": "2024-06-27T12:02:00Z", "payload": {}}
        ]
        
        # Test filtering with multiple types
        with patch('builtins.print') as mock_print:
            app.display_activity(events, ["PushEvent", "IssuesEvent"])
            
            # Should display 2 events (PushEvent and IssuesEvent)
            printed_output = str(mock_print.call_args_list)
            self.assertIn("Pushed", printed_output)
            self.assertIn("Opened", printed_output)
            self.assertNotIn("Starred", printed_output)  # WatchEvent should be filtered out
    
    def test_display_activity_single_filter_backward_compatibility(self):
        """Test that single string filter still works (backward compatibility)"""
        events = [
            {"type": "PushEvent", "repo": {"name": "test/repo1"}, 
             "created_at": "2024-06-27T12:00:00Z", "payload": {"commits": [1]}},
            {"type": "IssuesEvent", "repo": {"name": "test/repo2"}, 
             "created_at": "2024-06-27T12:01:00Z", "payload": {"action": "opened"}}
        ]
        
        with patch('builtins.print') as mock_print:
            app.display_activity(events, "PushEvent")
            
            printed_output = str(mock_print.call_args_list)
            self.assertIn("Pushed", printed_output)
            self.assertNotIn("Opened", printed_output)

    @patch('gh_feed.app.UNIX_LIKE', None)  # Simulate no keyboard support
    def test_multi_select_fallback(self):
        """Test multi-select fallback when no keyboard support available"""
        with patch('builtins.input', return_value="PushEvent,IssuesEvent"):
            with patch('builtins.print') as mock_print:
                result = app.multi_select_event_types()
                self.assertEqual(result, ["PushEvent", "IssuesEvent"])
                
        # Test empty input fallback
        with patch('builtins.input', return_value=""):
            result = app.multi_select_event_types()
            self.assertIsNone(result)

    @patch('gh_feed.app.clear_screen')
    @patch('gh_feed.app.get_key')
    @patch('gh_feed.app.UNIX_LIKE', True)
    def test_multi_select_keyboard_navigation(self, mock_get_key, mock_clear):
        """Test keyboard navigation in multi-select"""
        # Simulate: down arrow, space (select), enter (confirm)
        mock_get_key.side_effect = ['\x1b[B', ' ', '\r']
        
        with patch('builtins.print'):
            result = app.multi_select_event_types()
            # Should select the second item (IssuesEvent)
            self.assertEqual(result, ["IssuesEvent"])

    @patch('gh_feed.app.clear_screen')
    @patch('gh_feed.app.get_key')
    @patch('gh_feed.app.UNIX_LIKE', True)
    def test_multi_select_select_all(self, mock_get_key, mock_clear):
        """Test 'Select All' functionality"""
        # Navigate to "Select All" option and select it
        select_all_position = len(app.EVENT_TYPES)  # Last position
        keys = ['\x1b[B'] * select_all_position + [' ', '\r']  # Navigate down to "Select All", space, enter
        mock_get_key.side_effect = keys
        
        with patch('builtins.print'):
            result = app.multi_select_event_types()
            # Select All should return None (meaning all events)
            self.assertIsNone(result)

    @patch('gh_feed.app.clear_screen')
    @patch('gh_feed.app.get_key')
    @patch('gh_feed.app.UNIX_LIKE', True)
    def test_multi_select_escape_cancel(self, mock_get_key, mock_clear):
        """Test ESC key canceling multi-select"""
        mock_get_key.side_effect = ['\x1b']  # ESC key
        
        with patch('builtins.print'):
            result = app.multi_select_event_types()
            self.assertIsNone(result)

    def test_interactive_mode_with_username(self):
        """Test interactive mode with pre-provided username"""
        with patch('builtins.input', side_effect=['n', '', '1', 'n']):  # no token, empty token, option 1, no export
            with patch('gh_feed.app.fetch_user_activity', return_value=[]):
                with patch('builtins.print') as mock_print:
                    app.interactive_mode('testuser')
                    
                    # Check that username was used
                    printed_output = str(mock_print.call_args_list)
                    self.assertIn('testuser', printed_output)

    def test_main_interactive_with_username(self):
        """Test main() function with username --interactive argument"""
        with patch.object(sys, 'argv', ['gh-feed', 'octocat', '--interactive']):
            with patch('gh_feed.app.interactive_mode') as mock_interactive:
                app.main()
                mock_interactive.assert_called_once_with('octocat')

    def test_main_interactive_backward_compatibility(self):
        """Test main() function with --interactive only (backward compatibility)"""
        with patch.object(sys, 'argv', ['gh-feed', '--interactive']):
            with patch('gh_feed.app.interactive_mode') as mock_interactive:
                app.main()
                mock_interactive.assert_called_once_with(None)


if __name__ == "__main__":
    unittest.main()