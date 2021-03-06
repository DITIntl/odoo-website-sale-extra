# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz
import re

import logging
_logger = logging.getLogger(__name__)


class website_product_category(http.Controller):

    @http.route(['/category/<model("product.category"):category>', ], type='http', auth="public", website=True)
    def get_products(self, category=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        if category and not category.website_published:
            return request.render('website.page_404', {})
        elif category.website_description_template:
            return request.render(category.website_description_template.id, {'products': request.env['product.template'].sudo().search(['&', ('categ_id', '=', category.id), ('state', '=', 'sellable')], order='website_sequence'), 'category': category})
        else:
            return request.render('website_product_category.page_behandling', {'products': request.env['product.template'].sudo().search(['&', ('categ_id', '=', category.id), ('state', '=', 'sellable')], order='website_sequence'), 'category': category})
    
    @http.route(['/allcategory/<model("product.category"):category>', ], type='http', auth="public", website=True)
    def get_category(self, parent_id=1, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        categories = request.env['product.category'].sudo().search([('parent_id', '=', parent_id)], order='id')
        #categories.filtered("category.is_translated(lang)")
        return request.render('website_product_category.page_allcategories', {'categories': categories})


class product_category(models.Model):
    _inherit = "product.category"
    
    website_description = fields.Html('Description for the website', translate=True, sanitize=False)
    website_small_description = fields.Html('Short description', translate=True, sanitize=False)
    website_published = fields.Boolean('Available in the website', copy=False)
    website_image = fields.Binary('Category Image')
    website_description_template  = fields.Many2one(comodel_name="ir.ui.view",string="Optional Description Template", help="Optional with a custom template")

    def is_translated(self,lang):
        return len(self.env['ir.translation'].search(['&',('name','=','product.category,website_small_description'),('lang','=',lang)])) == 1
        #~ logging.warning('<<<<<<<<<<<<<< length: %s' % (len(self.env['ir.translation'].search(['&',('name','=','product.category,website_small_description'),('lang','=',lang)]))))

