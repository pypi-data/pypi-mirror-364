# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from ddt import ddt, file_data

from odoo.tests.common import tagged

from .base import BaseCase


@tagged("post_install", "-at_install")
@ddt
class TestCreate(BaseCase):
    @file_data("scenario_create_data.yml")
    def test_create(self, data):
        # Membuat data dengan isian yang valid
        rec = self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": data.get("name"),
                "code": data.get("code"),
                "value": data.get("value"),
                "note": data.get("note"),
            }
        )
        # Verifikasi semua data sudah disimpan dengan benar
        self.assertEqual(rec.name, data["name"])
        self.assertEqual(rec.code, data["code"])
        self.assertEqual(rec.value, data["value"])
        self.assertEqual(rec.note, data["note"])

    @file_data("scenario_create_invalid_data.yml")
    def test_create_validation_error(self, data):
        # Membuat data dengan isian yang tidak valid
        with self.assertRaises(ValueError):
            self.test_model.with_user(self.test_user_1.id).create(
                {
                    "name": data.get("name"),
                    "code": data.get("code"),
                    "value": data.get("value"),
                    "note": data.get("note"),
                }
            )
