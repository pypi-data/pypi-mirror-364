from django.test import TestCase
from django.urls import reverse

class CheckerViewTest(TestCase):
    def test_checker_letter(self):
        response = self.client.post(reverse('checker'), {'char': 'A'})
        self.assertContains(response, "C'est une lettre.")

    def test_checker_digit(self):
        response = self.client.post(reverse('checker'), {'char': '5'})
        self.assertContains(response, "C'est un chiffre.")

    def test_checker_special(self):
        response = self.client.post(reverse('checker'), {'char': '$'})
        self.assertContains(response, "C'est un caractère spécial.")
