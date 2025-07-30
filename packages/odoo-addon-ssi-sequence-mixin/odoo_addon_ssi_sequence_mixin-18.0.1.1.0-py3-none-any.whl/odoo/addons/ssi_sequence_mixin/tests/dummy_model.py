# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo import fields, models


# Dummy model turunan agar mixin bisa diuji
class DummyTestSequence(models.Model):
    _name = "ssi.test.sequence"
    _inherit = "mixin.sequence"
    _description = "Dummy Test Sequence"

    name = fields.Char(
        string="Description",
    )
    value = fields.Integer(
        string="Input Value",
    )
