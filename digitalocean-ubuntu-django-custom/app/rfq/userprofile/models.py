from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from utils.utils import Enum


class Profile(models.Model):
    """The profile for a user.
    """

    class Genders(Enum):
        MALE = 'm'
        FEMALE = 'f'

    class UserTypes(Enum):
        USER = 'user' 
        ADMIN = 'admin'
        ADMINISTRATOR = 'superadmin'
        OTHERUSER = 'otheruser'
        APPROVER = 'approver'

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=1, blank=True, choices=Genders.as_user_friendly(), default='-')
    dob = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=UserTypes.as_user_friendly(), default=UserTypes.USER)

    def __unicode__(self):
        return '{0} - {1}'.format(self.user, self.type)

    def IsTypeX():
        return self.type


def create_profile(sender, instance, created, raw, **kwargs):
    """Fleshes out the profile for the newly created user"""
    if created:
        profile = Profile(user=instance)
        profile.type = Profile.UserTypes.USER
        profile.save()


def update_user_permissions(sender, instance, created, raw, **kwargs):
    """Modifies the user permissions of the profile user"""
    
    user = instance.user
    
    if instance.type == Profile.UserTypes.ADMIN:        
        user.is_staff = True

    elif instance.type == Profile.UserTypes.USER:
        user.is_staff = True

    elif instance.type == Profile.UserTypes.ADMINISTRATOR:
        user.is_staff = True
        user.is_superuser = True

    elif instance.type == Profile.UserTypes.APPROVER:
        user.is_staff = False
        user.is_superuser = False

    elif instance.type == Profile.UserTypes.OTHERUSER:
        user.is_staff = False
        user.is_superuser = False

    user.save()


post_save.connect(create_profile, sender=User,
    dispatch_uid='userprofile.models.create_profile')


post_save.connect(update_user_permissions, sender=Profile,
    dispatch_uid='userprofile.models.update_user_permissions')