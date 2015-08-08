from django.contrib.auth.models import AnonymousUser, User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase, RequestFactory

from checkouts.views import (
    PilotList,
    PilotDetail,
)

import helper

class PilotViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='pass'
        )

    def test_PilotList(self):
        url = reverse('pilot_list')
        request = self.factory.get(url)

        # Anonymous
        request.user = AnonymousUser()
        response = PilotList.as_view()(request)
        self.assertEqual(response.status_code, 302)

        # Not anonymous, no pilots
        request.user = self.regular_user
        response = PilotList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['pilot_list']), 0)

        # Not anonymous, two pilots
        request.user = self.regular_user
        helper.create_pilot(username='kimpilot')
        helper.create_pilot(username='sampilot')
        response = PilotList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['pilot_list']), 2)

    def test_PilotDetail(self):
        url = reverse('pilot_detail', kwargs={'username':'no_exist'})
        request = self.factory.get(url)

        # Anonymous
        request.user = AnonymousUser()
        response = PilotDetail.as_view()(request, username='no_exist')
        self.assertEqual(response.status_code, 302)

        # Not anonymous, pilot does not exist
        request.user = self.regular_user
        with self.assertRaises(Http404):
            _ = PilotDetail.as_view()(request, username='no_exist')

        # Not anonymous, pilot exists
        request.user = self.regular_user
        helper.create_pilot(username='kimpilot')
        response = PilotDetail.as_view()(request, username='kimpilot')
        self.assertIsNotNone(response.context_data['pilot'])
        self.assertIsNotNone(response.context_data['checkouts'])

