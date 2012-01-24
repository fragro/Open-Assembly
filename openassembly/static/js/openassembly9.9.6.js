function spectrumvote(idk, pos, user_pk, obj_pk, ctype_pk){
$.post("/spectrumvote/", {vote: pos, pk: idk},
  function(data) {
      if(data.FAIL === true){
           $("#registration_simplebox").simplebox();
      }
      if(data.FAIL !== true){
        load_usersaltcache('#temp_check', user_pk, obj_pk, ctype_pk);
        $('#spectrum_vote').html(' - ' + data.votetype);
      }
      }, "json");

}

function add_platform(ctype, object_pk){ 
$.post("/add_platform/", {ctype:ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL === true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
}

function remove_platform(ctype, object_pk){ 
$.post("/remove_platform/", {ctype:ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL === true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
}

function starvote(idk, pos, user_pk, obj_pk, ctype_pk){ 
$.post("/starvote/", {vote: pos, pk: idk},
  function(data) {
      if(data.FAIL === true){     
           $("#registration_simplebox").simplebox();
      }
      if(data.FAIL !== true){
        load_usersaltcache('#temp_check', user_pk, obj_pk, ctype_pk);
      }

    }, "json");
}

function flagvote(idk,user,value,flag_type, div_id, img_id){ 
$.post("/flagvote/", {vote: value, pk: idk, user:user, flag_type:flag_type},
  function(data) {
      if(data.FAIL !== true){
          changeImgSrc(data.imgsrc,img_id);
          changeText(data.count,div_id);
      }
 }, "json");
}

function set_loc_by_ip(city,region,country){ 
$.post("/set_loc_by_ip/", {city:city, region:region, country:country},
  function(data) {
      if(data.FAIL !== true){

      }
 }, "json");
}
function changeText(text,div_id)
{
 elem = document.getElementById(div_id);
 elem.innerHTML = text;
}

function changeImgSrc(text,div_id)
{
 elem = document.getElementById(div_id);
 elem.src = text;
}

function js_redirect(location)
{
    window.location = location;
}

function add_tag(tag, obj_id, c_type, app_type){ 
$.post("/add_tag/", {tag: tag, obj: obj_id, c_type:c_type, app_type:app_type },
  function(data) {
      if(data.FAIL !== true){
          $("#recommendations").fadeOut('fast');
          $("#tags").fadeOut('fast');
          changeText(data.taglist,'recommendations');
          changeText(data.linktaglist,'tags');
          $("#recommendations").fadeIn('fast');
          $("#tags").fadeIn('fast');

      }
 }, "json");
}

function add_platform(ctype, object_pk){ 
$.post("/add_platform/", {ctype: ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL !== true){
      }
 }, "json");
}

function add_group(topic, user){ 
$.post("/add_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        $('#mygroup').append(data.group);
      }
 }, "json");
}

function remove_group(topic, user){ 
$.post("/remove_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        $(data.group).html('');
      }
 }, "json");
}

function del_tag(tag, obj_id, c_type, app_type){ 
$.post("/del_tag/", {tag: tag, obj: obj_id, c_type:c_type, app_type:app_type },
  function(data) {
      if(data.FAIL !== true){
          $("#recommendations").fadeOut('fast');
          $("#tags").fadeOut('fast');
          changeText(data.taglist,'recommendations');
          changeText(data.linktaglist,'tags');
          $("#recommendations").fadeIn('fast');
          $("#tags").fadeIn('fast');

      }
 }, "json");
}

function checkDelete(ctype_id, obj_id)
{
     if($('#nukecheck').is(':checked')){
         $.post("/objectdelete/", {content_type: ctype_id, object_id: obj_id},
              function(data) {
                if(data.FAIL !== true){
                  js_redirect('/p/content_delete');
                }
             }, "json");
     }
}

function ScrollToElement(theElement)
{

  var selectedPosX = 0;
  var selectedPosY = 0;
              
  while(theElement !== null){
    selectedPosX += theElement.offsetLeft;
    selectedPosY += theElement.offsetTop;
    theElement = theElement.offsetParent;
  }

 window.scrollTo(selectedPosX,selectedPosY);

}

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function ranked_vote_confirm(obj_pk, val){
  if(val){
  $.post("/confirm_ranked_vote/", {object_pk: obj_pk},
  function(data) {
      if(data.FAIL !== true){
          $("#confirm_button").fadeOut('fast');
          changeText(data.confirm_button,'confirm_button');
          $("#confirm_button").fadeIn('fast');
      }
 }, "json");
}
else{
  $.post("/del_confirm_ranked_vote/", {object_pk: obj_pk},
  function(data) {
      if(data.FAIL !== true){
          $("#confirm_button").fadeOut('fast');
          changeText(data.confirm_button,'confirm_button');
          $("#confirm_button").fadeIn('fast');
      }
 }, "json");
}
  


}

