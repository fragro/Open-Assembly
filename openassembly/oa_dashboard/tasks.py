from oa_dashboard.models import DashboardPanel
from celery.task import task


@task(ignore_result=True)
def async_sort_board(sort_vals):
        itr = 1
        print sort_vals
        for pk in sort_vals:
                try:
                        ds = DashboardPanel.objects.get(pk=pk)
                        ds.priority = itr
                        ds.save()
                        itr += 1
                except:
                        print str(pk)


@task(ignore_result=True)
def async_add_board(board_path, dashboard_id, user):
        prior = 1
        for ds in DashboardPanel.objects.filter(dashboard_id=dashboard_id, user=user):
                ds.priority = prior
                ds.save()
                prior += 1


def save_board(board_path, dashboard_id, user, boardname):
        ds, is_new = DashboardPanel.objects.get_or_create(plank=board_path, dashboard_id=dashboard_id, user=user)
        if is_new:
                ds.zoom_x = 0
                ds.zoom_y = 0
                ds.priority = 1
                ds.boardname = boardname
        ds.save()
        async_add_board(board_path, dashboard_id, user)
        return ds


@task(ignore_result=True)
def async_del_board(board_pk):
        ds = DashboardPanel.objects.get(pk=board_pk)
        user = ds.user
        dashboard_id = ds.dashboard_id
        ds.delete()
        itr = 1
        for ds in DashboardPanel.objects.filter(dashboard_id=dashboard_id, user=user).order_by('priority'):
                ds.priority = itr
                ds.save()
                itr += 1
