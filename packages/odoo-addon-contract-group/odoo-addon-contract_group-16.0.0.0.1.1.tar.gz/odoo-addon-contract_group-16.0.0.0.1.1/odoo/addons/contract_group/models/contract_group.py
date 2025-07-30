from odoo import models, fields, _


class ContractGroup(models.Model):
    _name = "contract.group"
    _description = "Contract group"
    _rec_name = "code"

    code = fields.Char(string="Code")
    partner_id = fields.Many2one("res.partner", string="Partner")

    contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="contract_group_id",
        string="Contracts",
    )
    account_move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="contract_group_id",
        string="Invoices",
    )
