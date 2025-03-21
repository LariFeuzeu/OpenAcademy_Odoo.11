# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api, exceptions


class Course(models.Model):
    _name = 'openacademy.course'  # Name Model

    name = fields.Char(string="Name", required=True)  # Le champ 'nom' est requis (True est un booléen, pas une chaîne)
    description = fields.Text(string="Description")  # Champ 'description'
    responsible_id = fields.Many2one('res.users', string="Responsible", index="true")
    # Relation inverse : le course peut avoir une session (One2many inverse)
    session_ids = fields.One2many('openacademy.session', 'course_id', required=True)


@api.multi
def copy(self, default=None):
    # Si 'default' est None, initialise comme un dictionnaire vide
    default = dict(default or {})

    # Cherche le nombre de copies déjà existantes dont le nom commence par 'Copy of' et correspond au nom actuel
    copied_count = self.search_count(
        [('name', '=like', u"Copy of {}%".format(self.name))])

    # Si aucune copie n'existe, le nom de la nouvelle copie sera 'Copy of <nom>'
    if not copied_count:
        new_name = u"Copy of {}".format(self.name)
    else:
        # Si des copies existent, le nom inclura un compteur (ex: 'Copy of <nom> (1)')
        new_name = u"Copy of {} ({})".format(self.name, copied_count)

    # Ajoute ou modifie le nom de la copie dans les 'default' pour l'enregistrement
    default['name'] = new_name

    # Appelle la méthode 'copy' du modèle parent pour créer la copie
    return super(Course, self).copy(default)


# Définition d'une contrainte SQL pour vérifier que le nom n'est pas identique à la description
_sql_constraints = [
    ('name_description_check',  # Identifiant de la contrainte
     'CHECK(name != description)',  # Condition de la contrainte: le nom doit être différent de la description
     'The name of the course cannot be the same as its description.')
    # Message d'erreur si la contrainte est violée
]


class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date(string="Start Date")
    duration = fields.Float(digits=(6, 2), help="Duree en jours")
    seating = fields.Integer(help="Number de places")

    instructor_id = fields.Many2one('res.partner', string='instructor',
                                    domain=['|', ('instructor', '=', True),
                                            # OU logique : sélectionne les instructeurs (instructor=True)
                                            ('category_id.name', 'ilike',
                                             "Teacher")])  # OU sélectionne les partenaires dont la catégorie contient "Teacher"

    # Relation Many2one vers Course. Chaque session appartient à un seul cours
    course_id = fields.Many2one('openacademy.course', string='Course', required=True)

    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    active = fields.Boolean(default=True)
    color = fields.Integer()
    # Déclaration d'un champ calculé 'taken_seats' qui sera calculé par la méthode '_taken_seats'
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    # Définition du champ 'end_date' calculé, stocké et lié aux méthodes '_get_end_date' et '_set_end_date'
    end_date = fields.Date(string="End Date", store=True,
                           compute='_get_end_date', inverse='_set_end_date')

    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')

    # Déclare une méthode dépendante du champ 'duration'
    @api.depends(
        'duration')  # Le décorateur @api.depends indique que cette méthode sera recalculée lorsque 'duration' change
    def _get_hours(self):
        # Cette méthode calcule 'hours' basé sur 'duration'
        for r in self:  # On parcourt tous les records (en cas de traitement par lot)
            r.hours = r.duration * 24  # On multiplie la durée par 24 pour obtenir les heures, car 'duration' est en jours

    # Méthode qui inverse le calcul en affectant la valeur de 'hours' à 'duration'
    def _set_hours(self):
        # Cette méthode convertit 'hours' en 'duration'
        for r in self:  # On parcourt tous les records
            r.duration = r.hours / 24  # On divise 'hours' par 24 pour obtenir la durée en jours

    @api.depends('attendee_ids')  # Déclenche la méthode quand 'attendee_ids' change
    def _get_attendees_count(self):
        for r in self:  # Pour chaque enregistrement de la session
            r.attendees_count = len(
                r.attendee_ids)  # On compte le nombre d'invités et on le stocke dans 'attendees_count'

    # Calcul de la date de fin en fonction de la date de début et de la durée
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):  # Si start_date ou duration manquent, end_date = start_date
                r.end_date = r.start_date
                continue

            start = fields.Datetime.from_string(r.start_date)  # Convertir start_date en datetime
            duration = timedelta(days=r.duration, seconds=-1)  # Ajouter la durée (ajustée d'une seconde)
            r.end_date = start + duration  # Calculer la date de fin en ajoutant la durée

    # Mise à jour de la durée lorsque la date de fin est modifiée
    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):  # Si start_date ou end_date manquent, on ne fait rien
                continue

            start_date = fields.Datetime.from_string(r.start_date)  # Convertir start_date en datetime
            end_date = fields.Datetime.from_string(r.end_date)  # Convertir end_date en datetime
            r.duration = (
                                 end_date - start_date).days + 1  # Calculer la durée (en jours) et ajuster +1 pour inclure le jour de départ

    attendees_count = fields.Integer(string="Attendees count", compute='_get_attendees_count', store=True)

    # La méthode '_taken_seats' est appelée chaque fois que les champs 'seats' ou 'attendee_ids' changent
    @api.depends('seating',
                 'attendee_ids')  # L'annotation @api.depends permet de lier cette méthode aux champs 'seats' et 'attendee_ids'
    def _taken_seats(self):
        # 'for r in self' parcourt chaque enregistrement de la session sur lequel cette méthode est appelée
        for r in self:
            # Si 'seats' est égal à 0 (aucune place disponible), 'taken_seats' sera égal à 0
            if not r.seating:
                r.taken_seats = 0.0  # Utilisation de '=' pour affecter la valeur 0.0 à 'taken_seats'
            else:
                # Si 'seats' n'est pas égal à 0, on calcule le pourcentage de places prises
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seating  # Calcul du pourcentage de places prises

    @api.onchange('seating', 'attendee_ids') #changemen uniquement visible sur interface odoo
    def _verify_valid_seats(self):
        if self.seating < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seating < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }

    # Le décorateur @api.constrains indique que cette méthode doit être appelée
    # chaque fois que les champs 'instructor_id' ou 'attendee_ids' sont modifiés
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        # Pour chaque enregistrement de session dans l'objet (self peut contenir plusieurs enregistrements)
        for r in self:
            # Vérifie si l'instructeur est défini et s'il est également dans la liste des participants
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                # Si l'instructeur est dans la liste des participants, une erreur de validation est levée
                raise exceptions.ValidationError("A session's instructor can't be an attendee")