function addObject(e){
    e.preventDefault();
    var form = $(e.target).serializeObject();
    $.post("/load_page/", {form: form, hash: location.href},
        function(data) {
                for(var item in data.output){
                    if(data.output[item].type == 'prepend'){
                      $(data.output[item].div).prepend(data.output[item].html); 
                    } 
                    if(data.output[item].type == 'append'){
                        $(data.output[item].div).append(data.output[item].html); 
                    } 
                    if(data.output[item].type == 'html'){
                        $(data.output[item].div).html(data.output[item].html); 
                    }
                    if(data.output[item].toggle === true){
                        $(data.output[item].div).slideToggle();
                    }
                    //now we need to gather side-effect data and render all side-effects
                    var se = $(data.output[item].div + '_side_effect').html();
                    $.get("/side_effect/", {key: location.href, side_effect: se, usc_pk: data.output[item].usc_pk, obj_pk: data.output[item].obj_pk},
                      function(data2) {
                          for(var item in data2.output){
                            if(data2.output[item].type == 'redirect'){
                              js_redirect(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'after'){
                                $(data2.output[item].div).after(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'before'){
                                $(data2.output[item].div).before(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'prepend'){
                                $(data2.output[item].div).prepend(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'append'){
                                $(data2.output[item].div).append(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'html'){
                                $(data2.output[item].div).html(data2.output[item].html); 
                            }
                            if(data2.output[item].scroll_to === true){
                                $(data2.output[item].div).slideto({'highlight_color':'#d6e3ec'});
                            }
                        }
                    }, "json");
                }
            //if(data.POST){}  
        }, "json");
  }

function load_usersaltcache(div, user, obj_pk, ctype_pk){
    $.get("/load_usersaltcache/", {div: div, hash: location.href, user: user, obj_pk: obj_pk, ctype_pk: ctype_pk},
        function(data) {
                for(var item in data.output){
                    if(data.output[item].type == 'prepend'){
                      $(data.output[item].div).prepend(data.output[item].html); 
                    } 
                    if(data.output[item].type == 'append'){
                        $(data.output[item].div).append(data.output[item].html); 
                    } 
                    if(data.output[item].type == 'html'){
                        $(data.output[item].div).html(data.output[item].html); 
                    }
                    if(data.output[item].toggle === true){
                        $(data.output[item].div).slideToggle();
                    }
                    //now we need to gather side-effect data and render all side-effects
                    var se = $(data.output[item].div + '_side_effect').html();
                    $.get("/side_effect/", {key: location.href, side_effect: se, usc_pk: data.output[item].usc_pk, obj_pk: data.output[item].obj_pk},
                      function(data2) {
                          for(var item in data2.output){
                            if(data2.output[item].type == 'redirect'){
                              js_redirect(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'after'){
                                $(data2.output[item].div).after(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'before'){
                                $(data2.output[item].div).before(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'prepend'){
                                $(data2.output[item].div).prepend(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'append'){
                                $(data2.output[item].div).append(data2.output[item].html); 
                            } 
                            if(data2.output[item].type == 'html'){
                                $(data2.output[item].div).html(data2.output[item].html); 
                            }
                            if(data2.output[item].scroll_to === true){
                                $(data2.output[item].div).slideto({'highlight_color':'#d6e3ec'});
                            }
                        }
                    }, "json");
                }
            //if(data.POST){}  
        }, "json");
  }

function getContent(){
//            if (currentXhr != null && typeof currentXhr != 'undefined') {
//                currentXhr.abort();
//            }
    d = {};
    d['hash'] = location.href;
    d['empty'] = ($('#content').is(':empty'));
    $.get("/load_page/", d,
      function(OAdata) {
          alert(OAdata.FAIL);
          if(OAdata.empty_content){$('#content').html('');}
          if(OAdata.FAIL !== true){
                for(var item in OAdata.output){
                    if(OAdata.output[item].type == 'prepend'){
                      $(OAdata.output[item].div).prepend(OAdata.output[item].html);
                    }
                    if(OAdata.output[item].type == 'append'){
                        $(OAdata.output[item].div).append(OAdata.output[item].html);
                    }
                    if(OAdata.output[item].type == 'html'){
                        $(OAdata.output[item].div).html(OAdata.output[item].html);
                    }
                }
              //$("#content").append(data.POST);
              
              //location.hash = data.url
          }
          if(OAdata.FAIL === true){
              alert('fail');
              js_redirect('/404.html?');
          }

          if(OAdata.scroll_to !== null){
            $(OAdata.scroll_to).slideto({'slide_duration': "fast", 'highlight': false});
          }
          else{
            $('html').slideto({'slide_duration': "fast", 'highlight': false});
          }

     }, "json");
}

function allowPush(e, url, that) {
    return (!e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey &&
        url != ''  && url.indexOf('#')==-1 && url.indexOf('javascript') == -1 && url.indexOf('http://') == -1 && url.indexOf('https://') == -1 && (typeof that.attr('target') == 'undefined' || that.attr('target') == '') 
        && !that.hasClass('nobbq') && typeof $.data(that.get(0), 'events') == 'undefined' && typeof disablePush == 'undefined')
}