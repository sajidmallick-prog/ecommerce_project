from django.contrib.auth.decorators import user_passes_test

def admin_or_staff_required(view_func):
    def check_user(user):
        return user.is_authenticated and (user.is_staff or user.is_superuser)
    return user_passes_test(check_user)(view_func)