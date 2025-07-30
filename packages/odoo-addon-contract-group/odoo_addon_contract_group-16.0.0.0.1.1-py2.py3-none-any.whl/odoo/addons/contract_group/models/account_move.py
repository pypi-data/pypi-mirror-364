from odoo import models, fields, _


class AccountInvoice(models.Model):
    _inherit = "account.move"

    contract_group_id = fields.Many2one("contract.group", string="Contract Group")
