# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class asistencia(models.Model):
    _name = 'asistencia'
    _description = _('Asistencia de sesiones de entrenamiento')
    _rec_name = 'nombre'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string="Código", tracking=True)
    nombre = fields.Char(string="Nombre completo", tracking=True)
    correo = fields.Char(string="Correo electrónico", tracking=True)
    telefono = fields.Char(string="Teléfono", tracking=True, compute='_compute_telefono')
    celular = fields.Char(string="Celular", tracking=True, compute='_compute_celular')
    curso = fields.Char(string="Curso", tracking=True)
    #cuenta = fields.Char(string="Cuenta")
    fecha = fields.Datetime(string="Fecha", tracking=True)
    minutos = fields.Float(string="Minutos conectados", tracking=True)
    horas = fields.Float(string="Horas", compute='_compute_horas', store=True)
    tipo = fields.Char(string="Tipo", tracking=True)
    duplicados = fields.Char(string="revisar duplicados")
    cod_nombre = fields.Char(string='N. Curso', tracking=True)
    #asesor = fields.Integer(string="Asesor", compute='_compute_asesor')
    user_id = fields.Many2one('res.users', string='Asesor tecnológico', compute='_compute_asesor')
    
    _sql_constraints = [('duplicados_unique', 'unique(duplicados)', "El código duplicados debe ser único")]

    def go_to_event_asistencia(self):
        name_form = _('Cursos')
        return {
        'name': name_form,
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'event.event',
        'res_id': int(self.codigo),  # Reference to the other model
        'target': 'current',
        'view_id': self.env.ref(
            'event.view_event_form').id,
        'context': {} # Optional
            }
    
    @api.depends('minutos','horas')
    def _compute_horas(self):
        for record in self:
            record.horas = round(record.minutos / 60.0,2) #if record.minutos else 0 # Calculate hours from minutes

    """ def write(self, vals):
        res = super(asistencia, self).write(vals)
        return res """
    
    """ @api.depends('codigo', 'curso')
    def _computeVar(self):
        for line in self:
            line.cod_nombre = f"{line.codigo} - {line.curso}" """
    
    @api.depends('codigo', 'correo')
    def _compute_asesor(self):
            for record in self:
                codigo_int = int(record.codigo)  # Convert codigo to integer
                curso_record = self.env['event.registration'].search([('event_id', '=', codigo_int), ('email', '=', record.correo)])
            if curso_record:
                record.user_id = int(curso_record.asesor)
            else:
                record.user_id = 9  # Set asesor to None if no match

    """ @api.depends('user_id')
    def _compute_user_name(self):
        for record in self:
            if record.user_id:
                record.user_name = record.user_id.name
        else:
                record.user_name = '' """

    @api.depends('codigo', 'correo')
    def _compute_telefono(self):
            for record in self:
                codigo_int = int(record.codigo)  # Convert codigo to integer
                curso_record = self.env['event.registration'].search([('event_id', '=', codigo_int), ('email', '=', record.correo)])
            if curso_record:
                record.telefono = curso_record.phone
            else:
                record.telefono = ''  # Set asesor to None if no match

    @api.depends('codigo', 'correo')
    def _compute_celular(self):
            for record in self:
                codigo_int = int(record.codigo)  # Convert codigo to integer
                curso_record = self.env['event.registration'].search([('event_id', '=', codigo_int), ('email', '=', record.correo)])
            if curso_record:
                record.celular = curso_record.celular
            else:
                record.celular = ''  # Set asesor to None if no match
