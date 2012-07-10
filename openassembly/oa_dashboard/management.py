##responsible for getting/creating anonymous dashboard
from oa_dashboard.models import DashboardPanel
from django.contrib.auth.models import User

AnonymousUser, is_new = User.objects.get_or_create(username='congress_critter')

db = DashboardPanel.objects.filter(user=AnonymousUser)
for i in db:
	i.delete()

DashboardPanel.objects.get_or_create(user=AnonymousUser, plank='/p/proposals/d-h',
								boardname='Proposals', priority=2, zoom_x=0, zoom_y=1, dashboard_id=1)

DashboardPanel.objects.get_or_create(user=AnonymousUser, plank='/p/topics/d-h',
								boardname='Groups', priority=4, zoom_x=0, zoom_y=0, dashboard_id=1)

DashboardPanel.objects.get_or_create(user=AnonymousUser, plank='/p/users/d-n',
								boardname='Members', priority=3, zoom_x=0, zoom_y=0, dashboard_id=1)

DashboardPanel.objects.get_or_create(user=AnonymousUser, plank='/p/tutorial',
								boardname='OpenAssembly Tutorial', priority=1, zoom_x=1, zoom_y=1, dashboard_id=1)


