import re
import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import phonenumbers
import logging
from datetime import datetime, timedelta, date
from . import api_facturae

_logger = logging.getLogger(__name__)


class PartnerElectronic(models.Model):
    _inherit = "res.partner"

    # ==============================================================================================
    #                                          PARTNER
    # ==============================================================================================

    # === Partner fields === #

    commercial_name = fields.Char()
    identification_id = fields.Many2one(comodel_name="identification.type")
    payment_methods_id = fields.Many2one(
        comodel_name="payment.methods", string="Payment Method"
    )
    export = fields.Boolean(string="It's export", default=False)

    # === Economic Activity fields === #

    activity_id = fields.Many2one(
        comodel_name="economic.activity",
        string="Default Economic Activity",
        context={"active_test": False},
    )
    economic_activities_ids = fields.Many2many(
        comodel_name="economic.activity",
        string="Economic Activities",
        context={"active_test": False},
    )

    # === Exonerations fields === #

    has_exoneration = fields.Boolean(string="Has Exoneration?", required=False)
    type_exoneration = fields.Many2one(
        comodel_name="aut.ex", string="Authorization Type"
    )
    exoneration_number = fields.Char()
    percentage_exoneration = fields.Float(
        string="Percentage of VAT Exoneration")
    institution_name = fields.Char(
        string="Exoneration Issuer")
    date_issue = fields.Date(string="Issue Date")
    date_expiration = fields.Date(string="Expiration Date")
    date_notification = fields.Date(string="Last notification date")

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------

    @api.onchange("vat")
    def _onchange_name_value(self):
        if self.vat:
            self.name = " "

    @api.onchange("phone")
    def _onchange_phone(self):
        if self.phone:
            phone = phonenumbers.parse(
                self.phone, self.country_id and self.country_id.code or "CR"
            )
            valid = phonenumbers.is_valid_number(phone)
            if not valid:
                alert = {
                    "title": "Atención",
                    "message": _("Número de teléfono inválido"),
                }
                return {"value": {"phone": ""}, "warning": alert}

    @api.onchange("mobile")
    def _onchange_mobile(self):
        if self.mobile:
            mobile = phonenumbers.parse(
                self.mobile, self.country_id and self.country_id.code or "CR"
            )
            valid = phonenumbers.is_valid_number(mobile)
            if not valid:
                alert = {"title": "Atención", "message": "Número de teléfono inválido"}
                return {"value": {"mobile": ""}, "warning": alert}

    @api.onchange("email")
    def _onchange_email(self):
        if self.email:
            if not re.match(
                r"^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$",
                self.email.lower(),
            ):
                vals = {"email": False}
                alerta = {
                    "title": "Atención",
                    "message": "El correo electrónico no cumple con una estructura válida. "
                    + str(self.email),
                }
                return {"value": vals, "warning": alerta}

    @api.onchange("vat")
    def _onchange_vat(self):
        if self.identification_id and self.vat:
            if self.identification_id.code == "05":
                if len(self.vat) == 0 or len(self.vat) > 20:
                    raise UserError(
                        _("La identificación debe tener menos de 20 carateres.")
                    )
            else:
                # Remove leters, dashes, dots or any other special character.
                self.vat = re.sub(r"[^0-9]+", "", self.vat)
                if self.identification_id.code == "01":
                    if self.vat.isdigit() and len(self.vat) != 9:
                        raise UserError(
                            _(
                                "La identificación tipo Cédula física debe "
                                + "de contener 9 dígitos, sin cero al inicio y sin guiones."
                            )
                        )
                elif self.identification_id.code == "02":
                    if self.vat.isdigit() and len(self.vat) != 10:
                        raise UserError(
                            _(
                                "La identificación tipo Cédula jurídica debe contener 10 "
                                + "dígitos, sin cero al inicio y sin guiones."
                            )
                        )
                elif self.identification_id.code == "03" and self.vat.isdigit():
                    if self.vat.isdigit() and len(self.vat) < 11 or len(self.vat) > 12:
                        raise UserError(
                            _(
                                "La identificación tipo DIMEX debe contener 11 o 12 "
                                + "dígitos, sin ceros al inicio y sin guiones."
                            )
                        )
                elif self.identification_id.code == "04" and self.vat.isdigit():
                    if self.vat.isdigit() and len(self.vat) != 9:
                        raise UserError(
                            _(
                                "La identificación tipo NITE debe contener 10 dígitos, "
                                + "sin ceros al inicio y sin guiones."
                            )
                        )
#----------------------------------------------------------------------------------
#SE COMENTÓ ESTE CÓDIGO PARA QUE NO HICIERA LA CONSULTA DE LA EXONERACIÓN


    #@api.onchange("exoneration_number")
    #def _onchange_exoneration_number(self):
    #    if self.exoneration_number:
    #        self.definir_informacion_exo(self.exoneration_number)
