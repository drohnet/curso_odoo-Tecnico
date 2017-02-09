# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import logging
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

COURSE_STATE = [('draft','Draft'),
                ('confirmed','Confirmed'),
                ('in_process','In Process'),
                ('cancel','Cancel'),
                ('done','Done')]
                                
ATTENDANCE_STATE = [('draft','Draft'),
                    ('confirmed','Confirmed'),                    
                    ('cancel','Cancel'),
                    ('done','Done')]

ACADEMY_TYPE_LIST = [('public','Public'),
                     ('private','Private'),
                     ('concerted','Concerted')]
                     
DAYS_OF_WEEK = [('monday','Monday'),
                ('tuesday','Tuesday'),
                ('wednesday','Wednesday'),
                ('thursday','Thursday'),
                ('friday','Friday'),
                ('saturday','Saturday'),
                ('sunday','Sunday'),]

"""Herencia: Academias, Estudiantes, Profesores ->Tipo"""
class res_partner(osv.osv):    
    _inherit = 'res.partner'
    
    def _check_name(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        current_obj = self.browse(cr, uid, ids, context=context)
        if current_obj.is_academy:
            #previous_name_ids = self.search(cr, uid, [('id','!=',current_obj.id),('name','=',current_obj.name),('is_academy','=',True)], context=context)
            previous_name_ids = self.search(cr, uid, [('id','!=',current_obj.id),('name','=ilike',current_obj.name),('is_academy','=',True)], context=context)
            
            if previous_name_ids:
                return False
                
        return True
   
    _columns = {
        'academy_type': fields.selection(ACADEMY_TYPE_LIST, 'Academy type', help= "Select the academy type for the record" ),
        'course_ids': fields.one2many('course', 'academy_id', string='Courses'),
        'is_academy': fields.boolean('Is Academy'),
        'is_student': fields.boolean('Is Student'),
        'is_teacher': fields.boolean('Is Teacher'),
        
    }
    
    _constraints = [(_check_name,_("The academy name must be unique"),['name']),
    ]
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if context is None:
            context={}
            
        res = {}
        _logger.info('------------ONCHANGE NAME------------')
        _logger.info(name)
        
        if name:
            res['value'] = {'name':name.title()}
            
        return res
    
"""Cursos"""                     
class course(osv.osv):    
    """ Course  """
    _name = 'course'
    
    _columns = {
                'academy_id': fields.many2one('res.partner', string='Academy', required=True, domain=[('is_academy','=',True)], ondelete='restrict'),
                'time_table_id': fields.many2one('time.table', string='Time table', required=True, ondelete='restrict'),
                'time_table_id_detail_ids': fields.related('time_table_id', 'time_detail_ids', type='one2many', relation='time.table.detail', string='Time table detail'),
                'name': fields.char('Name', required=True, size=64),
                'description': fields.text('Description'),
                'hours': fields.integer('Duration', required=True, help='Duration in hours'),
                'min_students': fields.integer('Min students', required=True, help='Minimum quantity of students'),
                'max_students': fields.integer('Max students', required=True, help='Maximum quantity of students'),
                'price': fields.float('Price', required=True, digits=(6,2), help='Price per student'),
                'subject_ids': fields.one2many('course.subject', 'course_id', string='Subjects'),
                'student_ids': fields.many2many('res.partner','course_student_table',string='Students', domain=[('is_student','=',True)]),
                'teacher_ids': fields.many2many('res.partner','course_teacher_table',string='Teachers', domain=[('is_teacher','=',True)]),
                'date_start': fields.date('Start date', required=True, help=''),                
                'date_end': fields.date('End date', required=True, help=''),
                'state': fields.selection(COURSE_STATE, 'state', required=False),
    }
    
    _defaults = {
                'state': COURSE_STATE[0][0],
    }
   
    
	
    
	
    def action_draft(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        if context.get('name',False):
            
        
			self.write(cr, uid, ids, { 'state' : 'draft' })
        
        return True
    
    def signal_confirmed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.signal_workflow(cr, uid, ids, 'button_confirmed')
        return True
    
    def action_confirmed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write(cr, uid, ids, { 'state' : 'confirmed' })
        
        return True
        
    def condition_draft_confirmed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        course_obj = self.browse(cr, uid, ids, context=context)
        if course_obj:
            if course_obj.subject_ids:
                return True
                
        return False
        
    def action_in_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write(cr, uid, ids, { 'state' : 'in_process' })
        
        return True
        
    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write(cr, uid, ids, { 'state' : 'done' })
        
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write(cr, uid, ids, { 'state' : 'cancel' })
        
        return True

    def onchange_time_table_id(self, cr, uid, ids, time_table_id, context=None):
        if context is None:
            context = {}
            
        res = {}
        time_table_obj = self.pool.get('time.table').browse(cr, uid, [time_table_id], context=context)
        
        _logger.info('***************TIME TABLE ID******************')
        
        if time_table_obj:
            res['value']= {'time_table_id_detail_ids':time_table_obj.time_detail_ids}
        _logger.info('***************TIME TABLE DETAILS******************')
                          
        return res
"""Materias"""    
class subject(osv.osv):    
    """ Subject  """
    _name = 'subject'
    
    
    
    def _check_name(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        current_obj = self.browse(cr, uid, ids, context=context)
        previous_name_ids = self.search(cr, uid, [('id','!=',current_obj.id),('name','=ilike',current_obj.name)], context=context)
            
        if previous_name_ids:
            return False
            
        return True
    
    _columns = {
                'name': fields.char('Name', required=True, size=64),
                'description': fields.text('Description'),
                'hours': fields.integer('Duration', required=True, help='Duration in hours'),                
    }
    
    _constraints = [(_check_name,_("The subject name must be unique"),['name']),
    ]
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if context is None:
            context={}
            
        res = {}
        if name:
            res['value'] = {'name':name.title()}
            
        return res
    
"""Relación curso-materia-horario"""
class course_subject(osv.osv):
    _name = 'course.subject'
   
    _columns = {
    'name': fields.char('Name', required=True, size=64),
    'course_id': fields.many2one('course', string='Course', required=True, ondelete='restrict'),
    'course_id_time_table_id': fields.related('course_id','time_table_id_detail_ids',type='many2one' ,relation='time.table', string='Course time table'),
    #test
    'time_table_id_detail_ids': fields.related('course_id','time_table_id', 'time_detail_ids', type='one2many', relation='time.table.detail', string='Time table detail'),

    #'course_id_time_table_details': fields.related('course_id','time_table_id_detail_ids',type='one2many' ,relation='time.table.detail', string='Course time table details'),
    'subject_id': fields.many2one('subject', string='Subject', required=True, ondelete='restrict'),
    'test_id':fields.many2one('subject', string='test_id',  ondelete='restrict'),
    #'time_table_id': fields.many2one('time.table', string='Time table', required=True, ondelete='restrict'),
    'child_ids': fields.one2many('course.subject.time.table.detail', 'course_subject_id', string='Time table', ondelete='cascade'),
    #(course.subject)-course_id(m2o)<->(m2o)time_time_table_id(course)<->(o2m)time_detail_ids(time_detail_ids)
    'test':fields.related('course_id','time_table_id','time_detail_ids',type="one2many",relation='time.table.detail' ,string='test1'),
    'testt': fields.related('course_id','time_table_id', 'time_detail_ids', type='one2many', relation='time.table.detail', string='Testt2'),
    'testtt':fields.related('course','time_table_id_detail_ids','day_of_week' ,string="testtt3")

    }
    
   
    
  
    
	
	
		
	
		
  
    
    def onchange_course_id(self, cr, uid, ids, course_id, context=None):
        if context is None:
            context = {}
            
        res = {}
        course_obj = self.pool.get('course').browse(cr, uid, [course_id], context=context)
        
        if course_obj:
            if course_obj.time_table_id_detail_ids:
                res['value']= {
                               'course_id_time_table_details':course_obj.time_table_id_detail_ids,
                               'course_id': course_id,
                }
            
        return res
        
    
    def onchange_subject_id(self, cr, uid, ids, subject_id, course_id, context=None):
        if context is None:
            context = {}
            
        res = {}
        course_obj = self.pool.get('course').browse(cr, uid, [course_id], context=context)
        
        subject_obj = self.pool.get('subject').browse(cr, uid, [subject_id], context=context)
        if course_obj and subject_obj:
            if course_obj.name and subject_obj.name:
                res['value']= {'name': course_obj.name + ' - ' + subject_obj.name,
                               
                }
            
        return res
    def onchange_time_table_id(self, cr, uid, ids, time_table_id, context=None):
        if context is None:
            context = {}
            
        res = {}
        time_table_obj = self.pool.get('time.table').browse(cr, uid, [time_table_id], context=context)
        time_table_det_obj = self.pool.get('time.table.detail').browse(cr,uid,ids,context=context)
        _logger.info('***************TIME TABLE ID******************')
        _logger.info(time_table_id)
        if time_table_obj:
            res['value']= {'time_table_id_detail_ids':time_table_obj.time_detail_ids}
        _logger.info('***************TIME TABLE DETAILS******************')
        #_logger.info(time_table_obj.time_detail_ids)
        #_logger.info(res)
            
        return res

"""curso-materia-horario-detalle"""    
class course_subject_time_table_detail(osv.osv):    
    """ Course subject time table detail  """
    _name = 'course.subject.time.table.detail'
    
    _columns = {
                'name': fields.char('Name', required=True, size=16),
                'course_subject_id': fields.many2one('course.subject', 'Course-Subject relation', required=True),
                'day_of_week': fields.selection(DAYS_OF_WEEK, 'Days of week', required=True),
                'hour_start': fields.float('From',digits=(4,2), required=True, help='Hour from'),                
                'hour_end': fields.float('To', digits=(4,2), required=True, help='Hour to'),  
                'sequence': fields.integer('Sequence'),              
    }
    
"""Horario"""
class time_table(osv.osv):    
    """ Time table  """
    _name = 'time.table'
        
    
    def _check_name(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        current_obj = self.browse(cr, uid, ids, context=context)
        previous_name_ids = self.search(cr, uid, [('id','!=',current_obj.id),('name','=ilike',current_obj.name)], context=context)
            
        if previous_name_ids:
            return False
            
        return True
    
    _columns = {
                'name': fields.char('Name', required=True, size=64),
                'description': fields.text('Description'),
                #'type': fields.selection(TIME_TABLE_TYPE, 'Type', required=True, help= "Select the type for the record" ),
                'time_detail_ids': fields.one2many('time.table.detail', 'time_table_id', string='Detail'),                
    }
    
    _constraints = [(_check_name,_("The subject name must be unique"),['name']),
    ]
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if context is None:
            context={}
            
        res = {}
        if name:
            res['value'] = {'name':name.title()}
            
        return res
    
"""Horario detalle"""    
class time_table_detail(osv.osv):    
    """ Time table detail  """
    _name = 'time.table.detail'
    #_order = 'time_table_id,sequence'
    
    def _check_current_time_range(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        current_obj = self.browse(cr, uid, ids, context=context)
        
        if current_obj.hour_end <= current_obj.hour_start:
            return False
            
        if current_obj.hour_start < 0.0 or current_obj.hour_start > 24.0:
            return False
            
        if current_obj.hour_end < 0.0 or current_obj.hour_end > 24.0:
            return False
            
        return True
        
    
    def _check_previous_time_range(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        current_obj = self.browse(cr, uid, ids, context=context)
        previous_name_ids = self.search(cr, uid, 
                        ['|','|',
                        '&',('hour_start','<=',current_obj.hour_start),('hour_end','>',current_obj.hour_start),
                        '&',('hour_start','<',current_obj.hour_end),('hour_end','>=',current_obj.hour_end),
                        '&',('hour_start','>',current_obj.hour_start),('hour_end','<',current_obj.hour_end),
                        ('id','!=',current_obj.id),
                        ('time_table_id','=',current_obj.time_table_id.id),
                        ('day_of_week','=',current_obj.day_of_week)], 
                        context=context)
            
        if previous_name_ids:
            return False
            
        return True
    
    _columns = {
                'name': fields.char('Name', required=True, size=16),
                'time_table_id': fields.many2one('time.table', 'Time table', required=True),
                'day_of_week': fields.selection(DAYS_OF_WEEK, 'Days of week', required=True),
                'hour_start': fields.float('From',digits=(4,2), required=True, help='Hour from'),                
                'hour_end': fields.float('To', digits=(4,2), required=True, help='Hour to'),  
                'sequence': fields.integer('Sequence'),              
    }
    
    _defaults = {
                'sequence':1,
    }
    
    _constraints = [(_check_current_time_range,_("The  time detail current"),['day_of_week','hour_start','hour_end']),
                    (_check_previous_time_range,_("The  time detail previous"),['day_of_week','hour_start','hour_end']),
    ]

"""Asistencia"""    
class student_attendance(osv.osv):
    """ Student Attendance Header  """
    _name = 'student.attendance'
    
    _columns = {'name': fields.char('Name', required=True, size=128),
                'course_subject_id': fields.many2one('course.subject', string="Course - Subject", required=True),
                'date_start': fields.date('Start date', required=True, help=''),                
                'date_end': fields.date('End date', required=True, help=''),
                'state': fields.selection(ATTENDANCE_STATE, 'state', required=True),
                
    }
        
    _defaults = {
                'state': ATTENDANCE_STATE[0][0],
    }

"""Asistencia detalle"""    
class student_attendance_detail(osv.osv):
    """ Student Attendance Detail  """
    _name = 'student.attendance.detail'
    
    _columns = {'name': fields.char('Name', required=True, size=64),
                'attendance_id': fields.many2one('student.attendance', string="Attendance", required=True),
                'student_id': fields.many2one('res.partner', string="Student", required=True, domain=[('is_student','=',True)]),
                'attendance_date': fields.date(string='Date', required=True),
                'sign': fields.boolean(string='Sign', required=False),
    }















