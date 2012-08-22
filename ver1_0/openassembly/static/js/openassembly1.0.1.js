

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

function support(add, subscribed, user){
  if(add === true){
      $.post("/add_support/", {subscribed: subscribed, user: user},
        function(data) {
            if(data.FAIL !== true){
              //$('#mygroup').append(data.group);
              history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
              getContent();
            }
       }, "json");
  }
  if(add === false){
      $.post("/remove_support/", {subscribed: subscribed, user: user},
        function(data) {
            if(data.FAIL !== true){
              //$('#mygroup').append(data.group);
              history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
              getContent();
            }
       }, "json");
  }
}

function add_group(topic, user){
$.post("/add_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        //$('#mygroup').append(data.group);
        //history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
        //getContent();
        //$('.thumbnail_list').prepend(data.group);
        js_redirect(data.redirect);
      }
 }, "json");
}

function remove_group(topic, user){
$.post("/remove_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        //$(data.group).remove();
        //history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
        //getContent();
        //$(data.group).remove();
        js_redirect(data.redirect);
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
    var o = {};
    var a = $(e.target).serializeArray();
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
    var form = o;
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
                            history.pushState({load:true, module:'leave'}, '', data2.output[item].html);
                            //remove current tab
                            var curtab = $('#current_tab').html();
                            $('#tabholdertab' + curtab).remove();
                            $('#page' + curtab).remove();
                            sessionStorage.removeItem(curtab);
                            $('#current_tab').html('');
                            $('#overlay').hide();
                            $("html").css("overflow", "auto");
                            getContent();
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
                                var hash = location.href;
                                var dom = $('#domain').html();
                                var tempkey = hash.replace(dom, '');
                                tempkey = tempkey.replace('http:', '');
                                tempkey = tempkey.replace(/\//g,"");
                                $(data2.output[item].div).slideto({'div_offset': -400, 'thadiv': '#page' + tempkey, 'highlight_color':'#d6e3ec'});                        }
                    }
                    //hrefLess();
                }, "json");
            }
          //if(data.POST){}
        }, "json");

  }

function tabQueue() {
    var window_width = $(window).width();
        ruler = $('#tab_ruler');
        ruler_width = ruler.width();
        min_win = window_width - 300;
        num_tabs = $('#the_queue .tab').length;
        tab_iter = $('#tab_queue .tab_iterate');
    
    // check to see if the tabs are being overlapped by the queue
    if (ruler_width > min_win) {
        // move tabs to queue
        var last_tab = $('#tab_ruler .tab').last();
        $('#the_queue').append(last_tab);
    } else if ( (min_win - 162 ) > ruler_width) {
        // move tabs back to taskbar
        var last_tab = $('#the_queue .tab').last();
        $('#tab_ruler').append(last_tab);
    }
    
    if (num_tabs > 0) {
        tab_iter.text(num_tabs);
    } else {
        tab_iter.text('No');
    }
    
}


