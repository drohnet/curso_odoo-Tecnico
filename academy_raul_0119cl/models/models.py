# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)
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
COURSE_STATE=[("cancel","cancel"),
			  ("draft","draft"),
			  ("confirmed","confirmed"),
			  ("in_process","in process"),
			  
			  ("done","done")]
			  
ATTENDANCE_STATE=[("draft","draft"),

		    ("confirmed","confirmed"),
		    ("cancel","cancel"),
		    ("done","done")]

TIME_TABLE_TYPE=[("course","course"),

	    ("subject","subject"),
	   ]

#herencia : academia estudiantes profesores	   
class res_partner2(osv.osv):
    """ Academia """   
    _inherit = 'res.partner'
    #funcion que detecta si el nombre de la academia es unico o ya esta en la bd
    def _check_academy_name(self, cr, uid, ids, context=None):
        #si el contex viene vacio lo convertimos a un diccionario para que no de error
        if context is None :
	    context = {}
        #contruimos y guardamos en el objeto current_obj la busqueda que de las academias en el campo name
        current_obj = self.browse(cr, uid,ids,context=context)
        #si el obejto que quiero guardar es is_academy
        _logger.info(current_obj)
        _logger.info(current_obj.is_academy)
        if current_obj.is_academy == True:
            _logger.info('-------------------------------is_academy-------------------------------')
            _logger.info(current_obj.is_academy)
            #hacemos una consulta con search y que compare los argumentos dados al objeto current_obj que no tenga el mismo id que tengan el mismo nombre y que sean academias
            previous_name_ids= self.search(cr,uid,[('id','!=',current_obj.id),('name','=',current_obj.name),('is_academy','=',True)],context=context)            
            pr= self.browse(cr,uid,ids,context=context)
            #printea el valor de los ids en caso de coincidencia, y en caso de no coincidir estara vacia por lo que no entrar en el ultimo if y no podra devolver False lo que significa que no hay coincidencia.
            _logger.info(previous_name_ids)
            _logger.info(pr.id)
            #si previus_name_ids es no coincide entra en false
            if previous_name_ids:
                return False
        return True
    
    _columns = {
        'is_academy': fields.boolean('Is Academy'),   
        'academy_type': fields.selection(ACADEMY_TYPE_LIST, 'Academy Type'),  
        'courses_ids':fields.one2many('course', 'academy_id',string="Courses"),
        'is_student': fields.boolean('Is Student', help="True if is student"),  
        'is_teacher': fields.boolean('Is Teacher', help="True if is teacher"),
        'surname':fields.char('Surname', help= "Second name", required=True, size= 64),

    }   
    #cualquier modelo puede tener multiples constrains  odoo espera verdadero para guardar el registro
    _constraints= [(_check_academy_name,_("The Academy name must be unique"),['name']),
                (_check_teacher_name_surname,_("The teacher name and surname must be unique"),['name','surname']),
                (_check_student_name_surname,_("The student name and surname must be unique"),['name'])]
    
