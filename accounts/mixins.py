
from django.contrib.auth.mixins import AccessMixin


class ViewPermissionMixin(AccessMixin):
    """Verify that the current user is authenticated or the current user is student"""

    def dispatch(self, request, *args, **kwargs):
        try:
            student = request.session['student']  # 1 True
        except KeyError:
            student = None

        if not request.user.is_authenticated and student == None:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
