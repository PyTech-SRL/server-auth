from odoo import models


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _get_rules(self, model_name, mode='read'):
        res = super()._get_rules(model_name, mode)
        # if self.env.context.get("is_impersonated"):
        # if model_name == "grifoflex.order":
        #     import wdb; wdb.set_trace()
        return res