#cursos
class course(osv.osv):
    
    """ Curso """
    #self esla instancia del objeto esn este caso course
    #cr cursor del currren row 
    #ids es el id que esta vivo en tiempo de ejecucion
    #context variables que en el tiempo de ejecucion se comunican entre metodos y objetos
    #los argumentos de la funcion los coje automaticamente de la interfaz de la accion
    def action_confirmed(self,cr,uid,ids,context=None):
	if context is None:
	    context={}
	self.write(cr,uid,ids,{'state':'confirmed'})
        return True
    def condition_draft_confirmed(self, cr, uid,ids,context=None):
	if context is None:
	    context={}
	#cuando no se conoce el id se usa el search cuando sabemos el id usamos el browse devuelve el objeto
	#metodo para buscar .search
	#self.pool.get('subjetc').search(cr,uid,['|',('name','!=',False),('cant','>','0'),('state','=','confirmed')],context=context) pool es el conunto de onjetos registrados
	#
	#browse va a la base de datos y hace una busqueda con los criterios dados
	course_obj = self.browse(cr,uid,ids,context=context)
	#si courseobj esta vacio
	if course_obj:
	    #si course_obj.subjetc_ids esta vacio
	    if course_obj.subject_ids:
		return True
	return False
    def signal_confirmed(self, cr, uid,ids,context=None):
	if context is None:
	    context={}
	self.signal_workflow(cr,uid,ids,'button_confirmed')
	return True
    def action_in_process(self,cr,uid,ids,context=None):
	if context is None:
	    context={}
	self.write(cr,uid,ids,{'state':'in_process'})
	return True
    def action_done(self,cr,uid,ids,context=None):
	if context is None:
	    context={}
	self.write(cr,uid,ids,{'state':'done'})
	return True
    def action_cancel(self,cr,uid,ids,context=None):
	if context is None:
	    context={}
	self.write(cr,uid,ids,{'state':'cancel'})
	return True
    def action_draft(self,cr,uid,ids,context=None):
	if context is None:
	    context={}
	self.write(cr,uid,ids,{'state':'draft'})
	return True
    _name = 'course'
    
    _columns = {
        'academy_id':fields.many2one('res.partner',domain =[('is_academy','=',True)], string="Academy"),
	'time_table_id':fields.many2one('time.table', string="Time Table", ondelete='restrict'),
        'name':fields.char('Name', size=64,required=True),
        'course_id':fields.one2many('res.partner','name'),
        'description':fields.text('Description'),
        'hours':fields.integer('Hours',required=True),
        'max_students':fields.integer('Students Maximum',required=True),
        'min_students':fields.integer('Students Minimum',required=True),
        'price':fields.float('Price',(4,2),required=True),
        'subject_ids':fields.one2many('course.subject','course_id',string="Subject" ),  
	'student_ids':fields.many2many('res.partner','course_student_table',domain =[('is_student','=',True)],string="Students"),
	'teacher_ids':fields.many2many('res.partner','course_teacher_table',domain =[('is_teacher','=',True)],string="Teachers"),
	#09_01/2017  
        "state":fields.selection (COURSE_STATE,"state", required=False),
	'date_start':fields.datetime('From', required= True),
	'date_end':fields.datetime('To', required= True),
	'detail_tt_id':fields.many2one('time.table.detail','name'),
	
    }
    _defaults = {
				'state':'draft',
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
#creamos una clase nueva que actua como un modelo relacional entre curso y materias 19/01/2017 con campos hijos de course ,subjetc y time table
class course_subject(osv.osv):
    _name= 'course.subject'
    _columns={
	'name':fields.char('Name', size=64,required=True),
	'course_id':fields.many2one('course',string='Course',required=True,ondelete='restrict'),
	'subject_id':fields.many2one('subject',string='subject',required=True,ondelete='restrict'),
	'time_table_id':fields.many2one('time.table',string='time table',required=True,ondelete='restrict'),
	}
    
class time_table(osv.osv):
	"""TIME TABLE"""
	_name='time.table'
	_columns={
		'name':fields.char('Name', required= True,SIZE=64),
		'description':fields.text('Description'),
		'type':fields.selection(TIME_TABLE_TYPE,'type',required=True),
		'time_table_detail_ids':fields.one2many('time.table.detail','name',string='Time table detail'),
			
	} 
	
class time_table_detail(osv.osv):
    
    

	""" detalle del horario"""
	_name='time.table.detail'
	_columns={
		'name':fields.char('Name', required= True, size = 16),
		'time_table_id':fields.many2one('time.table','time table',reqiured=True),
		'days_of_week':fields.selection(DAYS_OF_WEEK,'Days of week', required= True),
		'hour_start':fields.datetime('From', required= True),
		'hour_end':fields.datetime('To', required= True),
		
		'table_id':fields.many2one('time.table','name'), 
		'tt_detail_id':fields.one2many('course','name'),
		
	}
class student_attendance(osv.osv):
    _name="student.attendance"
    _columns={
	'name':fields.char('name',required=True,size=128),
	'course_subject_id':fields.many2one('course.subject',string="Course-subject",required=True),
	'date_start':fields.datetime('Start date', required= True),
	'date_end':fields.datetime('End date', required= True),
	'state':fields.selection(ATTENDANCE_STATE,'state',required=True),
	
    }
    _defaults = {
	'state':ATTENDANCE_STATE[0][0],
    }
class student_attendance_detail(osv.osv):
    _name="student.attaendance.detail"
    _columns={
	'name':fields.char('name',required=True,size=128),
	'attendance_id':fields.many2one('student.attendance',string="attendance",required=True),
	'student_id':fields.many2one('res.partner',string="student",required=True, domain=("is_student","=",True)),
	'attendace_date':fields.date(string="Date",required=True),
	'sign':fields.boolean(string="Sign",required=True),
	}
    _defaults = {
	'sign':False,
    }
