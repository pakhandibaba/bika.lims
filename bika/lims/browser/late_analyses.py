from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.publish import Publish
from bika.lims.utils import isActive, TimeOrDate
from zope.component import getMultiAdapter
import plone

class LateAnalysesView(BikaListingView):
    """ Late analysees (click from portlet_late_analyses More... link)
    """
    def __init__(self, context, request):
        super(LateAnalysesView, self).__init__(context, request)
        self.contentsMethod = getToolByName(self.context, 'portal_catalog')
        self.contentFilter = {'portal_type':'Analysis',
                              'getDueDate': {'query': [DateTime(),], 'range': 'max'},
                              'review_state':['assigned',
                                              'sample_received',
                                              'sample_due',
                                              'to_be_verified',
                                              'verified'],
                              'cancellation_state': 'active',
                              'sort_on':'id',
                              'sort_order': 'reverse'}
        self.show_editable_border = False
        self.title = _("Late Analyses")
        self.description = ""
        self.content_add_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 100
        self.view_url = self.view_url + "/late_analyses"
        self.columns = {'Analysis': {'title': _('Analysis')},
                        'RequestID': {'title': _('Request ID')},
                        'Client': {'title': _('Client')},
                        'Contact': {'title': _('Contact')},
                        'DateReceived': {'title': _('Date Received')},
                        'DueDate': {'title': _('Due Date')},
                        'Late': {'title': _('Late')},
                        }

        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns':['Analysis',
                        'RequestID',
                        'Client',
                        'Contact',
                        'DateReceived',
                        'DueDate',
                        'Late'],
             },
        ]

    def folderitems(self):
        items = super(LateAnalysesView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            ar = obj.aq_parent
            sample = ar.getSample()
            client = ar.aq_parent
            contact = ar.getContact()
            items[x]['Analysis'] = obj.Title()
            items[x]['RequestID'] = ''
            items[x]['replace']['RequestID'] = "<a href='%s'>%s</a>" % \
                 (ar.absolute_url(), ar.Title())
            items[x]['Client'] = ''
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                 (client.absolute_url(), client.Title())
            items[x]['Contact'] = ''
            items[x]['replace']['Contact'] = "<a href='mailto:%s'>%s</a>" % \
                 (contact.getEmailAddress(), contact.getFullname())
            items[x]['DateReceived'] = TimeOrDate(self.context, sample.getDateReceived())
            items[x]['DueDate'] = TimeOrDate(self.context, obj.getDueDate())

            late = DateTime() - obj.getDueDate()
            days = int(late / 1)
            hours = int((late % 1 ) * 24)
            mins = int((((late % 1) * 24) % 1) * 60)
            late_str = days and "%s day%s" % (days, days > 1 and 's' or '') or ""
            late_str += hours and " %s hour%s" % (hours, hours > 1 and 's' or '') or ""
            if not days and not hours:
                late_str = "%s min%s" % (mins, mins > 1 and 's' or '')

            items[x]['Late'] = late_str
        return items
