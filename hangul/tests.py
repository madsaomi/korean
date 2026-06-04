import pytest


@pytest.mark.django_db
class TestHangulViews:
    def test_hangul_page(self, client):
        resp = client.get('/hangul/')
        assert resp.status_code == 200

    def test_sentence_breakdown(self, client):
        resp = client.get('/hangul/breakdown/')
        assert resp.status_code == 200

    def test_sentence_builder(self, client):
        resp = client.get('/hangul/builder/')
        assert resp.status_code == 200

    def test_tts_endpoint(self, client):
        resp = client.get('/hangul/tts/', {'text': '안녕하세요'})
        assert resp.status_code in (200, 429)