// remember how many tabs were in queue on doc load
function rememberTabs() {
    var window_width = $(window).width();
        ruler = $('#tab_ruler');
        ruler_width = ruler.width();
        min_win = window_width - 157;
        num_tabs = $('#pages .page').length;
        old_width = $('#tab_width').text();
    
    num_of_times_to_fire = Math.ceil( num_tabs - ( Math.abs(old_width - window_width) / 162 ) );
    for (i=-2; i<=num_of_times_to_fire; i++) {
        tabQueue();
    }
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
                                  history.pushState({load:true, module:'Reload'}, '', data2.output[item].html);
                                  getContent();
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
                                var hash = location.href;
                                var dom = $('#domain').html();
                                var tempkey = hash.replace(dom, '');
                                tempkey = tempkey.replace('http:', '');
                                tempkey = tempkey.replace(/\//g,"");
                                $(data2.output[item].div).slideto({'div_offset': -400, 'thadiv': '#page' + tempkey, 'highlight_color':'#d6e3ec'});
                            }
                        }
                        //hrefLess();
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
    var dom = $('#domain').html();
    d['empty'] = ($('#content').is(':empty'));
    var tempkey = d['hash'].replace(dom, '');
    tempkey = tempkey.replace('http:', '');
    tempkey = tempkey.replace(/\//g,"");
    var ss = sessionStorage.getItem(tempkey);
    var state = history.state;
    if (typeof(state) !== 'undefined'){
      var data = state.data;
      var module = state.module;
    }
    else{
      var data = '';
      var module = '';
    }
    if(ss != 'True' || module == 'Reload'){
      $.get("/load_page/", d,
        function(OAdata) {
           if(OAdata.FAIL !== true){
                  for(var item in OAdata.output){
                      if((module === 'Reload' && OAdata.output[item].div == '#tab_ruler')){

                      }
                      else{
                          if(OAdata.output[item].div == '#pages' && module === 'Reload'){
                              $(OAdata.output[item].div).html(OAdata.output[item].html);
                          }
                          else{
                            if(OAdata.output[item].type == 'prepend'){
                              $(OAdata.output[item].div).prepend(OAdata.output[item].html);
                            }
                            if(OAdata.output[item].type == 'append'){
                                $(OAdata.output[item].div).append(OAdata.output[item].html);
                            }
                            if(OAdata.output[item].type == 'html'){
                                $(OAdata.output[item].div).html(OAdata.output[item].html);
                            }
                            if(OAdata.output[item].div == '#pages' && module !== 'Reload'){
                                toggleMinMax(OAdata.key);
                            }
                          }
                      }
                  }
                //$("#content").append(data.POST);
                
                //location.hash = data.url
            }
            if(OAdata.FAIL === true){
                alert('fail');
                js_redirect('/404.html?');
            }
            sessionStorage.setItem(OAdata.key, 'True');
            //hrefLess();
            rememberTabs();


          //if(OAdata.scroll_to !== null){
          //  $(OAdata.scroll_to).slideto({'slide_duration': "fast", 'highlight': false});
          //}
          //else{
          //  $('html').slideto({'slide_duration': "fast", 'highlight': false});
          //}
       }, "json");

    }
    if (ss === 'True' && module !== 'Reload'){
        toggleMinMax(tempkey);
    }
}


function sort_dashboard(sorted){
  
  $.post("/sort_board/", {sorted: sorted},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //$('#ballot_complete{{plat.pk}}').html(data.complete_perc);
      }
  }, "json");
}

function increase_zoom(obj_pk, dim, path, dash_id, type){
  
  $.post("/increase_zoom/", {object_pk: obj_pk, dimension: dim},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          if(type == 'Chat' || type == 'Stream'){
            refresh_size(path, dash_id);
          }
      }
  }, "json");
}

function decrease_zoom(obj_pk, dim, path, dash_id, type){
  
  $.post("/decrease_zoom/", {object_pk: obj_pk, dimension: dim},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          if(type == 'Chat' || type == 'Stream'){
            refresh_size(path, dash_id);
          }
      }
  }, "json");
}

function resort_dashboard(dash_id, sort_key){
  
  $.post("/resort_board/", {dashboard_id: dash_id, sort_key: sort_key},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //chat window should be resized
          refresh_dashboard(data.plank, data.dash_id);
      }
  }, "json");
}

function refresh_dashboard(path, dash_id, start, end){
  $.post("/add_board/", {path: path, dashboard_id: dash_id, type: 'refresh', boardname: null, start: start, end: end},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //chat window should be resized
          if(data.rendertype == 'chat'){
            $('.iframe' + data.dashpk).width(data.width);
            $('.iframe' + data.dashpk).height(data.height);
          }
          else{
            $('#' + data.dashpk).html(data.html);
            //hrefLess();
            //ui.item.addClass('dragging').removeClass('');
            //ui.item.addClass('dragging').addClass('panel');

          }
          $('#panels').masonry('reload');
      }

  }, "json");

}

