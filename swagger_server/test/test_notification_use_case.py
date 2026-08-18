from unittest import TestCase
from unittest.mock import Mock

from swagger_server.exception.custom_error_exception import CustomAPIException
from swagger_server.uses_cases.notification_use_case import NotificationUseCase


class TestNotificationUseCase(TestCase):

    def setUp(self):
        self.repository = Mock()
        self.use_case = NotificationUseCase(self.repository)

    def test_update_read_status(self):
        expected = {
            "id_notification": "notification-id",
            "is_read": True,
            "read_at": "2026-08-18T10:00:00",
        }
        self.repository.update_read_status.return_value = expected

        result = self.use_case.update_read_status(
            "notification-id", {"is_read": True}, "internal", "external"
        )

        self.assertEqual(expected, result)
        self.repository.update_read_status.assert_called_once_with(
            "notification-id", True, "internal", "external"
        )

    def test_update_read_status_requires_boolean(self):
        with self.assertRaises(CustomAPIException) as context:
            self.use_case.update_read_status(
                "notification-id", {"is_read": "true"}, "internal", "external"
            )

        self.assertEqual(400, context.exception.status_code)
        self.repository.update_read_status.assert_not_called()

    def test_update_read_status_returns_not_found(self):
        self.repository.update_read_status.return_value = None

        with self.assertRaises(CustomAPIException) as context:
            self.use_case.update_read_status(
                "notification-id", {"is_read": False}, "internal", "external"
            )

        self.assertEqual(404, context.exception.status_code)

    def test_mark_all_as_read(self):
        user_id = "7f9c3a1e-2b4d-4e5f-8a6b-1c2d3e4f5a6b"
        self.repository.mark_all_as_read.return_value = 3

        result = self.use_case.mark_all_as_read(
            {"user_id": user_id}, "internal", "external"
        )

        self.assertEqual({"user_id": user_id, "updated_count": 3}, result)
        repository_user_id = self.repository.mark_all_as_read.call_args.args[0]
        self.assertEqual(user_id, str(repository_user_id))

    def test_mark_all_as_read_requires_valid_user_id(self):
        with self.assertRaises(CustomAPIException) as context:
            self.use_case.mark_all_as_read(
                {"user_id": "invalid-user-id"}, "internal", "external"
            )

        self.assertEqual(400, context.exception.status_code)
        self.repository.mark_all_as_read.assert_not_called()

    def test_delete_notification(self):
        expected = {
            "id_notification": "notification-id",
            "is_deleted": True,
        }
        self.repository.delete_notification.return_value = expected

        result = self.use_case.delete_notification(
            "notification-id", "internal", "external"
        )

        self.assertEqual(expected, result)
        self.repository.delete_notification.assert_called_once_with(
            "notification-id", "internal", "external"
        )

    def test_delete_notification_returns_not_found(self):
        self.repository.delete_notification.return_value = None

        with self.assertRaises(CustomAPIException) as context:
            self.use_case.delete_notification(
                "notification-id", "internal", "external"
            )

        self.assertEqual(404, context.exception.status_code)
