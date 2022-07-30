from django.contrib.auth.mixins import UserPassesTestMixin


class PermissionRequiredMixin(UserPassesTestMixin):
    required_permission = 'corvee.view_persoon'

    def check_user(self, user):
        if user.is_authenticated and user.has_perm(self.required_permission) and user.is_active:
            return True
        return False

    def test_func(self):
        return self.check_user(self.request.user)
