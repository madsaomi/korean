
from django.test import SimpleTestCase

from config.env_loader import load_dotenv


class LoadDotEnvTests(SimpleTestCase):
    def _write(self, tmp_path, content):
        path = tmp_path / '.env'
        path.write_text(content, encoding='utf-8')
        return str(path)

    def test_missing_file_returns_zero(self):
        self.assertEqual(load_dotenv('Z:/definitely/not/here/.env'), 0)

    def test_parses_basic_pairs(self, tmp_path):
        env = {}
        path = self._write(tmp_path, 'A=1\nB=hello world\n')
        self.assertEqual(load_dotenv(path, environ=env), 2)
        self.assertEqual(env['A'], '1')
        self.assertEqual(env['B'], 'hello world')

    def test_skips_comments_and_blanks(self, tmp_path):
        env = {}
        path = self._write(tmp_path, '# comment\n\nKEY=val\n   \n')
        self.assertEqual(load_dotenv(path, environ=env), 1)
        self.assertEqual(env['KEY'], 'val')

    def test_strips_quotes_and_export_prefix(self, tmp_path):
        env = {}
        content = 'export Q="quoted"\nS=\'single\'\nP=plain\n'
        load_dotenv(self._write(tmp_path, content), environ=env)
        self.assertEqual(env['Q'], 'quoted')
        self.assertEqual(env['S'], 'single')
        self.assertEqual(env['P'], 'plain')

    def test_existing_env_wins(self, tmp_path):
        env = {'EXISTING': 'from-env'}
        path = self._write(tmp_path, 'EXISTING=from-file\nOTHER=x\n')
        count = load_dotenv(path, environ=env)
        self.assertEqual(count, 1)
        self.assertEqual(env['EXISTING'], 'from-env')
        self.assertEqual(env['OTHER'], 'x')
