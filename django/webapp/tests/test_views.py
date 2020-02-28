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
        if synagogue is not None:
            json['synagogue'] = synagogue
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
        unauthorized_statuses = [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
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
        self.get_url('/synagogue/1', 'patch', {'name': 'def'},
                     status.HTTP_200_OK if should_succeed else status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user(self):
        """
        make sure that a new user that is not on admins can't get the synagogue
        """
        self.start_test()
        self.add_user('john1', 'doe1', login=True)
        self.do_update(False)
        self.logout()

    def test_cant_add_synagogue_user(self):
        """
        make sure that unauthorized user can't create a user in a synagogue's admins
        """
        self.start_test()
        self.add_user('john1', 'doe1', synagogue=1, should_succeed=False)

    def test_add_to_admins(self):
        """
        make sure that we can add new user to admins and get synagogue
        :return:
        """
        self.start_test()
        self.login()
        self.add_user('john1', 'doe1', synagogue=1)
        self.logout()  # logout from the first user
        self.login('john1', 'doe1')
        self.do_update(True)
        self.logout()


class TestPersonView(ViewTest):
    def start_test(self):
        self.add_user(login=True)
        self.add_synagogue()

    def add_person(self, synagogue_pk=1, url_pk=1, should_succeed=True, first_name=None, last_name=None):
        json = {
            'synagogue': synagogue_pk,
            'first_name': first_name or os.urandom(8),
            'last_name': last_name or os.urandom(8)
        }
        url = '/synagogue/{}/person'.format(url_pk)
        if should_succeed:
            self.get_url(url, 'post', data=json, expected_status=status.HTTP_201_CREATED)
        else:
            self.check_unauthorized(url, 'post', data=json)

    def test_add_person(self):
        self.start_test()
        self.add_person()

    def test_different_pk(self):
        self.start_test()
        self.add_synagogue()
        self.add_person(1, 2, False)
        self.add_person(2, 1, False)

    def test_get_only_your_people(self):
        self.start_test()
        self.add_synagogue()
        self.add_person(1, 1, first_name='a')
        self.add_person(2, 2, first_name='b')
        response = self.get_url('/synagogue/1/person', method='get')
        self.check_response_is_person(response, 'a')

    def test_no_perms_for_other_synagogue(self):
        self.start_test()
        self.add_person()
        self.logout()
        self.check_unauthorized('/synagogue/1/person', method='get')
        self.check_unauthorized('/synagogue/1/person/1', method='get')

    def check_response_is_person(self, response, person_first_name):
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['first_name'], person_first_name)

    def test_get_specific_person(self):
        self.start_test()
        self.add_person(first_name='a')
        response = self.get_url('/synagogue/1/person/1', method='get')
        self.check_response_is_person(response, 'a')
