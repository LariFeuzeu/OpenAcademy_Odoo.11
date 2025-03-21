from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    # Ajouter une nouvelle colonne pour identifier si un partenaire est un instructeur
    instructor = fields.Boolean('Instructor', default=False)
    session_ids = fields.Many2many('openacademy.session', string='attendees session', readonly=True)
