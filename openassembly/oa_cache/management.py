from oa_cache.models import ModelCache, UserSaltCache, ListCache, SideEffectCache

###Gets or creates the cache keys in a hierarchical fashion
"""
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
"""

########PURGE THE NON-BELIEVERS!!!
for i in SideEffectCache.objects.all():
    i.delete()
for i in UserSaltCache.objects.all():
    i.delete()
for i in ListCache.objects.all():
    i.delete()
for i in ModelCache.objects.all():
    i.delete()

####USER PROFILE
usercache, is_new = ModelCache.objects.get_or_create(template="user/user.html",
                div_id="#pages", content_type="user", main=True, jquery_cmd="append")
user_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=usercache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

inboxcache, is_new = ModelCache.objects.get_or_create(template="inbox.html",
                div_id="#pages", content_type="inbox", main=True, jquery_cmd="append")
inbox_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=inboxcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

uploadcache, is_new = ModelCache.objects.get_or_create(template="upload.html",
                div_id="#pages", content_type="upload", main=True, jquery_cmd="append")
upload_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=uploadcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

ppblobformcache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_message_form.html",
                                                    div_id="#pp_message_form", jquery_cmd="html", object_specific=True)


##USER LISTS
shortusercache, is_new = ModelCache.objects.get_or_create(template="user/user_short.html",
            div_id="#panels", content_type="members", jquery_cmd="append")
userlistcache, is_new = ListCache.objects.get_or_create(model_cache=shortusercache.pk,
         template="users", div_id="#panels", content_type="members", default=True)

##USER LISTS
memberlistcache, is_new = ModelCache.objects.get_or_create(template="user/member_short.html",
            div_id="#panels", content_type="users", jquery_cmd="append")
largeuserlistcache, is_new = ListCache.objects.get_or_create(model_cache=memberlistcache.pk,
         template="users", div_id="#panels", content_type="users", default=True)

#GROUPS AND LISTING
mcache, is_new = ModelCache.objects.get_or_create(template="group/group.html",
                div_id="#pages", content_type="group", main=True, jquery_cmd="append")
group_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=mcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

tcache, is_new = ModelCache.objects.get_or_create(template="topic.html",
            div_id="#panels", content_type="groups", jquery_cmd="append")
topiclistcache, is_new = ListCache.objects.get_or_create(model_cache=tcache.pk,
         template="topics", div_id="#panels", content_type="topics", default=True)


####FORMS AND GROUP INTERACTIONS
intercache, is_new = ModelCache.objects.get_or_create(template="interact.html",
                div_id="#pages", content_type="interact", main=True, jquery_cmd="append")
interact_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=intercache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

oref, is_new = UserSaltCache.objects.get_or_create(model_cache=intercache.pk, is_toggle=False,
            template="forms/oa_referral_form.html", div_id="#oa_referral_form", jquery_cmd="html", load_last=True)
fac, is_new = UserSaltCache.objects.get_or_create(model_cache=intercache.pk, is_toggle=False,
        template="forms/oa_facilitators_form.html", div_id="#oa_facilitators_form", jquery_cmd="html", load_last=True)
ppedittopiccache, is_new = UserSaltCache.objects.get_or_create(model_cache=intercache.pk, template="forms/pp_edittopic_form.html",
                                        div_id="#pp_edittopic_form", jquery_cmd="html", redirect=True)

###PROPOSALS
propcache, is_new = ModelCache.objects.get_or_create(template="content/listing.html",
            div_id="#panels", content_type="proposals", jquery_cmd="append")
proplistcache, is_new = ListCache.objects.get_or_create(model_cache=propcache.pk,
         template="issues", div_id="#panels", content_type="proposals", default=True)

detailcache, is_new = ModelCache.objects.get_or_create(template="content/detail.html",
                div_id="#pages", content_type="item", main=True, jquery_cmd="append")
content_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

groupsettingsform, is_new = UserSaltCache.objects.get_or_create(is_toggle=False,
    template="forms/oa_group_settings_form.html", div_id="#oa_group_settings_form", jquery_cmd="html", load_last=True)


comcache, is_new = ModelCache.objects.get_or_create(template="comment.html",
    div_id="#content_children", content_type="item", is_recursive=True, object_specific=True, jquery_cmd="append")
commentslistcache, is_new = ListCache.objects.get_or_create(model_cache=comcache.pk,
        template="comments", div_id="#content_children", content_type="item", default=True)

###VOTING AND SIDEEFFECTS
tempcheckcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailcache.pk,
            template="content/temp_check.html", div_id="#temp_check", jquery_cmd="html", object_specific=True)

####ADMIN
report_abuse_model_cache, is_new = ModelCache.objects.get_or_create(template="report_abuse.html", main=True,
            div_id="#pages", content_type="report_abuse", jquery_cmd="append")
report_abuse_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=report_abuse_model_cache.pk, template="report_abuse.html",
                                                                div_id="#report_abuse", jquery_cmd="html")
pptopictab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=report_abuse_model_cache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")


##FORMS
ppcommentformcache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_comment_form.html",
                        div_id="#pp_comment_form", jquery_cmd="html", load_last=True)
