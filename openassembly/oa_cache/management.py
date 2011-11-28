from oa_cache.models import ModelCache, UserSaltCache, ListCache, SideEffectCache

###Gets or creates the cache keys in a hierarchical fashion
emptycache, is_new = ModelCache.objects.get_or_create(template="model.html", div_id="#content", content_type="empty_class", main=True)
mcache = ModelCache.objects.get(template="group.html")

us, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache, is_toggle=False, template="oa_group_settings_form.html", div_id="#settings", jquery_cmd="html", load_last=True)

oref, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache, is_toggle=False, template="oa_referral_form.html", div_id="#oa_referral", jquery_cmd="html", load_last=True)

fac, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache, is_toggle=False, template="oa_facilitators_form.html", div_id="#add_facilitators", jquery_cmd="html", load_last=True)

topnav, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache, is_toggle=False, template="topnav.html", div_id="#topnav", jquery_cmd="html", opposite=True)

titlenav, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache, is_toggle=False, template="header_title.html", div_id="#header_title", jquery_cmd="html", opposite=True)

createcontent, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache, is_toggle=False, template="create_content.html", div_id="#create_content", jquery_cmd="html", opposite=True)
