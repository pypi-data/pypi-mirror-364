from odoo import models, fields, _


class ContractContract(models.Model):
    _inherit = "contract.contract"

    contract_group_id = fields.Many2one("contract.group", string="Contract Group")