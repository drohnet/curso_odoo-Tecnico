# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

ACADEMY_TYPE_LIST = [('public', 'Public'),
					('private', 'Private	'),
					('concerted', 'Concerted')]


class res_partner2(osv.osv):
    """ Academia """   
    _inherit = 'res.partner'
    #### Herencia clásica (extiende objeto res_partner)    class academy(osv.osv):
    _columns = {
        'is_academy': fields.boolean('Is Academy'),   
        'academy_type': fields.selection(ACADEMY_TYPE_LIST, 'Academy Type'),  
        'courses_ids':fields.one2many('course', 'academy_id',string="Courses"),
        'is_student': fields.boolean('Is Student', help="True if is student"),  
        'is_teacher': fields.boolean('Is Teacher', help="True if is teacher"),
        'asignature':fields.many2one('course','name'),
        'subject_ids':fields.many2many('subject','teachersubject_rel_v2',string="Subject", ),           
    }   
 
class course(osv.osv):
    """ Curso """
    _name = 'course'
    
    _columns = {
        'academy_id':fields.many2one('res.partner',domain =[('is_academy','=',True)], string="Academy"),
        'name':fields.char('Name', size=64,required=True),
        'course_id':fields.one2many('res.partner','name'),
        'description':fields.text('Description'),
        'hours':fields.integer('Hours'),
        'max_students':fields.integer('Students Maximum'),
        'min_students':fields.integer('Students Minimum'),
        'price':fields.float('Price',(4,2)),
        'subject_ids':fields.many2many('subject','coursesubject_rel_v2',string="Subject" ),     
    }

   
class subject(osv.osv):
    """ Asignaturas """
    _name = 'subject'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours'),
        'teachers_ids':fields.many2many('res.partner','subjetrespartner_rel_v2',string="Profesores Disponible") ,
        
               
    }

	
