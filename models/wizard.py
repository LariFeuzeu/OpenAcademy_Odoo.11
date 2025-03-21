# Importation des modules nécessaires d'Odoo
from odoo import models, fields, api


# Définition d'un modèle transitoire (temporaire) dans Odoo
class Wizard(models.TransientModel):
    _name = 'openacademy.wizard'  # Nom technique du modèle, ici c'est un modèle temporaire pour OpenAcademy

    def _default_session(self):
        # Récupère l'ID de la session depuis le contexte actif
        active_id = self._context.get('active_id')

        # Retourne l'enregistrement de la session correspondant à l'ID
        return self.env['openacademy.session'].browse(active_id)

    # Définition d'un champ Many2one, représentant une relation vers le modèle 'openacademy.session'
    session_id = fields.Many2one('openacademy.session',  # Champ de type Many2one vers le modèle 'openacademy.session'
                                 string="Session", required=True,
                                 default=_default_session,  # Label affiché dans l'interface
                                 )  # Ce champ est obligatoire (l'utilisateur doit choisir une session)

    # Définition d'un champ Many2many, représentant une relation vers le modèle 'res.partner'
    attendee_ids = fields.Many2many('res.partner',
                                    # Champ de type Many2many vers le modèle 'res.partner' (les partenaires)
                                    string="Attendees")  # Label affiché dans l'interface pour ce champ, ici c'est pour les participants


@api.multi
def subscribe(self):
    for session in self.session_ids:
        self.session_id.attendee_ids |= self.attendee_ids
    # Ajoute les participants (attendees) au champ 'attendee_ids' de la session
    # '|=' est un opérateur de mise à jour pour les champs Many2many, il ajoute des enregistrements sans les dupliquer.

    # Retourne un dictionnaire vide, généralement utilisé pour fermer un wizard ou une vue.
    return {}