function refresh_size(path, dash_id){
  $.post("/add_board/", {path: path, dashboard_id: dash_id, type: 'refresh', boardname: null},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //chat window should be resized
          if(data.rendertype == 'chat'){
            $('#chat_ctrl' + data.dashpk).css('marginTop', data.height + "px");

          }
          else{
            $('#' + data.dashpk).html(data.html);
            $('#' + data.dashpk).removeClass('pwide' + data.dashzoom_x );
            $('#' + data.dashpk).removeClass('pwide' + data.dashzoom_x + 2);
            $('#' + data.dashpk).removeClass('ptall' + data.dashzoom_y );
            $('#' + data.dashpk).removeClass('ptall' + data.dashzoom_y + 2);

            $('#' + data.dashpk).addClass('pwide' + data.dashzoom_x + 1);
            $('#' + data.dashpk).addClass('ptall' + data.dashzoom_y + 1);

          }
          $('#panels').masonry('reload');
          //hrefLess();

      }
  }, "json");

}

function push_dashboard(path, dash_id, boardname){
  $.post("/add_board/", {path: path, dashboard_id: dash_id, type: 'add', boardname: boardname},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          $('#panels').prepend(data.html);
          $('#panels').masonry('reload');
          $('#tutorial').hide();
          $('#youtube').remove();
          //hrefLess();
      }
  }, "json");
}

function delete_dashboard(obj_pk){
  
  $.post("/del_board/", {object_pk: obj_pk},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
        $('#' + obj_pk).remove();
        $('#panels').masonry('reload');
      }
  }, "json");
}


function allowPush(e, url, that) {
    return (!e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey &&
        url != ''  && url.indexOf('#')==-1 && url.indexOf('javascript') == -1 && url.indexOf('http://') == -1 && url.indexOf('https://') == -1 && (typeof that.attr('target') == 'undefined' || that.attr('target') == '') 
        && !that.hasClass('nobbq') && typeof $.data(that.get(0), 'events') == 'undefined' && typeof disablePush == 'undefined')
}

// Panel resizing
// Down
function downzoom(dashpk, path, dash_id, type){
    var p = $('#' + dashpk);
    if (p.hasClass('ptall3')) {
        return false;
    } else if (p.hasClass('ptall2')) {
        p.removeClass('ptall2').addClass('ptall3');
        p.find('icon-chevron-down').closest('li').addClass('disabled');
        increase_zoom(p.attr('id'), 'Y', path, dash_id, type);
        $('#panels').masonry('reload');

    } else {
        p.find('.icon-chevron-up').closest('li').removeClass('disabled');
        p.addClass('ptall2');
        increase_zoom(p.attr('id'), 'Y', path, dash_id, type);
        $('#panels').masonry('reload');
    }
}
// Up
function upzoom(dashpk, path, dash_id, type){
    var p = $('#' + dashpk);
    if (p.hasClass('ptall3')) {
        p.find('.icon-chevron-down').closest('li').removeClass('disabled');
        p.removeClass('ptall3').addClass('ptall2');
        decrease_zoom(p.attr('id'), 'Y', path, dash_id, type);
        $('#panels').masonry('reload');

    } else if (p.hasClass('ptall2')) {
        p.removeClass('ptall2');
        p.find('.icon-chevron-up').closest('li').addClass('disabled');
        decrease_zoom(p.attr('id'), 'Y', path, dash_id, type);
        $('#panels').masonry('reload');

    } else {
        return false;
    }
}
// Right
function rightzoom(dashpk, path, dash_id, type){
    var p = $('#' + dashpk);
    if (p.hasClass('pwide4')) {
        return false;
    } else if (p.hasClass('pwide3')) {
        p.removeClass('pwide3').addClass('pwide4');
        p.find('.icon-chevron-right').closest('li').addClass('disabled');
        increase_zoom(p.attr('id'), 'X', path, dash_id, type);
        $('#panels').masonry('reload');

    } else if (p.hasClass('pwide2')) {
        p.removeClass('pwide2').addClass('pwide3');
        increase_zoom(p.attr('id'), 'X', path, dash_id, type);
        $('#panels').masonry('reload');

    } else {
        p.addClass('pwide2');
        p.find('.icon-chevron-left').closest('li').removeClass('disabled');
        increase_zoom(p.attr('id'), 'X', path, dash_id, type);
        $('#panels').masonry('reload');
    }
}
// Left
function leftzoom(dashpk, path, dash_id, type){
    var p = $('#' + dashpk);
    if (p.hasClass('pwide4')) {
        p.find('.icon-chevron-right').closest('li').removeClass('disabled');
        p.removeClass('pwide4').addClass('pwide3');
        decrease_zoom(p.attr('id'), 'X', path, dash_id, type);
        $('#panels').masonry('reload');

    } else if (p.hasClass('pwide3')) {
        p.removeClass('pwide3').addClass('pwide2');
        decrease_zoom(p.attr('id'), 'X', path, dash_id, type);
        $('#panels').masonry('reload');

    } else if (p.hasClass('pwide2')) {
        p.removeClass('pwide2');
        p.find('icon-chevron-left').closest('li').addClass('disabled');
        decrease_zoom(p.attr('id'), 'X', path, dash_id, type);
        $('#panels').masonry('reload');

    } else {
        return false;
    }
}

