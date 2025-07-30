# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _name = "res.config.settings"
    _inherit = [
        "res.config.settings",
    ]

    module_ssi_l10n_id_taxform_bukti_potong_pph_f113301 = fields.Boolean(
        string="Bukti Potong PPh 21/26 Tidak Final (f.1.1.33.01)",
    )

    module_ssi_l10n_id_taxform_bukti_potong_pph_f113302 = fields.Boolean(
        string="Bukti Potong PPh 21 Final (f.1.1.33.02)",
    )

    module_ssi_l10n_id_taxform_bukti_potong_pph_f113304 = fields.Boolean(
        string="Bukti Potong PPh 22 (f.1.1.33.04)",
    )

    module_ssi_l10n_id_taxform_bukti_potong_pph_f113306 = fields.Boolean(
        string="Bukti Potong PPh 23 (f.1.33.06)",
    )
    module_ssi_l10n_id_taxform_bukti_potong_pph_f113308 = fields.Boolean(
        string="Bukti Potong PPh 26 (f.1.1.33.08)",
    )
