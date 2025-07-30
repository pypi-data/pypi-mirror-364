# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo import fields, models


class DummyModel(models.Model):
    _name = "dummy_model"
    _inherit = "mixin.master_data"
    _description = "Dummy Model"

    value = fields.Integer(
        string="Input Value",
    )
