from django.test import TestCase

from core.permissions import _conductor_owns_furgon, _apoderado_owns_student


class BadUser:
    def __getattr__(self, name):
        # Always raise to simulate broken attribute access
        raise RuntimeError("bad access")


class BadObj:
    def __getattr__(self, name):
        raise RuntimeError("broken")


class PermissionsHelpersTests(TestCase):
    def test_conductor_ownership_handles_exception_and_returns_false(self):
        bad_user = BadUser()
        bad_obj = BadObj()
        # Should not raise, should return False
        self.assertFalse(_conductor_owns_furgon(bad_user, bad_obj))

    def test_apoderado_ownership_handles_exception_and_returns_false(self):
        bad_user = BadUser()
        bad_obj = BadObj()
        self.assertFalse(_apoderado_owns_student(bad_user, bad_obj))
