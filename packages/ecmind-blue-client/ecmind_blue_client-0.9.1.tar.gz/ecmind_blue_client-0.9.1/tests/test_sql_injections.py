import unittest
import time
from uuid import uuid4
from ecmind_blue_client.client import parse_sqlstring
from ecmind_blue_client.tcp_pool_client import TcpPoolClient


class TestSqlInjections(unittest.TestCase):
    """
    Diese Tests simulieren einige bekannte Angriffe, bei denen SQL-Injections
    gemacht werden. Setup sollte sein, einerseits eine Test-Datenbanktabelle
    zu erzeugen
    CREATE TABLE injectiontest (zahl int, zeichen varchar(255))
    (die Injects würden im Erfolgsfall dort einen Eintrag schreiben)
    und andererseits ein Client-Objekt zu erzeugen, das mit einer Datenbank verbunden ist.
    In meinem Beispiel ging das mit dem folgenden auskommentierten Teil.

    import os
    path_to_enaio_config = os.path.join(os.getcwd(), "src", "suvi_konfiguration")
    path_to_app_config = os.path.join(os.getcwd(), "src", "konfiguration", "application.xml")
    from config_helper import lese_konfiguration
    CONFIG = lese_konfiguration(
        ordner_konfigurationen_suvi=path_to_enaio_config,
        pfad_app_konfiguration=path_to_app_config,
        service_name="dms-universal-api",
        zusatz_profile=["enaio"],
    )
    try:
        client = TcpPoolClient(**CONFIG["enaio"])
    except Exception as e:
        fail(f"Versuch, zum Enaio-Server zu verbinden, ist fehlgeschlagen. Fehler: {e}")

    Diese Zeile macht die Datei pro forma zu korrekter Syntax. Auskommentieren,
    sobald der Teil oben erledigt ist.
    """

    def setUp(self):
        self.client = TcpPoolClient("localhost:4000:1", __name__, "root", "optimal", True)
        # This is a somewhat-common SQL string I use in most tests
        self.user_and_pw_sqlstr = r"SELECT * FROM benutzer WHERE benutzer = %s AND passwort = 'wrongpw'"

    def test_attack_inject_line_comment(self):
        string = self.user_and_pw_sqlstr
        param = "kivbf_adm'--"
        expected = "SELECT * FROM benutzer WHERE benutzer = 'kivbf_adm''--' AND passwort = 'wrongpw'"

        self.assertEqual(parse_sqlstring(string, param), expected)

        result = self.client.execute_sql(string, param)
        assert result is not None and len(result) == 0

    def test_attack_inline_comment(self):

        string = self.user_and_pw_sqlstr
        param = "/* 1/0, */ 1"
        expected = r"SELECT * FROM benutzer WHERE benutzer = '/* 1/0, */ 1' AND passwort = 'wrongpw'"

        self.assertEqual(parse_sqlstring(string, param), expected)

        result = self.client.execute_sql(string, param)

        self.assertTrue(result is not None and len(result) == 0)

    def test_attack_stacked_queries(self):
        string = self.user_and_pw_sqlstr

        random_string = str(uuid4())
        param = f"1; UPDATE injectiontest set text = '{random_string}') WHERE id = 1;"
        expected = f"SELECT * FROM benutzer WHERE benutzer = '1; UPDATE injectiontest set text = ''{random_string}'') WHERE id = 1;' AND passwort = 'wrongpw'"

        self.assertEqual(parse_sqlstring(string, param), expected)

        # run the attack
        self.client.execute_sql(string, param)
        # assert that the values were not inserted
        res = self.client.execute_sql("SELECT text FROM injectiontest WHERE id = 1")
        self.assertTrue(res is not None and res[0] is not random_string)

    def test_attack_union_injection(self):
        # the MD5 hash for 1234 is 81dc9bdb52d04dc20036dbd8313ed055
        # Enaio doesn't use MD5 (OS never disclosed which hashing-algo
        # they actually use), but even if they did, this attack is handled
        # properly by escaping. The AND 1=0 UNION... part is never considered
        # code
        string = r"SELECT * FROM benutzer WHERE benutzer = %s AND passwort = %s"
        param1 = "admin' AND 1=0 UNION ALL SELECT 'kivbf_adm', '81dc9bdb52d04dc20036dbd8313ed055'"
        param2 = "1234"
        params = [param1, param2]

        self.assertEqual(
            parse_sqlstring(string, *params),
            (
                "SELECT * FROM benutzer WHERE benutzer = 'admin'' AND 1=0 UNION ALL SELECT ''kivbf_adm'', ''81dc9bdb52d04dc20036dbd8313ed055''' "
                "AND passwort = '1234'"
            ),
        )

    def test_attack_shutdown(self):

        string = self.user_and_pw_sqlstr
        param = "'; shutdown --"

        self.assertEqual(
            parse_sqlstring(string, param), (r"SELECT * FROM benutzer WHERE benutzer = '''; shutdown --' AND passwort = 'wrongpw'")
        )

        # run the attack
        self.client.execute_sql(string, param)
        # wait 2 seconds, then check if the DB is still running
        time.sleep(2)
        result = self.client.execute_sql("SELECT 1 as status")
        self.assertTrue(result is not None and result[0]["status"] == "1")
