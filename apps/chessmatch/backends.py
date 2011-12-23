from django_auth_ldap.backend import LDAPBackend
from django.conf import settings
from django.contrib.auth.models import Group

from chessmatch.models import Player

class PlayerLDAPBackend(LDAPBackend):

    def get_or_create_user(self, username, ldap_user):
        user, created = super(PlayerLDAPBackend, self).get_or_create_user(username, ldap_user)
        if created: # create player profile the first time they log in
        	player, player_created = Player.objects.get_or_create(user=user)

        return (user, created)
