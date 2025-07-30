from odoo import models, fields, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    contract_group_id = fields.Many2one("contract.group", string="Contract Group")