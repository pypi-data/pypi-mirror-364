# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from ddt import ddt, file_data

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .base import BaseCase


@tagged("post_install", "-at_install")
@ddt
class TestGenerateCode(BaseCase):
    @file_data("scenario_create_data.yml")
    def test_generate_code_no_sequence(self, data):
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": data.get("name"),
                "code": data.get("code"),
                "value": data.get("value"),
                "note": data.get("note"),
            }
        )

        with self.assertRaises(UserError):
            rec.action_generate_code()

    @file_data("scenario_generate_code.yml")
    def test_generate_code(self, data, sequence, template):
        sequence_prefix = self.env["ir.sequence"].create(
            {
                "name": sequence["name"],
                "code": sequence["code"],
                "prefix": sequence["prefix"],
                "number_next": sequence["number_next"],
                "number_increment": sequence["number_increment"],
                "padding": sequence["padding"],
            }
        )
        self.env["sequence.template"].create(
            {
                "name": template["name"],
                "model_id": self.tester_model.id,
                "sequence_field_id": self.field_obj.id,
                "date_field_id": self.field_date_obj.id,
                "initial_string": template["initial_string"],
                "computation_method": template["computation_method"],
                "python_code": template["python_code"],
                "sequence_selection_method": template["sequence_selection_method"],
                "sequence_id": sequence_prefix.id,
            }
        )
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": data.get("name"),
                "value": data.get("value"),
                "note": data.get("note"),
            }
        )
        rec.action_generate_code()
        self.assertEqual(rec.code, "TEST-000001")
