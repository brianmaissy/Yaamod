from django.test import TestCase
from rest_framework import status
from django.test.client import Client


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

    def check_perms(self, url, method, data=None, expected_status=status.HTTP_200_OK):
        """
        check that a view can be accessed while logged in, and unaccessible while not.
        """
        unauthorized_statuses = [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        self.get_url(url, method, data, unauthorized_statuses)
        self.login()
        response = self.get_url(url, method, data, expected_status)
        self.logout()
        self.get_url(url, method, data, unauthorized_statuses)
        return response

    def add_synagogue(self):
        self.get_url('/synagogue', 'post', {'name': 'abc'}, status.HTTP_201_CREATED)


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
