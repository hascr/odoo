# -*- coding: utf-8 -*-

from odoo import models, fields, api


class has_event(models.Model):
    _inherit = 'event.event'
    

    presencial = fields.Boolean(string='Presencial', tracking=True, help='En oficina de Advance o instalaciones físicas del cliente')
    noenviar = fields.Boolean(string='No bienvenida', tracking=True)
    nocontrato = fields.Boolean(string='Sin contrato', tracking=True)
    materiallearn = fields.Char(string='Material Learn', tracking=True)
    urllearn = fields.Char(string='URL Learn', tracking=True)
    urlmatricula = fields.Char(string='URL matrícula', tracking=True)
    fechas_teams_pres = fields.Char(string='Fechas (Teams o presencial)', tracking=True)
    cantsesion = fields.Float (string='Cantidad de sesiones', tracking=True)
    hsesion = fields.Float (string='Horas por sesión', tracking=True)
    husd = fields.Float (string='Hora USD', tracking=True)
    enofi = fields.Boolean(string='En Oficina', tracking=True, help="Exclusivamente en oficina de Advance")
    titulo = fields.Boolean(string='Título entregado', tracking=True)
    cuenta_id = fields.Many2one(comodel_name='training.account', tracking=True, string='Cuenta Training')
    instructor_id = fields.Many2one(comodel_name='res.partner', tracking=True, string='Instructor', domain=[('instructor', '=', True)],)
    #instructor_id = fields.Many2one(comodel_name='instructor.name', tracking=True, string='Instructor')
    asesor = fields.Many2one(comodel_name='res.users', tracking=True, string='Realizar evaluación', domain=lambda self: [("groups_id", "=", self.env.ref( "sales_team.group_sale_salesman" ).id)])
    #facturado = fields.Boolean(string='Facturado', tracking=True)
    contrato_firmado = fields.Binary(attachment=True)
    account_move_id = fields.Many2one('account.move', string='Factura de Proveedor', domain=[('instructor', '=', True)])


    def go_to_contratos(self):
        name_form = ('Contratos')
        return {
        'name': name_form,
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'event.event',
        'res_id': self.id,  # Reference to the other model
        'target': 'new',
        'view_id': self.env.ref(
            'event.view_event_form').id,
        'context': {} # Optional
            }