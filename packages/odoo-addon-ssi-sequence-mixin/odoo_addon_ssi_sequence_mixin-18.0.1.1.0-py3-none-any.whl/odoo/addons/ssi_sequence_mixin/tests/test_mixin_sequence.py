# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from ddt import data, ddt, unpack

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .base import BaseCase


@tagged("post_install", "-at_install")
@ddt
class TestMixinSequence(BaseCase):
    @data(["/", 12])
    @unpack
    def test_sequence_python_true(self, name, value):
        # value > 10, python_code -> result = True
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": name,
                "value": value,
            }
        )
        template = rec._get_template_sequence()
        self.assertEqual(template, self.template_python)
        # # Test create sequence
        rec._create_sequence()
        self.assertNotEqual(rec.name, "/")

    @data(["/", 5])
    @unpack
    def test_sequence_domain_true(self, name, value):
        # value < 10, python_code -> result = False,
        # harus failover ke template domain atau error
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": name,
                "value": value,
            }
        )
        template = rec._get_template_sequence()
        self.assertEqual(template, self.template_domain)
        rec._create_sequence()
        self.assertNotEqual(rec.name, "/")

    @data(["/", 10])
    @unpack
    def test_sequence_domain_false(self, name, value):
        # value <= 5, tidak ada template applicable, harus raise error
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": name,
                "value": value,
            }
        )
        with self.assertRaises(UserError):
            rec._create_sequence()

    @data(["/", 20])
    @unpack
    def test_edge_case_initial_string_true(self, name, value):
        # Pastikan initial_string digunakan saat record baru
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": name,
                "value": value,
            }
        )
        # Sebelum membuat sequence, name harus sesuai dengan initial_string
        self.assertEqual(rec.name, "/")
        rec._create_sequence()
        # Setelah membuat sequence, name harus berubah
        self.assertNotEqual(rec.name, "/")

    @data(["00001", 20])
    @unpack
    def test_edge_case_initial_string_false(self, name, value):
        # Sequence tidak terbuat apabila name tidak sesuai dengan inital_string
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": name,
                "value": value,
            }
        )
        # Sebelum membuat sequence, name = 000001
        self.assertEqual(rec.name, "00001")
        rec._create_sequence()
        # Setelah membuat sequence, name harus tetap 00001
        self.assertEqual(rec.name, "00001")

    @data(["/", 50])
    @unpack
    def test_template_order(self, name, value):
        # Jika ada lebih dari satu applicable template,
        # urutan sequence di template harus digunakan
        # Tambah template dengan order lebih tinggi
        model_obj = self.template_python.model_id
        field_obj = self.template_python.sequence_field_id
        field_date_obj = self.template_python.date_field_id
        template_high_order = self.env["sequence.template"].create(
            {
                "name": "High Order",
                "model_id": model_obj.id,
                "sequence_field_id": field_obj.id,
                "date_field_id": field_date_obj.id,
                "initial_string": "/",
                "computation_method": "use_domain",
                "domain": "[('value', '>', 0)]",
                "sequence": 100,  # urutan tinggi
            }
        )
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": name,
                "value": value,
            }
        )
        template = rec._get_template_sequence()
        self.assertEqual(template, template_high_order)
