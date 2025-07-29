import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

import requests
import json

logger = logging.getLogger(__name__)


class SendContractWizard(models.TransientModel):
    _name = "send.contract.wizard"
    _description = "Send contract to SomEnergia via curl"

    sale_order_id = fields.Many2one("sale.order", compute="_compute_sale_order_id")
    cups = fields.Char(related="sale_order_id.cups")
    is_light = fields.Boolean(related="sale_order_id.is_light")
    service_street = fields.Char(related="sale_order_id.service_street")
    service_state_id = fields.Many2one(related="sale_order_id.service_state_id")
    service_city = fields.Char(related="sale_order_id.service_city")
    service_zip_code = fields.Char(related="sale_order_id.service_zip_code")
    is_home = fields.Boolean(related="sale_order_id.is_home")
    cnae = fields.Char(related="sale_order_id.cnae")
    cadastral_reference = fields.Char(related="sale_order_id.cadastral_reference")
    statement = fields.Boolean(related="sale_order_id.statement")
    voltage_installation_type = fields.Selection(related="sale_order_id.voltage_installation_type")
    power_type = fields.Char(related="sale_order_id.power_type")
    current_power_point = fields.Char(related="sale_order_id.current_power_point")
    current_power_valley = fields.Char(related="sale_order_id.current_power_valley")
    current_power_p1 = fields.Char(related="sale_order_id.current_power_p1")
    current_power_p2 = fields.Char(related="sale_order_id.current_power_p2")
    current_power_p3 = fields.Char(related="sale_order_id.current_power_p3")
    current_power_p4 = fields.Char(related="sale_order_id.current_power_p4")
    current_power_p5 = fields.Char(related="sale_order_id.current_power_p5")
    current_power_p6 = fields.Char(related="sale_order_id.current_power_p6")
    selfconsume = fields.Char(related="sale_order_id.selfconsume")
    installation = fields.Boolean(compute="_compute_installation")
    cau = fields.Char(related="sale_order_id.cau")
    installation_power = fields.Char(related="sale_order_id.installation_power")
    installation_situation = fields.Selection(related="sale_order_id.installation_situation")
    installation_type = fields.Selection(related="sale_order_id.installation_type")
    auxiliar_service = fields.Boolean(related="sale_order_id.auxiliar_service")
    titular_nif = fields.Char(related="sale_order_id.titular_nif")
    is_previous_titular = fields.Boolean(related="sale_order_id.is_previous_titular")
    titular_firstname = fields.Char(related="sale_order_id.titular_firstname")
    titular_lastname = fields.Char(related="sale_order_id.titular_lastname")
    titular_street = fields.Char(related="sale_order_id.titular_street")
    titular_state_id = fields.Many2one(related="sale_order_id.titular_state_id")
    titular_city = fields.Char(related="sale_order_id.titular_city")
    titular_zip_code = fields.Char(related="sale_order_id.titular_zip_code")
    titular_email = fields.Char(related="sale_order_id.titular_email")
    titular_phone = fields.Char(related="sale_order_id.titular_phone")
    conditions = fields.Boolean(related="sale_order_id.conditions")
    payment_conditions = fields.Boolean(related="sale_order_id.payment_conditions")
    privacy_policy = fields.Boolean(related="sale_order_id.privacy_policy")
    tariff = fields.Char(compute="_compute_tariff")
    iban = fields.Char(related="sale_order_id.iban")
    donation = fields.Boolean(related="sale_order_id.donation")
    iban_statement = fields.Boolean(related="sale_order_id.iban_statement")

    def _compute_sale_order_id(self):
        sale_order = self.env["sale.order"].browse(
            self.env.context["active_ids"]
        )
        self.sale_order_id = sale_order.id

    def _compute_tariff(self):
        self.tariff = self.sale_order_id.tariff.default_code

    def _compute_installation(self):
        if self.sale_order_id.installation == "collective_installation":
            self.installation = True
        else:
            self.installation = False

    def send_contract(self):
        values = {
            "member_number": "19753",
            "member_vat": "F47736335",
            "cups": self.cups,
            "is_indexed": self.is_light,
            "tariff": self.tariff,
            "power_p1": self.current_power_point or self.current_power_p1,
            "power_p2": self.current_power_valley or self.current_power_p2,
            # "power_p3": self.current_power_p3,
            # "power_p4": self.current_power_p4,
            # "power_p5": self.current_power_p5,
            # "power_p6": self.current_power_p6,
            "cups_address": self.service_street,
            "cups_postal_code": self.service_zip_code,
            "cups_city_id": 5020,
            "cups_state_id": 9,
            "cnae": self.cnae,
            "supply_point_accepted": True,
            "owner_is_member": self.is_previous_titular,
            "contract_owner": {
                "is_juridic": False,
                "vat": self.titular_nif,
                "name": self.titular_firstname,
                "surname": self.titular_lastname,
                "address": self.titular_street,
                "city_id": 5020,
                "state_id": 9,
                "postal_code": self.titular_zip_code,
                "email": self.titular_email,
                "phone": self.titular_phone,
                "lang": "es_ES",
                "privacy_conditions": self.privacy_policy
            },
            "self_consumption": {
                "aux_services": self.auxiliar_service,
                "cau": self.cau,
                "collective_installation": self.installation,
                "installation_power": self.installation_power,
                "installation_type": "01",
                "technology": "b11"
            },
            "owner_is_payer": True,
            "payment_iban": self.iban,
            "sepa_conditions": self.iban_statement,
            "donation": self.donation,
            "process": "A3",
            "general_contract_terms_accepted": self.conditions,
            "particular_contract_terms_accepted": self.payment_conditions
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            'https://api.somenergia.coop/procedures/contract',
            headers=headers,
            data=json.dumps(values),
            timeout=20
        )

        logger.info(
            "Contract sending: {} {}".format(response.status_code, response.text)
        )

        if response.status_code == 200:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": "Éxito",
                    "message": "Contrato enviado correctamente.",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "warning",
                    "title": "Error",
                    "message": f"Error {response.status_code}: {response.text}",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
