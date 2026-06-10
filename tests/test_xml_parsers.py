import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.xml.parsers.registry import parse_xml_document, supported_document_types, load_root
from src.xml.parsers.detector import detect_document_type, DOC_NFSE

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestXmlParsers(unittest.TestCase):

    def test_supported_types(self):
        types = supported_document_types()
        ids = {t['id'] for t in types}
        self.assertIn('NFE', ids)
        self.assertIn('NFSE', ids)
        self.assertIn('CTE', ids)
        self.assertIn('MDFE', ids)

    def test_parse_nfe(self):
        doc = parse_xml_document(os.path.join(os.path.dirname(__file__), '..', 'nota_teste.xml'),
                                company_cnpj='98765432000199')
        self.assertIsNotNone(doc)
        self.assertIn(doc.doc_tipo, ('NFE', 'NFCE'))
        self.assertEqual(doc.numero, '12345')
        self.assertEqual(len(doc.itens), 2)
        self.assertEqual(doc.tipo, 'entrada')

    def test_parse_nfse_abrasf(self):
        path = os.path.join(FIXTURES, 'nfse_abrasf.xml')
        doc = parse_xml_document(path, company_cnpj='98765432000199')
        self.assertEqual(doc.doc_tipo, 'NFSE')
        self.assertEqual(doc.numero, '201500000000279')
        self.assertEqual(len(doc.itens), 1)
        self.assertEqual(doc.itens[0]['codigo_servico'], '17.01')
        self.assertEqual(doc.tipo, 'entrada')

    def test_parse_cte(self):
        path = os.path.join(FIXTURES, 'cte.xml')
        doc = parse_xml_document(path, company_cnpj='98765432000199')
        self.assertEqual(doc.doc_tipo, 'CTE')
        self.assertEqual(doc.numero, '202600000041185')
        self.assertEqual(len(doc.itens), 1)
        self.assertIn('transporte', doc.itens[0]['descricao'].lower())
        self.assertEqual(doc.tipo, 'entrada')

    def test_parse_mdfe(self):
        path = os.path.join(FIXTURES, 'mdfe.xml')
        doc = parse_xml_document(path, company_cnpj='12345678000100')
        self.assertEqual(doc.doc_tipo, 'MDFE')
        self.assertEqual(doc.numero, '1001')
        self.assertEqual(len(doc.itens), 1)
        self.assertEqual(doc.tipo, 'saida')

    def test_detector_nfse(self):
        root = load_root(os.path.join(FIXTURES, 'nfse_abrasf.xml'))
        self.assertEqual(detect_document_type(root), DOC_NFSE)


if __name__ == '__main__':
    unittest.main()
