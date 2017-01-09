# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

ACADEMY_TYPE_LIST = [('public', 'Public'),
					('private', 'Private	'),
					('concerted', 'Concerted')]
DAYS_OF_WEEK = [('monday', 'Monday'),
				('tuesday','Tuesday'),
				('wednesday','Wednesday'),
				('Thursday', 'Thursday	'),
				('friday','Friday'),
				('saturday','Saturday')]
#defino constantes de estados 09_01/2017
COURSE_STATE=[
              ("cancel","cancel"),
              ("draft","draft"),
			  ("confirmed","Confirmed"),
			  ("in_process","in process"),
			  ("done","done")]
class res_partner2(osv.osv):
    """ Academia """   
    _inherit = 'res.partner'
    
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
        #09_01/2017  
        "state":fields.selection (COURSE_STATE,"state", required=False)
    }
    _defaults = {
				'state':'draft',
				}
	
    #los argumentos de la funcion los coje automaticamente de la interfaz de la accion
    def action_confirmed(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'confirmed'})
		return True
    def action_in_process(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'in_process'})
		return True
    def action_done(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'done'})
		return True
    def action_cancel(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'cancel'})
		return True
    def action_draft(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'draft'})
		return True
   
class subject(osv.osv):
    """ Asignaturas """
    _name = 'subject'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours'),
        'teachers_ids':fields.many2many('res.partner','subjetrespartner_rel_v2',string="Profesores Disponible") ,
        
               
    }
class time_table(osv.osv):
	"""nombre"""
	_name='time.table'
	_columns={
		'name':fields.char('Name', required= True),
		'description':fields.text('Description'),
		'date_start':fields.datetime('From', required= True),
		'date_end':fields.datetime('To', required= True),
		'detail_id':fields.one2many('time.table.detail','name'),
			
	} 
	
class time_table_detail(osv.osv):
	""" detalle del horario"""
	_name='time.table.detail'
	_columns={
		'name':fields.char('Name', required= True, size = 16),
		'days_of_week':fields.selection(DAYS_OF_WEEK,'Days of week', required= True),
		'hour_start':fields.datetime('From', required= True),
		'hour_end':fields.datetime('To', required= True),
		
		'table_id':fields.many2one('time.table','name'), 
		
	}
