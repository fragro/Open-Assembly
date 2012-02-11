from oa_cache.models import ModelCache, UserSaltCache, ListCache, SideEffectCache

###Gets or creates the cache keys in a hierarchical fashion

#####MODEL CACHES

emptycache, is_new = ModelCache.objects.get_or_create(template="model.html", div_id="#content", content_type="empty_class", main=True)

pcache, is_new = ModelCache.objects.get_or_create(template="platform.html", div_id="#content", content_type="platform", main=True)

mcache, is_new = ModelCache.objects.get_or_create(template="group.html", div_id="#content", content_type="group", main=True)

tcache, is_new = ModelCache.objects.get_or_create(template="topic.html", div_id="#content", content_type="list", jquery_cmd="append")

argcache, is_new = ModelCache.objects.get_or_create(template="argument.html", div_id="#content_children", content_type="arg", main=False, jquery_cmd="append")

comcache, is_new = ModelCache.objects.get_or_create(template="comment.html", div_id="#content_children", content_type="item", is_recursive=True, jquery_cmd="append")

usercache, is_new = ModelCache.objects.get_or_create(template="user_dyn.html", div_id="#content", content_type="user", main=True, jquery_cmd="html")

listcache, is_new = ModelCache.objects.get_or_create(template="listing.html", div_id="#content", content_type="list", jquery_cmd="append")

detailcache, is_new = ModelCache.objects.get_or_create(template="detail_dyn.html", div_id="#content", content_type="item", main=True, jquery_cmd="html")

#####LIST CACHES

questionslistcache, is_new = ListCache.objects.get_or_create(model_cache=mcache.pk, template="Question", div_id="#questions", content_type="item", default=False)
nominationsslistcache, is_new = ListCache.objects.get_or_create(model_cache=mcache.pk, template="Nomination", div_id="#nominations", content_type="item", default=False)
decisionsslistcache, is_new = ListCache.objects.get_or_create(model_cache=mcache.pk, template="Decision", div_id="#decisions", content_type="item", default=False)

topiclistcache, is_new = ListCache.objects.get_or_create(model_cache=tcache.pk, template="topics", div_id="#content", content_type="topics", default=True)

childrenlistcache, is_new = ListCache.objects.get_or_create(model_cache=argcache.pk, template="children", div_id="#content_children", content_type="item", default=False)

yeacache, is_new = ListCache.objects.get_or_create(model_cache=argcache.pk, template="yea", div_id="#content_children", content_type="item", default=False)

naycache, is_new = ListCache.objects.get_or_create(model_cache=argcache.pk, template="nay", div_id="#content_children", content_type="item", default=False)

commentslistcache, is_new = ListCache.objects.get_or_create(model_cache=comcache.pk, template="comments", div_id="#content_children", content_type="item", default=True)

issuescache, is_new = ListCache.objects.get_or_create(model_cache=listcache.pk, template="issues", div_id="#content", content_type="list", default=True)

####USERSALTCACHES

us, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache.pk, is_toggle=False, template="oa_group_settings_form.html", div_id="#settings", jquery_cmd="html", load_last=True)

oref, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache.pk, is_toggle=False, template="oa_referral_form.html", div_id="#oa_referral", jquery_cmd="html", load_last=True)

fac, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache.pk, is_toggle=False, template="oa_facilitators_form.html", div_id="#add_facilitators", jquery_cmd="html", load_last=True)

topnav, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache.pk, is_toggle=False, template="topnav.html", div_id="#topnav", jquery_cmd="html", opposite=True)

titlenav, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache.pk, is_toggle=False, template="header_title.html", div_id="#header_title", jquery_cmd="html", opposite=True)

createcontent, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache.pk, is_toggle=False, template="create_content.html", div_id="#create_content", jquery_cmd="html", opposite=True)

ppurlsource, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="pp_urlsource_form.html", div_id="#pp_urlsource_form", jquery_cmd="html")

sortcache, is_new = UserSaltCache.objects.get_or_create(model_cache=listcache.pk, template="sort.html", div_id="#sort", jquery_cmd="html", load_last=True)

ppargyeacache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="pp_argument_form_yea.html", div_id="#pp_argument_form_yea", jquery_cmd="html", redirect=True)

ppcommentcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="pp_comment_form.html", div_id="#pp_comment_form", jquery_cmd="html")

pptagcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="pp_tag_form.html", div_id="#pp_tag_form", jquery_cmd="html")

ppargnaycache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="pp_argument_form_nay.html", div_id="#pp_argument_form_nay", jquery_cmd="html", redirect=True)

ppblobcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="pp_blob_child.html", div_id="#pp_blob_child", jquery_cmd="html")

emptyusersaltcache, is_new = UserSaltCache.objects.get_or_create(model_cache=listcache.pk, template="empty.html", div_id="#sort", jquery_cmd="html", opposite=True)

ppreplycache, is_new = UserSaltCache.objects.get_or_create(model_cache=comcache.pk, template="pp_reply_form.html", div_id="#pp_reply_form", jquery_cmd="html", is_recursive=True, is_toggle=True, object_specific=True, load_last=True)