ppreplycache, is_new = UserSaltCache.objects.get_or_create(model_cache=comcache.pk,
    template="forms/pp_reply_form.html", div_id="#pp_reply_form", jquery_cmd="html", is_recursive=True,
    is_toggle=True, object_specific=True, load_last=True)

pptopiccache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_topic_form.html",
                         div_id="#create_group", jquery_cmd="html", redirect=True)

ppreplysdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppreplycache.pk,
        template="comment.html", div_id="#comment_links", jquery_cmd="append", object_specific=True)


pptopiccache, is_new = UserSaltCache.objects.get_or_create(template="create_group.html",
                        div_id="#pages", jquery_cmd="append", redirect=True)
pptopictab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=pptopiccache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")


errorcache, is_new = ModelCache.objects.get_or_create(template="404.html", main=True,
            div_id="#pages", content_type="404", jquery_cmd="append")

errortab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=errorcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

helpcache, is_new = ModelCache.objects.get_or_create(template="natgathelp.html", main=True,
            div_id="#pages", content_type="natgathelp", jquery_cmd="append")

helptab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=helpcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

natgatcache, is_new = ModelCache.objects.get_or_create(template="etc/faq.html", main=True,
            div_id="#pages", content_type="help", jquery_cmd="append")

natgattab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=natgatcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

ppblobformcache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_blob_form.html",
                                                    div_id="#pp_blob_form", jquery_cmd="html", object_specific=True)

ppblobeditformcache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_blobedit_form.html",
                                                    div_id="#pp_blobedit_form", jquery_cmd="html", object_specific=True)

submitcache, is_new = ModelCache.objects.get_or_create(template="submit.html",
                div_id="#pages", content_type="submit", main=True, jquery_cmd="append")
submit_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=submitcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")


pprofilecache, is_new = ModelCache.objects.get_or_create(template="pp_profile_form.html",
                div_id="#pages", content_type="pp_profile_form", main=True, jquery_cmd="append")

pprofileformcache, is_new = UserSaltCache.objects.get_or_create(template="pp_profile_form.html",
                                                    div_id="#pp_profile_form", jquery_cmd="append")
pprofileform_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=pprofilecache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

ppeditcache, is_new = UserSaltCache.objects.get_or_create(model_cache=comcache.pk,
        template="forms/pp_edit_form.html", div_id="#pp_edit_form", jquery_cmd="html",
            is_recursive=True, is_toggle=True, object_specific=True, load_last=True)


####REGISTRATION STUFF
registercache, is_new = ModelCache.objects.get_or_create(template="etc/register.html",
                div_id="#pages", content_type="register", main=True, jquery_cmd="append")
register_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=registercache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

confirmcache, is_new = ModelCache.objects.get_or_create(template="confirm.html",
                div_id="#pages", content_type="confirm", main=True, jquery_cmd="append")
confirmation_tab_cache, is_new = UserSaltCache.objects.get_or_create(model_cache=confirmcache.pk, template="skeleton/tab_template.html",
                         div_id="#tab_ruler", jquery_cmd="append")

#LISTCACHE FOR CHILDREN
questionslistcache, is_new = ListCache.objects.get_or_create(model_cache=mcache.pk,
    template="Question", div_id="#questions", content_type="item", default=False)
nominationsslistcache, is_new = ListCache.objects.get_or_create(model_cache=mcache.pk,
    template="Nomination", div_id="#nominations", content_type="item", default=False)
decisionsslistcache, is_new = ListCache.objects.get_or_create(model_cache=mcache.pk,
    template="Decision", div_id="#decisions", content_type="item", default=False)


###SIDE EFFECT FOR COMMENTS
ppurlsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppcommentformcache.pk,
                        template="comment.html", div_id="#content_children", jquery_cmd="prepend", object_specific=True)
pp_editsdcache, is_new = SideEffectCache.objects.get_or_create(user_salt_cache=ppeditcache.pk,
        template="content/comment_edit.html", div_id="#comment_text", jquery_cmd="html", object_specific=True)




# #FORMS
# pptopiccache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_topic_form.html",
#                         div_id="#content_right", jquery_cmd="html", redirect=True)
# ppcommentformcache, is_new = UserSaltCache.objects.get_or_create(template="forms/pp_comment_form.html",
#                         div_id="#content_right", jquery_cmd="html")


# ##CONTENT AND LISTING
# listcache, is_new = ModelCache.objects.get_or_create(template="listing.html",
#                     div_id="#content_right", content_type="panel_list", jquery_cmd="append")
# issuescache, is_new = ListCache.objects.get_or_create(model_cache=listcache.pk,
#                 template="issues", div_id="#content_right", content_type="panel_list", default=True)

# detailrightcache, is_new = ModelCache.objects.get_or_create(template="content/detail_right.html",
#                     div_id="#content_right", content_type="item", main=True, jquery_cmd="html")
# detailleftcache, is_new = UserSaltCache.objects.get_or_create(model_cache=detailrightcache.pk,
#                 template="content/detail_left.html", div_id="#content_left", jquery_cmd="html")


# ##COMMENTS
# comcache, is_new = ModelCache.objects.get_or_create(template="comment.html",
#         div_id="#content_right", content_type="item", is_recursive=True, jquery_cmd="append")
# commentslistcache, is_new = ListCache.objects.get_or_create(model_cache=comcache.pk,
#         template="comments", div_id="#content_right", content_type="item", default=True)
