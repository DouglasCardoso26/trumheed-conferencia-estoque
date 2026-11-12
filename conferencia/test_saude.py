from django.test import TestCase
from django.urls import reverse


class SaudeTests(TestCase):
    def test_responde_ok_sem_login(self):
        resposta = self.client.get(reverse("saude"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"status": "ok"})