#commentsaltcache, is_new = UserSaltCache.objects.get_or_create(model_cache=comcache.pk, template="comment_salt.html", div_id="#comment_links", jquery_cmd="html", is_recursive=True, object_specific=True)

ppeditcache, is_new = UserSaltCache.objects.get_or_create(model_cache=comcache.pk, template="pp_edit_form.html", div_id="#pp_edit_form", jquery_cmd="html",  is_recursive=True, is_toggle=True, object_specific=True, load_last=True)

rangelistcache, is_new = UserSaltCache.objects.get_or_create(model_cache=listcache.pk, template="rangelist.html", div_id="#rangelist", jquery_cmd="append")
rangelist2cache, is_new = UserSaltCache.objects.get_or_create(model_cache=tcache.pk, template="rangelist_topic.html", div_id="#rangelist", jquery_cmd="append")

ppblobformcache, is_new = UserSaltCache.objects.get_or_create(template="pp_blob_form.html", div_id="#pp_blob_form", jquery_cmd="html")

ppblobeditformcache, is_new = UserSaltCache.objects.get_or_create(template="pp_blobedit_form.html", div_id="#pp_blobedit_form", jquery_cmd="html")

ppprofileformcache, is_new = UserSaltCache.objects.get_or_create(template="pp_profile_form.html", div_id="#pp_profile_form", jquery_cmd="html")

oaaddgroupitemcache, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache.pk, template="oa_addgroup_form.html", div_id="#addgroup", jquery_cmd="html")


sortingcache, is_new = UserSaltCache.objects.get_or_create(model_cache=tcache.pk, template="sort_group.html", div_id="#sort", jquery_cmd="html", load_last=True)
sortdetailcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="detail_sort.html", div_id="#sort", jquery_cmd="html", load_last=True)
groupnavcache, is_new = UserSaltCache.objects.get_or_create(model_cache=pcache.pk, template="group_nav.html", div_id="#sort", jquery_cmd="html", load_last=True)

ppmessagescache, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache.pk, template="pp_messages.html", div_id="#pp_messages", jquery_cmd="html", opposite=True)

groupnavcache2, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache.pk, template="group_nav.html", div_id="#sort", jquery_cmd="html", load_last=True)

pptopiccache, is_new = UserSaltCache.objects.get_or_create(template="pp_topic_form.html", div_id="#content", jquery_cmd="html", redirect=True)

ppedittopiccache, is_new = UserSaltCache.objects.get_or_create(template="pp_edittopic_form.html", div_id="#pp_edittopic_form", jquery_cmd="html", redirect=True)

ppdeleteformcache, is_new = UserSaltCache.objects.get_or_create(model_cache=comcache.pk, template="pp_delete_form.html", div_id="#pp_delete_form", jquery_cmd="html", is_recursive=True, is_toggle=True, object_specific=True)

livestreamcache, is_new = UserSaltCache.objects.get_or_create(model_cache=emptycache.pk, template="livestream_small.html", div_id="#livestream_small", jquery_cmd="html", persistent=True)
tempcheckcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="temp_check.html", div_id="#temp_check", jquery_cmd="html")

ppsendmessagecache, is_new = UserSaltCache.objects.get_or_create(template="pp_message_form.html", div_id="#content", jquery_cmd="html")
ppsearchformcache, is_new = UserSaltCache.objects.get_or_create(template="pp_search_form.html", div_id="#id_search", jquery_cmd="html", redirect=True)


###SIDE EFFECT CACHE

ppsearchsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppsearchformcache.pk, template="proposal_header.html", div_id="#content", jquery_cmd="html")

proposalheadercache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppblobcache.pk, template="proposal_header.html", div_id="#proposal_header", jquery_cmd="html", scroll_to=False)

sdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppdeleteformcache.pk, template="comment.html", div_id="#comment", jquery_cmd="html", object_specific=True)

pptopicsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=pptopiccache.pk, template="comment.html", div_id="#comment", jquery_cmd="html")

ppblobchildcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppblobcache.pk, template="listing_child.html", div_id="#children_details", jquery_cmd="prepend")

pptagformsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=pptagcache.pk, template="urlsource.html", div_id="#urlsource", jquery_cmd="html")

ppreplysdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppreplycache.pk, template="comment.html", div_id="#comment_links", jquery_cmd="append", object_specific=True)

pp_editsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppeditcache.pk, template="comment_edit.html", div_id="#comment_text", jquery_cmd="html", object_specific=True)

pp_argsyea_sdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppargyeacache.pk, template="argument.html", div_id="#comment_children", jquery_cmd="prepend")

pp_argsnay_sdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppargnaycache.pk, template="argument.html", div_id="#comment_children", jquery_cmd="prepend")

ppurlsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppurlsource.pk, template="urlsource.html", div_id="#urlsource", jquery_cmd="html")

ppurlsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppcommentcache.pk, template="comment.html", div_id="#content_children", jquery_cmd="prepend")

ppblobchildeffectcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppblobcache.pk, template="pp_blob_child_effect.html", div_id="#pp_blob_child", jquery_cmd="html", scroll_to=False)