function toggleMinMax(t){
    var curtab = $('#current_tab').html();
    var keepif = (curtab === '');
    var is_add = $('#minmax' + t).find('i').hasClass('icon-plus-sign');
    var nempty = $('#pages').find('.current').length === 0;

    if(!nempty && !is_add){
        $('#overlay').hide();
        $("html").css("overflow", "auto");

    }

    if(t != curtab){
        $('#overlay').show();
        //add new page
        $('#page' + t).show();
        $('#tab' + t).addClass('current-icon');
        $('#page' + t).addClass('current');
        $('#minmax' + t).find('i').toggleClass('icon-minus-sign icon-plus-sign');
        $("html").css("overflow", "hidden");
        //set the current div
        $('#current_tab').html(t);
    }
    else{
        $('#current_tab').html('');
    }
    if(!keepif){
        //remove the old page
        $('#page' + curtab).removeClass('current');
        $('#page' + curtab).hide();
        $('#tab' + curtab).removeClass('current-icon');
        $('#minmax' + curtab).find('i').toggleClass('icon-minus-sign icon-plus-sign');
    }
}

// Remove's href from anchors and adds them as data attr (so browser status bars don't cover up OA's taskbar)
function hrefLess() {
    //alert('hefrels');
    $('a').each(function(){
        var t = $(this);
        if(t.attr('id') != 'register'){
            if(typeof t.attr('href') != 'undefined'){
                t.data('href', t.attr('href'));
                t.removeAttr('href');
            }
        }
    });
    //$('a').on('click', function(){
    //   var t = $(this);
    //    if(t.attr('id') != 'register' && t.attr('id') != 'fancybox-close'){
    // //        window.location = $(this).data('href');
    //     }
    // });
}

function minimizeAll(){
    var curtab = $('#current_tab').html();
    if(curtab !== ''){
        if($('#page' + curtab).hasClass('current')){
            $('#page' + curtab).removeClass('current');
            $('#page' + curtab).hide();
        }
        if($('#tab' + curtab).hasClass('current-icon')){
            $('#tab' + curtab).removeClass('current-icon');
        }
        $('#minmax' + curtab).find('i').toggleClass('icon-minus-sign icon-plus-sign');
        $('#overlay').hide();
        $('#current_tab').html('');
        $("html").css("overflow", "auto");

    }
}

function load_patch(obj_pk, patch){
  edit_pk = $('#current_edit' + obj_pk).attr("class");
  edit_num = $('#edit_num' + obj_pk).attr("class");
  $.post("/load_patch/", {obj_pk: obj_pk, edit_num: edit_num, patch: patch},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          $('#description' + obj_pk).fadeOut('fast', function() {
            $('#description' + obj_pk).html(data.text);
            $('#description' + obj_pk).fadeIn();
          });
          $('#current_edit' + obj_pk).html(data.next);
          $('#edits' + obj_pk).html(data.ctrl);

          //hrefLess();
      }
  }, "json");

}