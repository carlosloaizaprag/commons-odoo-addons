# -*- encoding: utf-8 -*-


from odoo import models, fields, api, _

# Define an extencible city model.


class ResCity(models.Model):
    _name = 'res.country.state.city'
    _description = 'Ciudad'    
    name = fields.Char(
        string='City',
        required=True)
    state_id = fields.Many2one(
        'res.country.state',
        string='State')
    phone_prefix = fields.Char(
        string='Phone Prefix')
    statcode = fields.Char(
        string='DANE Code',
        size=5,
        help='Code of the Colombian statistical department')
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        related='state_id.country_id',
        store=True,
        readonly=True)


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    space = fields.Char('Espacio', readonly=True, default=' ,')
    country_id = fields.Many2one(
        'res.country',
        related='city_id.state_id.country_id',
        readonly=True)
    city = fields.Char(invisible=True, string="City")

    city_id = fields.Many2one(
        'res.country.state.city',
        'City Id'
    )
    state_id = fields.Many2one(
        'res.country.state',
        related='city_id.state_id',
        readonly=True,
        string="State Id"
    )

    @api.onchange('city_id')
    def _change_city(self):
        self.city = self.city_id.name
