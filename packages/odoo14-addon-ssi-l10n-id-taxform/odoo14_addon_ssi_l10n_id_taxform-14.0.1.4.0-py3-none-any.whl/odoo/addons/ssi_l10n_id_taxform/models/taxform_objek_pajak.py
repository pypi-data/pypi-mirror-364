# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class TaxformObjekPajak(models.Model):
    _name = "l10n_id.taxform_objek_pajak"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Taxform Objek Pajak"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    code = fields.Char(
        string="Kode Objek Pajak",
        required=True,
        translate=True,
    )
    name = fields.Text(
        string="Description",
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        ondelete="restrict",
        readonly=True,
    )
