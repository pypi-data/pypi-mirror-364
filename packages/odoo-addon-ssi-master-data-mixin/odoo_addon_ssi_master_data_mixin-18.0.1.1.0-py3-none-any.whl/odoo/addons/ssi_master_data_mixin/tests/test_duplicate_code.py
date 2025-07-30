# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from ddt import ddt, file_data

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .base import BaseCase


@tagged("post_install", "-at_install")
@ddt
class TestDuplicateCpde(BaseCase):
    @file_data("scenario_duplicate_code.yml")
    def test_create_duplicate_code(self, data1, data2):
        # Membuat data pertama
        self.test_model.with_user(self.test_user_1.id).create(
            {
                "name": data1.get("name"),
                "code": data1.get("code"),
                "value": data1.get("value"),
                "note": data1.get("note"),
            }
        )

        # Test Membuat data kedua dengan kode yang sudah ada
        with self.assertRaises(UserError):
            self.test_model.with_user(self.test_user_1.id).create(
                {
                    "name": data2.get("name"),
                    "code": data2.get("code"),
                    "value": data2.get("value"),
                    "note": data2.get("note"),
                }
            )