#----------------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # TOOLING
    # -------------------------------------------------------------------------

    def action_get_economic_activities(self):
        if self.vat:
            json_response = api_facturae.get_economic_activities(self)
            _logger.debug("E-INV CR  - Economic Activities: %s", json_response)
            if json_response["status"] == 200:
                activities = json_response["activities"]
                # Activity Codes
                a_codes = list([])
                for activity in activities:
                    if activity["estado"] == "A":
                        a_codes.append(activity["codigo"])
                economic_activities = (
                    self.env["economic.activity"]
                    .with_context(active_test=False)
                    .search([("code", "in", a_codes)])
                )

                self.economic_activities_ids = economic_activities
                self.name = json_response["name"]
                self.identification_id = int(json_response["id_vat"])

                if len(a_codes) >= 1:
                    # print(self.name, self.id, self.vat)
                    if economic_activities:
                        self.activity_id = economic_activities[0]
            else:
                alert = {
                    "title": json_response["status"],
                    "message": json_response["text"],
                }
                return {"value": {"vat": ""}, "warning": alert}
        else:
            alert = {"title": "Atención", "message": _("Company VAT is invalid")}
            return {"value": {"vat": ""}, "warning": alert}

    def definir_informacion_exo(self, cedula):
        url_base = self.sudo().env.company.url_base_exo
        if url_base:
            url_base = url_base.strip()

            if url_base[-1:] == "/":
                url_base = url_base[:-1]

            end_point = url_base + "autorizacion=" + cedula

            headers = {
                "content-type": "application/json",
            }

            peticion = requests.get(end_point, headers=headers, timeout=10)

            ultimo_mensaje = (
                "Fecha/Hora: "
                + str(datetime.now())
                + ", Codigo: "
                + str(peticion.status_code)
                + ", Mensaje: "
                + str(peticion._content.decode())
            )

            if peticion.status_code in (200, 202) and len(peticion._content) > 0:
                contenido = json.loads(str(peticion._content, "utf-8"))

                self.sudo().env.company.ultima_respuesta_exo = ultimo_mensaje

                if "identificacion" in contenido:
                    if self.vat != contenido.get("identificacion"):
                        raise UserError(
                            _(
                                "El código de exoneración no concuerda con la cédula del socio de negocio."
                            )
                        )
                    fecha_emision = datetime.strptime(
                        str(contenido.get("fechaEmision"))[:10], "%Y-%m-%d"
                    )
                    self.date_issue = fecha_emision
                    fecha_vencimiento = datetime.strptime(
                        str(contenido.get("fechaVencimiento"))[:10], "%Y-%m-%d"
                    )
                    self.date_expiration = fecha_vencimiento
                    self.percentage_exoneration = float(
                        contenido.get("porcentajeExoneracion")
                    )
                    self.institution_name = contenido.get("nombreInstitucion")

                    tipo_documento = contenido.get("tipoDocumento")

                    autorizacion = (
                        self.env["aut.ex"]
                        .sudo()
                        .search(
                            [
                                ("code", "=", tipo_documento.get("codigo")),
                                ("active", "=", True),
                            ],
                            limit=1,
                        )
                    )

                    if len(autorizacion) > 0:
                        self.type_exoneration = autorizacion.id

    def check_exonerations(self):
        clients = self.env["res.partner"].search(
            [("has_exoneration", "=", True), ("date_expiration", "<", datetime.today())]
        )
        for client in clients:
            if (
                not client.date_notification
                or (client.date_notification + timedelta(days=8)) < date.today()
            ):
                email_template = client.env.ref(
                    "cr_electronic_invoice.email_template_client_exoneration_expired"
                )
                if email_template:
                    email_template.send_mail(client.id)
                    client.date_notification = date.today()

    @api.onchange("property_account_position_id")
    def _onchange_property_account_position_id(self):
        if self.property_account_position_id:
            # Obtener la posición fiscal seleccionada
            fiscal_position = self.env["account.fiscal.position"].browse(
                self.property_account_position_id.id
            )

            # Verificar si es zona Franca)
            if fiscal_position.name == "Zona Franca":
                self.has_exoneration = True
                self.type_exoneration = 3
                self.exoneration_number = "Ley 9635"
                self.percentage_exoneration = self.env.company.account_sale_tax_id.amount
                self.institution_name = "Ministerio de Hacienda"
                self.date_issue = "2018-12-04"

            # Verificar si es Venta exenta a diplomático)
            elif fiscal_position.name == "Venta exenta a diplomático":
                self.has_exoneration = True
                self.type_exoneration = 2
                self.exoneration_number = False
                self.percentage_exoneration = self.env.company.account_sale_tax_id.amount
                self.institution_name = "Ministerio de Relaciones Exteriores y Culto"
                self.date_issue = False
            # Verificar si es exportador de servicios)
            elif fiscal_position.name == "Cliente en el exterior":
                self.export = True
            # Verificar si es Venta exenta a diplomático)
            elif fiscal_position.name == "Otra exoneración":
                self.has_exoneration = True
                self.type_exoneration = False
                self.exoneration_number = False
                self.percentage_exoneration = self.env.company.account_sale_tax_id.amount
                self.institution_name = False
                self.date_issue = False
            else:
                self.has_exoneration = False
                self.type_exoneration = False
                self.exoneration_number = False
                self.percentage_exoneration = False
                self.institution_name = False
                self.date_issue = False
