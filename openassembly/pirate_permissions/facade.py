
from pirate_permissions.models import PermissionsGroup, Permission
from pirate_reputation.models import Reputation


def canI(user, permission_str, component, generic_obj=None):
    '''
    This method is used to test whether a particular has permission to undertake a particular
    action within a particular system component.  Both the permission string and the
    component string are arbitrarily set by the user, the intent being to allow permissions
    to be controlled at the template-level at the discression of the site designer.

    The generic_obj argument changes the behavior of the method slightly by allowing the
    user to use permissions that are marked as being "component membership required".
    In these cases, the user's membership in generic_obj is tested before it is determined
    whether the user has the permission in question.

    First, set up the test user, and give it a reputation score.

    >>> from django.contrib.auth.models import User
    >>> from pirate_reputation.models import Reputation
    >>> user = User.objects.create_user("temp_user","temp@user.net")
    >>> Reputation.objects.register_event(100, user)

    Second, set up the permissions that the user cannot meet.

    >>> from pirate_permissions.models import PermissionsGroup, Permission, ReputationSpec
    >>> component = "consensus"

    >>> perm_str1 = "update_vote"
    >>> group1 = PermissionsGroup(name="Voters", description="People who can vote.")
    >>> group1.save(); 
    >>> perm1  = Permission(name=perm_str1, component=component, permissions_group=group1)
    >>> perm1.save(); 
    >>> spec1  = ReputationSpec(threshold=150, permissions_group=group1)
    >>> spec1.save()

    Third, set up the permissions that the user will be able to meet.

    >>> perm_str2 = "read_vote"
    >>> group2 = PermissionsGroup(name="Viewers", description="People who can view votes.")
    >>> group2.save(); 
    >>> perm2  = Permission(name=perm_str2, component=component, permissions_group=group2)
    >>> perm2.save(); 
    >>> spec2  = ReputationSpec(threshold=50, permissions_group=group2)
    >>> spec2.save()

    >>> canI(user, perm_str1, component)
    False
    >>> canI(user, perm_str2, component)
    True

    '''
    '''

    Finally, clean everything up.

    >>> user.delete(); 
    >>> group1.delete(); perm1.delete(); spec1.delete()
    >>> group2.delete(); perm2.delete(); spec2.delete()
    >>> ReputationEvent.objects.clear()
    >>> Reputation.objects.clear()
    >>> ReputationDimension.objects.clear()
    '''

    permissions = Permission.objects.filter(name=permission_str, component=component)
    for permission in permissions:

        ### In the case that the permission is only granted to members of the generic_obj,
        ### i.e. if permission.component_membership_required is set to True, then
        ### this permission is only valid when the user is a member of the specified object.
        ### If the user is a member, the user still needs to be tested according to standard
        ### criteria

        if permission.component_membership_required:
            if generic_obj is None:
                continue
            elif not hasattr(generic_obj, "is_member"):
                continue
            elif not generic_obj.is_member(user):
                continue

        group = permission.permissions_group

        ### First, test to se if the user is explicitly a member of the group
        ### TODO: this is not implemented because ManyToOne is not supported by django-nonrel

        #if group.user_set.filter(id=user.id).count() > 0:
        #    return True
        
        ### If that is not good enough, then test to see if the user exceeds one of the 
        ### thresholds specified.

        for spec in group.reputationspec_set.all():
            score = Reputation.objects.get_user_score(user, spec.dimension)
            if score.score > spec.threshold:
                return True
    
    # If none of the permissions work, then the answer is false
    return False

