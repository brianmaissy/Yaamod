from django.test import TestCase
from rest_framework import status
from django.test.client import Client
import os


class RegularContentTypeClient(Client):
    def patch(self, path, data='', content_type='application/json',
              follow=False, secure=False, **extra):
        """
        this function is here just to change the odd thing that django's client uses octet content_type which returns
        415 for all our views
        """
        return super().patch(path, data, content_type, follow, secure, **extra)


class ViewTest(TestCase):
    USERNAME = 'john'
    PASSWORD = 'doe'
    EMAIL = 'jd@gmail.com'
    client_class = RegularContentTypeClient

    def get_url(self, url, method, data=None, expected_status=status.HTTP_200_OK):
        data = data or {}
        response = getattr(self.client, method)(url, data)
        if isinstance(expected_status, list):
            self.assertIn(response.status_code, expected_status)
        else:
            self.assertEqual(response.status_code, expected_status)
        return response

    def add_user(self, username=USERNAME, password=PASSWORD, synagogue=None, login=False, should_succeed=True):
        json = {
            'username': username,
            'password': password,
            'email': self.EMAIL
        }
        expected_status = status.HTTP_201_CREATED if should_succeed else status.HTTP_401_UNAUTHORIZED

        self.get_url('/user', 'post', json, expected_status)
        if login:
            self.login(username, password)

    def login(self, username=USERNAME, password=PASSWORD):
        self.get_url('/login', 'post', {
            'username': username,
            'password': password
        })

    def logout(self):
        self.get_url('/logout', 'post')

    def check_unauthorized(self, url, method, data=None):
        unauthorized_statuses = [status.HTTP_401_UNAUTHORIZED]
        self.get_url(url, method, data, unauthorized_statuses)

    def check_perms(self, url, method, data=None, expected_status=status.HTTP_200_OK):
        """
        check that a view can be accessed while logged in, and unaccessible while not.
        """
        self.check_unauthorized(url, method, data)
        self.login()
        response = self.get_url(url, method, data, expected_status)
        self.logout()
        self.check_unauthorized(url, method, data)
        return response

    def add_synagogue(self):
        self.get_url('/synagogue', 'post', {'name': os.urandom(8)}, status.HTTP_201_CREATED)


class TestSynagogueView(ViewTest):
    def test_synagogue(self):
        self.add_user()

        self.check_perms('/synagogue', 'post', {'name': 'abc'}, status.HTTP_201_CREATED)
        self.check_perms('/synagogue/1', 'patch', {'name': 'def'})

        # get should work while logged out
        self.logout()
        response = self.get_url('/synagogue/1', 'get')
        self.assertEqual(response.json(), {'name': 'def'})


class TestPerms(ViewTest):
    def start_test(self):
        self.add_user(login=True)
        self.add_synagogue()
        self.logout()

    def do_update(self, should_succeed=True):
        """
        update synagogue with pk=1.
        we don't test that the update work, it's just a random view to check if a given user has perms to this synagogue
        """
        # if should succeed is False, 400 will return since the person will not be in the queryset
        expected_status = status.HTTP_200_OK if should_succeed else status.HTTP_401_UNAUTHORIZED
        self.get_url('/synagogue/1', 'patch', {'name': 'def'}, expected_status)

    def test_unauthorized_user(self):
        """
        make sure that a new user that is not on admins can't get the synagogue
        """
        self.start_test()
        self.add_user('john1', 'doe1', login=True)
        self.do_update(False)
        self.logout()

    def test_two_synagogue_users(self):
        """
        make sure that we can add new user to the synagogue
        :return:
        """
        self.start_test()
        self.login()
        self.add_user('john1', 'doe1')
        self.logout()  # logout from the first user
        self.login('john1', 'doe1')
        self.do_update(True)
        self.logout()


class TestPersonView(ViewTest):
    def start_test(self):
        self.add_user(login=True)
        self.add_synagogue()

    def add_person(self, first_name=None, last_name=None):
        json = {
            'first_name': first_name or os.urandom(8),
            'last_name': last_name or os.urandom(8)
        }

        self.get_url('/person', 'post', data=json, expected_status=status.HTTP_201_CREATED)

    def test_add_person(self):
        self.start_test()
        self.add_person()

    def test_get_only_your_people(self):
        self.start_test()
        # add person to first synagogue
        self.add_person(first_name='a')
        self.logout()

        self.add_user('john1', 'doe1', login=True)
        self.add_synagogue()
        self.add_person(first_name='b')
        self.logout()

        self.login()
        response = self.get_url('/person', method='get')
        self.check_response_is_person(response, 'a', is_list=True)

    def test_cant_reach_person(self):
        self.start_test()
        self.add_person(first_name='a')
        self.logout()

        self.add_user('john1', 'doe1', login=True)
        self.add_synagogue()
        self.get_url('/person/1', method='get', expected_status=status.HTTP_404_NOT_FOUND)

    def check_response_is_person(self, response, person_first_name, is_list=False):
        if is_list:
            self.assertTrue(isinstance(response.json(), list))
            self.assertEqual(len(response.json()), 1)
            person = response.json()[0]
        else:
            person = response.json()
        self.assertEqual(person['first_name'], person_first_name)

    def test_get_specific_person(self):
        self.start_test()
        self.add_person(first_name='a')
        self.add_person(first_name='b')
        response = self.get_url('/person/1', method='get')
        self.check_response_is_person(response, 'a')
