# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FakturPajakKeluaran(models.Model):
    _name = "faktur_pajak_keluaran"
    _inherit = [
        "faktur_pajak_keluaran",
        "mixin.single_operating_unit",
    ]

    @api.depends(
        "operating_unit_id",
        "operating_unit_id.partner_id",
        "operating_unit_id.partner_id.nitku",
    )
    def _compute_efaktur_seller_id_tku(self):
        for record in self:
            result = "0000000000000000"
            if (
                record.operating_unit_id
                and record.operating_unit_id.partner_id
                and record.operating_unit_id.partner_id.nitku
            ):
                result = record.operating_unit_id.partner_id.nitku
            record.efaktur_seller_id_tku = result

    efaktur_seller_id_tku = fields.Char(
        compute="_compute_efaktur_seller_id_tku",
    )
