from usersprofile.models import Profile

def vp_only(fn):
    """
    Make sure the user is requesting this view as a vp.
    """

    def wrapper(self, *args, **kwargs):
        # Make sure the credentials are valid
        if self.user.is_authenticated():
            try:
                profile = Profile.objects.get(user=self.user)
            except:
                raise "User profile doesn't exist"

            # Check levels and admin status
            if not self.user.profile.type == Profile.UserTypes.VP:
                raise "Permission Denied"
            return fn(self, *args, **kwargs)     
        raise "Authentication Failure"

    return wrapper