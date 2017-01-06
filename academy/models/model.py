from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

ACADEMY_TYPE_LIST=[("public","Public"),
		   ("private","Private"),
		   ("concerted","Concerted")
		  ]

class academy(osv.osv):
	_name='academy'
	_inherit='res.partner'
	_columns={
		'academy_type':fields.selection(ACADEMY_TYPE_LIST, string="academy_type", help="Select the academy type"),
		
		'sources_id':fields.one2many('academy.sources','name'),
		
		
		 }
	_defaults={
		'academy_type':[0][0],
		 }
class academy_sources(osv.osv):
	_name='academy.sources'
	_columns={
		'name':fields.char('Sources', required=True, size=64),
		'description':fields.text('Description', help='Description source'),
		'hours':fields.integer('horas'),
		'min_student':fields.integer('min student'),
		'max_student':fields.integer('max student'),	
		'price':fields.integer('Price'),
		'academy_id':fields.many2one('academy','Academy'),
		'teacher_id':fields.many2one('academy.teacher','Teacher'),
		
		
		}
class academy_teacher(osv.osv):
	
	_name='academy.teacher'
	_inherit='res.users'
	_columns={
		'teacher_id':fields.many2one('academy.sources','name'),
		'subject':fields.char('Subjects',size=64),
		}




academy()
	
