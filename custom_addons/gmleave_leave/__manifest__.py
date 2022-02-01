{
    'name': 'GMLeave Leave',
    'version': '0.1',
    'author': 'Greenmount',
    'website': 'http://www.greenmount.co.th/gmleave',
    'category': 'Custom',
    'depends': ['base', 'gmleave_master'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/leave_view.xml',
        'wizard/leave_approve_wizard.xml',
        'wizard/leave_cancel_wizard.xml',
    ],
    'demo': [],
}
