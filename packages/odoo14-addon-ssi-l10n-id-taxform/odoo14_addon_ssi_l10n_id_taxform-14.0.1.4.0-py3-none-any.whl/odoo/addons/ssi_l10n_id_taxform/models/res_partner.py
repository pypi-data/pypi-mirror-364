# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    nitku = fields.Char(
        string="NITKU",
        help="Nomor Induk Tempat Kegiatan Usaha (NITKU)",
    )
