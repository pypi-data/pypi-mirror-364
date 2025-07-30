# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TaxYear(models.Model):
    _name = "l10n_id.tax_year"
    _inherit = [
        "mixin.master_data",
        "mixin.date_duration",
    ]
    _description = "Tax Year"
    _order = "date_start asc, id"

    name = fields.Char(
        string="Tax Year",
        required=True,
    )
    period_ids = fields.One2many(
        string="Periods",
        comodel_name="l10n_id.tax_period",
        inverse_name="year_id",
    )

    def action_create_period(self):
        for year in self:
            year._create_period()

    def _create_period(self):
        self.ensure_one()
        obj_period = self.env["l10n_id.tax_period"]
        date_start = self.date_start
        while date_start < self.date_end:
            date_end = date_start + relativedelta(months=+1, days=-1)

            if date_end > self.date_end:
                date_end = self.date_end

            if date_end < date_start:
                strWarning = _(
                    "Date Start "
                    + date_start.strftime("%Y-%m-%d")
                    + " > Date End "
                    + date_end.strftime("%Y-%m-%d")
                )
                raise UserError(strWarning)

            obj_period.create(
                {
                    "name": date_start.strftime("%m/%Y"),
                    "code": date_start.strftime("%m/%Y"),
                    "date_start": date_start.strftime("%Y-%m-%d"),
                    "date_end": date_end.strftime("%Y-%m-%d"),
                    "year_id": self.id,
                }
            )
            date_start = date_start + relativedelta(months=+1)

    @api.model
    def _find_year(self, dt=None):
        if not dt:
            dt = datetime.now().strftime("%Y-%m-%d")
        criteria = [
            ("date_start", "<=", dt),
            ("date_end", ">=", dt),
        ]
        results = self.search(criteria)
        if not results:
            strWarning = _("No tax year configured for %s" % dt)
            raise models.ValidationError(strWarning)
        result = results[0]
        return result


class TaxPeriod(models.Model):
    _name = "l10n_id.tax_period"
    _inherit = [
        "mixin.master_data",
        "mixin.date_duration",
    ]
    _description = "Tax Period"
    _order = "date_start asc, id"

    name = fields.Char(
        string="Tax Period",
        required=True,
    )
    year_id = fields.Many2one(
        string="Tax Year",
        comodel_name="l10n_id.tax_year",
        ondelete="cascade",
    )

    def _next_period(self, step):
        self.ensure_one()
        criteria = [("date_start", ">", self.date_start)]
        results = self.search(criteria)
        if results:
            return results[step - 1]
        return False

    def _previous_period(self, step):
        self.ensure_one()
        criteria = [("date_start", "<", self.date_start)]
        results = self.search(criteria, order="date_start desc")
        if results:
            return results[step - 1]
        return False

    @api.model
    def _find_period(self, dt=None):
        if not dt:
            dt = datetime.now().strftime("%Y-%m-%d")
        criteria = [
            ("date_start", "<=", dt),
            ("date_end", ">=", dt),
        ]
        results = self.search(criteria)
        if not results:
            strWarning = _("No tax period configured for %s" % dt)
            raise models.ValidationError(strWarning)
        result = results[0]
        return result
