# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from ddt import ddt, file_data

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .base import BaseCase


@tagged("post_install", "-at_install")
@ddt
class TestMixinSequence(BaseCase):
    @file_data("scenario_custom_suffix.yml")
    def test_error_sequence_custom_suffix(self, sequence, template, test_model):
        # Test sequence dengan custom suffix
        sequence_suffix = self.env["ir.sequence"].create(
            {
                "name": sequence["name"],
                "code": sequence["code"],
                "number_next": sequence["number_next"],
                "number_increment": sequence["number_increment"],
                "padding": sequence["padding"],
            }
        )
        template_suffix = self.env["sequence.template"].create(
            {
                "name": template["name"],
                "model_id": self.tester_model.id,
                "sequence_field_id": self.field_obj.id,
                "date_field_id": self.field_date_obj.id,
                "initial_string": template["initial_string"],
                "computation_method": template["computation_method"],
                "python_code": template["python_code"],
                "sequence_selection_method": template["sequence_selection_method"],
                "sequence_id": sequence_suffix.id,
                "add_custom_suffix": template["add_custom_suffix"],
                "suffix_python_code": "-",
                "sequence": template["sequence"],
            }
        )
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": test_model["name"],
                "value": test_model["value"],
            }
        )
        template = rec._get_template_sequence()
        self.assertEqual(template, template_suffix)
        # Raise Error
        with self.assertRaises(UserError):
            rec._create_sequence()

    @file_data("scenario_custom_suffix.yml")
    def test_sequence_custom_suffix(self, sequence, template, test_model):
        # Test sequence dengan custom suffix
        sequence_suffix = self.env["ir.sequence"].create(
            {
                "name": sequence["name"],
                "code": sequence["code"],
                "number_next": sequence["number_next"],
                "number_increment": sequence["number_increment"],
                "padding": sequence["padding"],
            }
        )
        template_suffix = self.env["sequence.template"].create(
            {
                "name": template["name"],
                "model_id": self.tester_model.id,
                "sequence_field_id": self.field_obj.id,
                "date_field_id": self.field_date_obj.id,
                "initial_string": template["initial_string"],
                "computation_method": template["computation_method"],
                "python_code": template["python_code"],
                "sequence_selection_method": template["sequence_selection_method"],
                "sequence_id": sequence_suffix.id,
                "add_custom_suffix": template["add_custom_suffix"],
                "suffix_python_code": template["suffix_python_code"],
                "sequence": template["sequence"],
            }
        )
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": test_model["name"],
                "value": test_model["value"],
            }
        )
        template = rec._get_template_sequence()
        self.assertEqual(template, template_suffix)
        rec._create_sequence()
        # Pastikan name dimulai dengan suffix
        self.assertEqual(rec.name, "000001/TEST-SUFFIX")
