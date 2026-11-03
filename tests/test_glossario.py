import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from ditado.glossario import Glossario


class GlossarioTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo = Path(self.pasta.name) / "glossario.json"
        self.glossario = Glossario(self.arquivo)

    def tearDown(self):
        self.pasta.cleanup()

    def test_salva_e_carrega_do_arquivo(self):
        self.glossario.adicionar("Learning360", favorito=True)
        self.glossario.adicionar("bravend", "Bravend")
        self.glossario.salvar()

        carregado = Glossario(self.arquivo)
        self.assertEqual([e.termo for e in carregado.entradas], ["Learning360", "bravend"])
        self.assertTrue(carregado.buscar("learning360").favorito)
        self.assertEqual(carregado.buscar("BRAVEND").substituto, "Bravend")

    def test_adicionar_termo_existente_atualiza_sem_duplicar(self):
        self.glossario.adicionar("ClickUp")
        self.glossario.adicionar("clickup", "ClickUp")
        self.assertEqual(len(self.glossario.entradas), 1)
        self.assertEqual(self.glossario.entradas[0].substituto, "ClickUp")

    def test_termo_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            self.glossario.adicionar("   ")

    def test_remover(self):
        self.glossario.adicionar("Teams")
        self.assertTrue(self.glossario.remover("teams"))
        self.assertFalse(self.glossario.remover("teams"))

    def test_vocabulario_ordena_por_favorito_recencia_e_usos(self):
        agora = datetime(2026, 11, 3, 12, 0)
        for termo in ["Zeta", "Alfa", "Recente", "Favorito", "Antigo"]:
            self.glossario.adicionar(termo)
        self.glossario.adicionar("Substituido", "Outro")
        self.glossario.buscar("Favorito").favorito = True
        self.glossario.buscar("Recente").ultimo_uso = (agora - timedelta(hours=2)).isoformat()
        self.glossario.buscar("Antigo").ultimo_uso = (agora - timedelta(days=30)).isoformat()
        self.glossario.buscar("Antigo").usos = 9

        self.assertEqual(
            self.glossario.vocabulario(agora=agora),
            ["Favorito", "Recente", "Antigo", "Alfa", "Zeta"],
        )
        self.assertEqual(self.glossario.vocabulario(limite=2, agora=agora), ["Favorito", "Recente"])


if __name__ == "__main__":
    unittest.main()
